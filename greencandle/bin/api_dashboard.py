#!/usr/bin/env python
#pylint: disable=bare-except,no-member,consider-using-with,too-many-locals,assigning-non-slot,global-statement

"""
Flask module for manipulating API trades and displaying relevent graphs
"""
import re
import os
import json
import subprocess
from collections import defaultdict
from datetime import timedelta
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request, Response, redirect, url_for, session, g
from flask_login import LoginManager, login_required, current_user
import setproctitle
from greencandle.lib.redis_conn import Redis
from greencandle.lib.mysql import Mysql
from greencandle.lib.common import (arg_decorator, divide_chunks, get_be_services, list_to_dict,
                                    perc_diff, get_tv_link, get_trade_link)
from greencandle.lib import config
from greencandle.lib.flask_auth import load_user, login as loginx, logout as logoutx

config.create_config()
APP = Flask(__name__, template_folder="/etc/gcapi", static_url_path='/',
            static_folder='/etc/gcapi')
LOGIN_MANAGER = LoginManager()
LOGIN_MANAGER.init_app(APP)
LOGIN_MANAGER.login_view = "login"
APP.config['SECRET_KEY'] = os.environ['SECRET_KEY'] if 'SECRET_KEY' in os.environ else \
        os.urandom(12).hex()
LOAD_USER = LOGIN_MANAGER.user_loader(load_user)
LOGIN = APP.route("/login", methods=["GET", "POST"])(loginx)
LOGIN = APP.route("/logout", methods=["GET", "POST"])(logoutx)

VALUES = defaultdict(dict)

SCRIPTS = ["write_balance", "get_quote_balance", "repay_debts", "get_risk", "get_trade_status",
           "get_hour_profit", "repay_debts", "balance_graph", "test_close", "close_all"]

def get_pairs(env=config.main.base_env):
    """
    get details from docker_compose, configstore, and router config
    output in reversed JSON format

    Usage: api_dashboard
    """
    docker_compose = open(f"/srv/greencandle/install/docker-compose_{env}.yml", "r")
    pairs_dict = {}
    names = {}
    length = defaultdict(int)
    pattern = "CONFIG_ENV"
    for line in docker_compose:
        if re.search(pattern, line.strip()) and not line.strip().endswith(('prod', 'api', 'cron')):
            env = line.split('=')[1].strip()
            command = f'configstore package get --basedir /srv/greencandle/config {env} pairs'
            result = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            pairs = result.stdout.read().split()
            command = f'configstore package get --basedir /srv/greencandle/config {env} name'
            result = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
            name = result.stdout.read().split()
            pairs_dict[env] = [pair.decode('utf-8') for pair in pairs]
            length[env] += 1
            names[env] = name[0].decode('utf-8')
    for key, val in pairs_dict.items():
        length[key] = len(val)
    return pairs_dict, dict(length), names

@APP.before_request
def before_request():
    """
    Perserve session
    """
    session.permanent = True
    APP.permanent_session_lifetime = timedelta(weeks=1)
    session.modified = True
    g.user = current_user

@APP.route('/healthcheck', methods=["GET"])
@login_required
def healthcheck():
    """
    Docker healthcheck
    Return 200
    """
    return Response(status=200)

@APP.route('/commands', methods=["GET"])
@login_required
def commands():
    """Run commands locally"""
    return render_template('commands.html', scripts=SCRIPTS)

@APP.route('/internal', methods=["GET"])
@login_required
def interal():
    """Load internal page"""
    page = "http://" + request.args.get('page')
    resp = requests.get(page, timeout=20)
    if page.endswith('png'):
        filename = os.path.split(page)[-1]
        return render_template('image.html', filename=filename)
    return render_template('internal.html', page=resp.content.decode())


@APP.route('/iframe', methods=["GET"])
@login_required
def example():
    """Load page in an iframe"""
    page = request.args.get('page')
    return render_template('iframe.html', page=page)

@APP.route('/run', methods=["POST"])
@login_required
def run():
    """
    Run command from web
    """
    command = request.args.get('command')
    if command.strip() in SCRIPTS:
        subprocess.Popen(command)
    return redirect(url_for('commands'))

@APP.route('/charts', methods=["GET"])
@login_required
def charts():
    """Charts for given strategy/config_env"""
    config_env = request.args.get('config_env')
    groups = list(divide_chunks(get_pairs()[0][config_env], 2))

    return render_template('charts.html', groups=groups)

@APP.route("/action", methods=['POST', 'GET'])
@login_required
def action():
    """
    get open/close request
    """

    # get integer value of action
    # keep open the same as we don't know direction
    int_action = {"open": "open",
                  "close": 0,
                  "short": -1,
                  "long": 1,
                  }

    pair = request.args.get('pair')
    strategy = request.args.get('strategy')
    trade_action = int_action[request.args.get('action')]
    close = request.args.get('close')
    take = request.args.get('tp') if 'tp' in request.args else None
    stop = request.args.get('sl') if 'sl' in request.args else None
    send_trade(pair, strategy, trade_action, take=take, stop=stop)
    if close:
        return '<button type="button" onclick="window.close()">Close Tab</button>'
    return redirect(url_for('trade'))

def send_trade(pair, strategy, trade_action, take=None, stop=None):
    """
    Create OPEN/CLOSE post request and send to API router
    """
    payload = {"pair": pair,
               "text": f"Manual {trade_action} action from API",
               "action": trade_action,
               "strategy": strategy,
               "manual": True,
               "tp": take,
               "sl": stop}
    api_token = config.web.api_token
    url = f"http://router:1080/{api_token}"
    try:
        requests.post(url, json=payload, timeout=1)
    except:
        pass

@APP.route('/trade', methods=["GET"])
@login_required
def trade():
    """
    open/close actions for API trades
    """
    pairs, _, names = get_pairs()

    rev_names = {v: k for k, v in names.items()}
    with open('/etc/router_config.json', 'r') as json_file:
        router_config = json.load(json_file)

    env = config.main.base_env
    links_list = get_be_services(env)
    links_dict = list_to_dict(links_list, reverse=True, str_filter='-be-')

    my_dic = defaultdict(set)
    for strat, short_name in router_config.items():
        for item in short_name:
            name = item.split(':')[0]

            if not name in ['alert', 'forward']:
                try:
                    container = links_dict[name]
                except KeyError:
                    continue
            else:
                continue

            try:
                config_env = rev_names[container]
            except KeyError:
                # remove -long/-short from container names
                # this is to support long/short containers
                # with the same name
                container = re.sub(r'-\w+$', '', container)
                config_env = rev_names[container]

            xxx = pairs[config_env]
            my_dic[strat] |= set(xxx)

    return render_template('action.html', my_dic=my_dic)

def get_value(item, pair, name, direction):
    """
    try to get value from global dict if exists
    otherwise return -1
    """
    try:
        return VALUES[item][f"{pair}:{name}:{direction}"]
    except KeyError:
        return -1

@APP.route('/live', methods=['GET', 'POST'])
@login_required
def live():
    """
    route to live data
    """
    files = ['prices']

    if request.method == 'GET':
        return render_template('data.html', files=files)
    if request.method == 'POST':
        req = request.form['submit']
        all_data = results = defaultdict(list)
        dbase = Mysql()
        stream = os.environ['STREAM']
        stream_req = requests.get(stream, timeout=10)
        prices = stream_req.json()

        services = list_to_dict(get_be_services(config.main.base_env),
                                reverse=False, str_filter='-be-')
        raw = dbase.get_open_trades()

        for open_time, interval, pair, name, open_price, direction in raw:
            current_price = prices['recent'][pair]['close']
            perc = perc_diff(open_price, current_price)
            perc = -perc if direction == 'short' else perc
            trade_direction = f"{name}-{direction}" if \
                    not (name.endswith('long') or name.endswith('short')) else name

            short_name = services[trade_direction]
            close_link = get_trade_link(pair, short_name, 'close', 'close_now',
                                  config.web.nginx_port, anchor=True)
            take = get_value('take', pair, name, direction)
            stop = get_value('stop', pair, name, direction)
            drawup = get_value('drawup', pair, name, direction)
            drawdown = get_value('drawdown', pair, name, direction)

            all_data["prices"].append({"pair": get_tv_link(pair, interval, anchor=True),
                                       "interval": interval,
                                       "open_time": open_time,
                                       "name": short_name,
                                       "open_price": '{:g}'.format(float(open_price)),
                                       "current_price": '{:g}'.format(float(current_price)),
                                       "perc": round(perc,4),
                                       "close": close_link,
                                       "tp/sl": f"{take}/{stop}",
                                       "du/dd": f"{round(drawup,2)}/{round(drawdown,2)}" })

        results = all_data[req]
        fieldnames = list(results[0].keys())

        return render_template('data.html', results=results, fieldnames=fieldnames, len=len,
                               files=files, order_column=6)
    return None

@APP.route('/data', methods=['GET', 'POST'])
@login_required
def data():
    """
    route to data spreadsheets
    """
    files = ['middle_200', 'num', 'stoch_flat', 'candle_size', 'avg_candles', 'sum_candles',
             'bb_size', 'all', 'bbperc_diff', 'distance_200', 'stx_diff', 'date']
    if request.method == 'GET':
        return render_template('data.html', files=files)
    if request.method == 'POST':
        req = request.form['submit']
        all_data = results = defaultdict(list)
        redis = Redis(db=3)
        keys = redis.conn.keys()
        for key in keys:
            cur_data = redis.conn.hgetall(key)
            decoded = {k.decode():v.decode() for k,v in cur_data.items()}
            sort_data = dict(sorted(decoded.items(), key=lambda pair: files.index(pair[0])))
            pair, interval = key.decode().split(':')
            current_row = {}
            current_row.update({'pair': pair, 'interval':interval})
            for function, value in sort_data.items():
                current_value = '' if 'None' in value else value
                all_data[function].append({'pair': pair, 'interval': interval,
                                                    function: current_value})
                current_row.update({function:current_value})
            all_data['all'].append(current_row)
        results = all_data[req]
        fieldnames = list(results[0].keys())

        return render_template('data.html', results=results, fieldnames=fieldnames, len=len,
                               files=files, order_column=5)
    return None

@APP.route('/menu', methods=["GET"])
@login_required
def menu():
    """
    Menu of strategies
    """
    length = get_pairs()[1]
    return render_template('menu.html', strats=length)

def get_additional_details():
    """
    Get tp/sl and drawup/drawdown from redis and mysql
    """
    redis=Redis()
    dbase = Mysql()

    trades = dbase.get_open_trades()
    global VALUES
    for item in trades:
        _, interval, pair, name, _, direction = item
        VALUES['drawup'][f"{pair}:{name}:{direction}"] = redis.get_drawup(pair, name=name,
                                                        interval=interval)['perc']
        VALUES['drawdown'][f"{pair}:{name}:{direction}"] = redis.get_drawdown(pair, name=name,
                                                            interval=interval)['perc']
        try:
            VALUES['take'][f"{pair}:{name}:{direction}"] = redis.get_on_entry(pair,
                                                                              'take_profit_perc',
                                                                              name=name,
                                                                              interval=interval)

            VALUES['stop'][f"{pair}:{name}:{direction}"] = redis.get_on_entry(pair,
                                                                              'stop_loss_perc',
                                                                              name=name,
                                                                              interval=interval)
        except KeyError:
            pass

@arg_decorator
def main():
    """API for interacting with trading system"""

    setproctitle.setproctitle("api_dashboard")
    scheduler = BackgroundScheduler() # Create Scheduler
    scheduler.add_job(func=get_additional_details, trigger="interval", seconds=5)
    scheduler.start() # Start Scheduler
    APP.run(debug=False, host='0.0.0.0', port=5000, threaded=True)

if __name__ == '__main__':
    main()
