#pylint: disable=wrong-import-position,import-error,undefined-variable,unused-argument
#pylint: disable=invalid-name,logging-format-interpolation

"""
Push/Pull crypto signals and data to mysql
"""

import os
import sys
import operator
import MySQLdb
import MySQLdb.cursors
import binance

BASE_DIR = os.getcwd().split('greencandle', 1)[0] + 'greencandle'
sys.path.append(BASE_DIR)

from lib.config import get_config
from lib.logger import getLogger

HOST = get_config('database')['host']
USER = get_config('database')['user']
PASSWORD = get_config('database')['password']
DB = get_config('database')['db']
logger = getLogger(__name__)

def get_buy():
    """
    Get list of pairs which have just changed from SELL, to BUY and order by strength, return
    ordered tuple.  We look at pairs which have just switched from SELL to BUY to catch it at the
    beginning of an upward trend.  If the state is already BUY then we have likely missed the train,
    so we pass.
    Args:
          None
    Returns:
          sorted tuple each containing pair, score, current price
    """
    logger.debug("Finding symbols to buy")
    potential_buys = get_changes()
    sorted_buys = sorted(potential_buys.items(), key=operator.itemgetter(1))[::-1]

    return sorted_buys

def get_sell():
    """
    From list of current pair holdings list all which are currently in SELL regardless of score.  We
    are not just looking for pairs that have just switched, incase we miss the trigger
    ordered tuple
    Args:
          None
    Returns:
          None
    """

    current_holdings = get_trades()
    command = """select t1.pair from (select pair, total, max(ctime) AS MaxCreated
from action_totals group by pair) t2 join action_totals t1 on t2.pair = t1.pair
and t2.MaxCreated = t1.ctime and t1.total < 1 and t1.total = t2.total ;"""
    db = MySQLdb.connect(host=HOST,
                         user=USER,
                         passwd=PASSWORD,
                         db=DB)

    cur = db.cursor()
    cur.execute(command)

    all_sell = [item[0] for item in cur.fetchall()]
    db.close()

    current_sell = [item for item in current_holdings if item in all_sell]
    return current_sell

def get_changes():
    """
    Get changes of status from BUY to SELL by running a query that compares current value to
    previous value
    Args:
          None
    Returns:
          dict of values.  Keys: pair, ctime, total, gt
          where gt indicates the strength of the BUY signal
    """
    # FIXME: make select match docstring returns
    command = """
    select
s1.pair as pair,
s1.ctime AS ctime1,
s2.ctime as ctime2,
s1.total AS total1,
s2.total as total2,
((s1.total >= 0) and (s2.total <= 0)) AS gt
from (action_totals s1 left join action_totals s2 on ((s1.pair = s2.pair)))

where (
(s1.total <> s2.total) and
((s1.total > 0) and (s2.total <0)) and
(s1.ctime > (now() - interval 5 minute)) and
(s2.ctime < now() - interval 15 minute));
    """
    return fetch_sql_data(command)

def fetch_sql_data(query):
    """"
    Fetch SQL data for totals and return dict
    Args:
          String SQL select query
    Returns:
          dict of tuples.  where key is pair name containing a tuple of total and current price)
    """

    di = {}
    db = MySQLdb.connect(host=HOST,
                         user=USER,
                         passwd=PASSWORD,
                         db=DB,
                         cursorclass=MySQLdb.cursors.DictCursor)
    prices = binance.prices()
    try:
        with db.cursor() as cursor:
            cursor.execute(query)
            data = cursor.fetchall()
            for record in data:
                di[record['pair']] = record['total1'], prices[record['pair']]

    finally:
        db.close()
    return di

def run_sql_query(query):
    """
    Run a given mysql query (INSERT)
    Args:
          string query
    Returns:
          True/False success
    """


    db = MySQLdb.connect(host=HOST,
                         user=USER,
                         passwd=PASSWORD,
                         db=DB)

    cur = db.cursor()
    try:
        cur.execute(query)
    except NameError:
        logger.critical("One or more expected variables not passed to DB")

    db.commit()
    db.close()

def clean_stale():
    """
    Delete stale records from actions and action_totals db tables - any records older than 30
    minutes
    Args:
          None
    Returns:
          None
    """

    logger.debug("Cleaning stale data")
    command1 = "delete from action_totals where ctime < NOW() - INTERVAL 30 MINUTE;"
    command2 = "delete from actions where ctime < NOW() - INTERVAL 30 MINUTE;"
    run_sql_query(command1)
    run_sql_query(command2)

def insert_trade(pair, date, price, investment, total):
    """
    Insert new trade into DB
    Args:
          pair: traiding pair
          price: current price of pair
          investment: amount invested in gbp
          total:
    Returns:
          None
    """

    logger.info("Buying {0}".format(pair))
    command = """insert into trades (pair, buy_time, buy_price, investment, total) VALUES ("{0}",
    "{1}", "{2}", "{3}", "{4}");""".format(pair, date, float(price), investment, total)
    run_sql_query(command)

def get_trade_value(pair):
    """
    Return the value of an open trade for a given trading pair
    """

    command = """ select buy_price from trades where sell_price is NULL and pair = "{0}"
    """.format(pair)
    db = MySQLdb.connect(host=HOST,
                         user=USER,
                         passwd=PASSWORD,
                         db=DB)

    cur = db.cursor()
    cur.execute(command)

    row = [item[0] for item in cur.fetchall()]
    db.close()
    return row


def get_trades():
    """
    Get a list of current open trades.  This is identified by a db record
    which has a buy price, but no sell price - ie. we haven't sold it yet

    Args:
    Returns:
          a single list of pairs that we currently hold
    """

    command = """ select pair from trades where sell_price is NULL """
    db = MySQLdb.connect(host=HOST,
                         user=USER,
                         passwd=PASSWORD,
                         db=DB)

    cur = db.cursor()
    cur.execute(command)

    row = [item[0] for item in cur.fetchall()]
    db.close()
    return row

def update_trades(pair, sell_time, sell_price):
    logger.info("Selling, {0}".format(pair))
    command = """update trades set sell_price={0},sell_time="{1}" where sell_price is NULL and
    pair="{2}" """.format(float(sell_price), sell_time, pair)
    run_sql_query(command)

def insert_data(**kwargs):
    """
    Insert Data into DB
    Args:
          symbol
          event
          direction
          data
          difference
          resistance
          support
          buy
          sell
          market
          balance
    Returns:
          None
    """

    globals().update(kwargs)
    command = """INSERT INTO data (symbol, event, direction, data, difference, resistance, support,
    buy, sell, market, balance)
    VALUES ("{0}","{1}","{2}","{3}","{4}","{5}","{6}","{7}","{8}","{9}","{10}");""".format(
        symbol, event, direction, data, difference, resistance, support, buy, sell, market, balance)
    run_sql_query(command)

def insert_balance(d):
    """
    Insert balance in GBP/BTC/USD into balance table for coinbase & binance
    Args:
          dict of balances
    Returns:
          None
    """


    for exchange, values in d.items():
        for coin, data in values.items():
            try:
                command = """insert into balance (gbp, btc, usd, count, coin, exchange_id) values
                ("{0}", "{1}", "{2}", "{3}", "{4}", (select id from exchange where
                name="{5}"))""".format(data['GBP'], data['BTC'], data['USD'], data['count'], coin,
                                       exchange)
            except KeyError:
                logger.critical(" ".join(["XXX", coin, exchange, "KEYERROR"]))
                continue
            except IndexError:
                logger.info(exchange)
                raise

            try:
                run_sql_query(command)
            except NameError:
                logger.info("One or more expected variables not passed to insert into DB")

def insert_action_totals():
    """
    Get recent coin actions from actions table, sum totals and insert into action_totals table
    Args:
          None
    Returns:
          None
    """

    logger.debug("Inserting Totals")
    command = """ INSERT INTO action_totals (pair, total) select pair, SUM(action) as total from
    recent_actions group by pair order by total;"""
    run_sql_query(command)

def insert_actions(**kwargs):
    """
    Insert actions into actions table
    Args:
          pair (string pairname)
          indicator (eg. RSI, Supertrend)
          value: value of indicator/oscilator
          action: 0/1/-1 for HOLD, BUY,SELL (used to sum totals later)
    Returns:
          None
    """

    globals().update(kwargs)

    command = """INSERT INTO actions (pair, indicator, value, action)
                 VALUES ("{0}","{1}","{2}","{3}");""".format(pair, indicator, value, action)

    run_sql_query(command)
