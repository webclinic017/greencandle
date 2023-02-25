#pylint: disable=no-member,wrong-import-order,logging-not-lazy,too-many-locals
"""
Test Buy/Sell orders
"""

from collections import defaultdict
import time
import datetime
import re
from str2bool import str2bool
from pathlib import Path
from greencandle.lib.auth import binance_auth
from greencandle.lib.logger import get_logger, exception_catcher
from greencandle.lib.mysql import Mysql
from greencandle.lib.redis_conn import Redis
from greencandle.lib.binance_accounts import get_binance_spot, base2quote, quote2base
from greencandle.lib.balance_common import get_base, get_quote, get_step_precision
from greencandle.lib.common import perc_diff, add_perc, sub_perc, AttributeDict, QUOTES
from greencandle.lib.alerts import send_gmail_alert, send_slack_trade, send_slack_message

GET_EXCEPTIONS = exception_catcher((Exception))

class InvalidTradeError(Exception):
    """
    Custom Exception for invalid trade type of trade direction
    """

class Trade():
    """Buy & Sell class"""

    def __init__(self, interval=None, test_data=False, test_trade=False, config=None):
        self.logger = get_logger(__name__)
        self.test_data = test_data
        self.test_trade = test_trade
        self.config = config
        self.prod = str2bool(self.config.main.production)
        self.client = binance_auth()
        self.interval = interval

    @staticmethod
    def is_float(element: any) -> bool:
        """
        check if variable is a float
        return True|False
        """
        # If you expect None to be passed:
        if element is None:
            return False
        try:
            float(element)
            return True
        except ValueError:
            return False

    def is_in_drain(self):
        """
        Check if current scope is in drain given date range, and current time
        Drain time is set in config (drain/drain_range)
        or by the existance of /var/local/{env}_drain file
        """
        currentime = datetime.datetime.now()
        time_str = currentime.strftime('%H:%M')
        raw_range = self.config.main.drain_range.strip()
        start, end = re.findall(r"\d\d:\d\d\s?-\s?\d\d:\d\d", raw_range)[0].split('-')
        time_range = (start.strip(), end.strip())
        drain = str2bool(self.config.main.drain)
        manual_drain = Path('/var/local/{}_drain'.format(self.config.main.base_env)).is_file()
        if time_range[1] < time_range[0]:
            return time_str >= time_range[0] or time_str <= time_range[1]
        return (time_range[0] <= time_str <= time_range[1]) if drain else manual_drain

    def __send_redis_trade(self, **kwargs):
        """
        Send trade event to redis
        """
        valid_keys = ["pair", "open_time", "current_time", "price", "interval", "event"]
        kwargs = AttributeDict(kwargs)
        for key in valid_keys:
            if key not in valid_keys:
                raise KeyError("Missing param %s" % key)

        self.logger.debug('Strategy - Adding to redis')
        redis = Redis()
        if 'api' in self.config.main.name or 'data' in self.config.main.base_env:
            mepoch = int(time.mktime(time.strptime(kwargs.current_time,
                                                   '%Y-%m-%d %H:%M:%S'))) * 1000 + 999
        else:
            mepoch = redis.get_items(kwargs.pair, kwargs.interval)[-1]

        data = {"event":{"result": kwargs.event,
                         "current_price": format(float(kwargs.price), ".20f"),
                         "date": mepoch,
                        }}

        redis.append_data(kwargs.pair, kwargs.interval, data)
        del redis

    def check_pairs(self, items_list):
        """
        Check we can trade which each of given trading pairs
        Return filtered list
        """
        dbase = Mysql(test=self.test_data, interval=self.interval)
        current_trades = dbase.get_trades()
        avail_slots = int(self.config.main.max_trades) - len(current_trades)
        self.logger.info("%s open slots available" % avail_slots)
        table = dbase.fetch_sql_data('show tables like "tmp_pairs"', header=False)
        tmp_pairs = dbase.fetch_sql_data('select pair from tmp_pairs', header=False) \
                if table else []
        db_pairs = [x[0] for x in tmp_pairs] if tmp_pairs else {}
        final_list = []
        manual = "any" in self.config.main.name
        good_pairs = str2bool(self.config.main.good_pairs)

        for item in items_list:
            if not self.test_trade:
                account = 'margin' if 'margin' in self.config.main.trade_type else 'binance'
                totals = self.get_total_amount_to_use(dbase, item[0], account=account)
                if sum(totals.values()) == 0:
                    self.logger.warning("Insufficient funds available for %s %s, skipping..."
                                        % (self.config.main.trade_direction, item[0]))
                    continue


            if current_trades and [trade for trade in current_trades if item[0] in trade]:
                self.logger.warning("We already have a trade of %s %s, skipping..." % (
                    self.config.main.trade_direction, item[0]))
            elif not manual and (item[0] not in self.config.main.pairs and not self.test_data):
                self.logger.error("Pair %s not in main_pairs, skipping..." % item[0])
            elif not manual and good_pairs and db_pairs and (item[0] not in db_pairs
                                                             and not self.test_data):
                self.logger.warning("Pair %s not in db_pairs, skipping..." % item[0])
                send_slack_message("trades", "Pair %s not in db_pairs, skipping..." % item[0])
            elif self.is_in_drain() and not self.test_data:
                self.logger.warning("strategy is in drain for pair %s, skipping..." % item[0])
                send_slack_message("trades", "strategy is in drain, skipping %s" % item[0])
                return []
            elif self.is_float(item[4]) and \
                    ((float(item[4]) > 0 and self.config.main.trade_direction == "short") or \
                    (float(item[4]) < 0 and self.config.main.trade_direction == "long")):
                self.logger.info("Wrong trade direction %s" % self.config.main.trade_direction)
            elif avail_slots <= 0:
                pairs_str = ', '.join((x[0] for x in items_list))
                self.logger.warning("Too many trades for %s, skipping:%s"
                                    % (self.config.main.trade_direction, pairs_str))
                send_slack_message("alerts", "Too many trades for {}, skipping {}"
                                   .format(self.config.main.trade_direction, pairs_str))
            else:
                final_list.append(item)
                avail_slots -= 1
        return final_list

    @GET_EXCEPTIONS
    def open_trade(self, items_list):
        """
        Main open trade method
        Will choose between spot/margin and long/short
        """

        items_list = self.check_pairs(items_list)
        if not items_list:
            self.logger.warning("No items to open trade with")
            return False

        if self.config.main.trade_type == "spot":
            if self.config.main.trade_direction == "long":
                self.__open_spot_long(items_list)
            else:
                raise InvalidTradeError("Invalid trade direction for spot")

        elif self.config.main.trade_type == "margin":
            if self.config.main.trade_direction == "long":
                self.__open_margin_long(items_list)
            elif self.config.main.trade_direction == "short":
                self.__open_margin_short(items_list)
            else:
                raise InvalidTradeError("Invalid trade direction")

        else:
            raise InvalidTradeError("Invalid trade type")
        return True

    @GET_EXCEPTIONS
    def close_trade(self, items_list, drawdowns=None, drawups=None, update_db=True):
        """
        Main close trade method
        Will choose between spot/margin and long/short
        """
        additional_trades = []
        if not items_list:
            self.logger.warning("No items to close trade with")
            return False

        for item in items_list:

            # Number of trades within scope
            dbase = Mysql(test=self.test_data, interval=self.interval)
            count = dbase.fetch_sql_data("select count(*) from trades where close_price "
                                         "is NULL and pair like '%{0}' and name='{1}' "
                                         "and direction='{2}'"
                                         .format(item[0], self.config.main.name,
                                                 self.config.main.trade_direction),
                                         header=False)[0][0]

            while count -1 > 0:
                additional_trades.append(item)
                count -= 1

        items_list += additional_trades

        if self.config.main.trade_type == "spot":
            if self.config.main.trade_direction == "long":
                result = self.__close_spot_long(items_list, drawdowns=drawdowns, drawups=drawups,
                                                update_db=update_db)
            else:
                raise InvalidTradeError("Invalid trade direction for spot")

        elif self.config.main.trade_type == "margin":
            if self.config.main.trade_direction == "long":
                result = self.__close_margin_long(items_list, drawdowns=drawdowns, drawups=drawups)
            elif self.config.main.trade_direction == "short":
                result = self.__close_margin_short(items_list, drawdowns=drawdowns, drawups=drawups)
            else:
                raise InvalidTradeError("Invalid trade direction")

        else:
            raise InvalidTradeError("Invalid trade type")

        return result

    def get_borrowed(self, pair, symbol):
        """
        get amount borrowed from exchange for both cross and isolated modes
        for a particular pair/direction
        """

        if not str2bool(self.config.main.isolated):
            # if we are attempting a cross trade
            details = self.client.get_cross_margin_details()
            for item in details['userAssets']:
                borrowed = float(item['borrowed'])
                asset = item['asset']
                if asset == symbol:
                    return borrowed if borrowed else 0

        elif str2bool(self.config.main.isolated):
            # if we are attempting an isolated trade
            details = self.client.get_isolated_margin_details(pair)
            if details['assets'][0]['quoteAsset']['asset'] == symbol:
                return float(details['assets'][0]['quoteAsset']['borrowed'])
            if details['assets'][0]['baseAsset']['asset'] == symbol:
                return float(details['assets'][0]['baseAsset']['borrowed'])
        return 0

    def get_balance_to_use(self, dbase, account=None, pair=None):
        """
        Choose between spot/cross/isolated/test balances
        Retrive dict and return appropriate value
        Only return 99% of the value
        Returns: float in base if short, or quote if long
        """
        symbol = get_quote(pair) if self.config.main.trade_direction == 'long' else get_base(pair)
        test_balances = self.get_test_balance(dbase, account=account)[account]
        final = 0
        if self.test_data or self.test_trade:
            if self.config.main.trade_direction == 'short' and symbol not in test_balances:
                usd = test_balances['USDT']['count']
                final = quote2base(usd, symbol +'USDT')
            else:
                final = test_balances[symbol]['count']

        elif account == 'binance':
            try:
                final = float(get_binance_spot()[account][symbol]['count'])
            except KeyError:
                pass

        elif account == 'margin' and str2bool(self.config.main.isolated):
            try:
                final = float(self.client.isolated_free()[pair][symbol])
            except KeyError:
                pass

        elif account == 'margin' and not str2bool(self.config.main.isolated):
            try:
                final = float(self.client.cross_free()[symbol]['net'])
            except KeyError:
                pass

        # Use 99% of amount determined by divisor
        return_symbol = sub_perc(1, final / float(self.config.main.divisor)) if final else 0
        return_usd = return_symbol if 'USD' in symbol else base2quote(return_symbol, symbol+'USDT')
        return_dict = {"symbol": return_symbol,
                       "symbol_name": symbol,
                       "usd": return_usd}
        return return_dict

    def get_amount_to_borrow(self, pair, dbase):
        """
        Get amount to borrow based on pair, and trade direction
        divide by divisor and return in the symbol we need to borrow
        Only return 99% of the value
        Returns: float in base if short, or quote if long
        """
        return_dict = {}
        orig_base = get_base(pair)
        orig_quote = get_quote(pair)
        orig_direction = self.config.main.trade_direction

        # get current borrowed
        mode = "isolated" if str2bool(self.config.main.isolated) else "cross"
        rows = dbase.get_current_borrowed(pair if mode == 'isolated' else '', mode)
        borrowed_usd = 0
        # go through open trades
        for (current_pair, amt, direction) in list(rows):
            base = get_base(current_pair)
            quote = get_quote(current_pair)
            if direction == "long":
                borrowed_usd += float(amt) if 'USD' in quote else base2quote(amt, quote+"USDT")
            elif direction == "short":
                borrowed_usd += float(amt) if 'USD' in base else base2quote(amt, base+"USDT")
            # get aggregated total borrowed in USD

        # get (addiontal) amount we can borrow
        if str2bool(self.config.main.isolated):
            asset = orig_quote if orig_direction == 'long' else orig_base
            max_borrow = self.client.get_max_borrow(asset=asset, isolated_pair=pair)
            max_borrow_usd = max_borrow if 'USD' in asset else base2quote(max_borrow, asset+'USDT')
        else:
            # cross always returns USD
            max_borrow_usd = self.client.get_max_borrow()
        # sum of total borrowed and total borrowable
        total = (float(borrowed_usd) + float(max_borrow_usd))

        # divide total by divisor
        # convert to quote asset if not USDT

        # long
        if self.config.main.trade_direction == "long":
            if "USD" in orig_quote:
                value = sub_perc(1, total / float(self.config.main.divisor))
                return_dict['usd'] = value
                return_dict['symbol'] = value
            else:
                final_symbol = sub_perc(1, quote2base(total, orig_quote+"USDT") /
                                        float(self.config.main.divisor))
                final_usd = sub_perc(1, total / float(self.config.main.divisor))

                usd_value = sub_perc(1, total / float(self.config.main.divisor))
                value = quote2base(usd_value, orig_quote+'USDT')
                return_dict['usd'] = final_usd
                return_dict['symbol'] = final_symbol

        # convert to base asset if we are short
        # short
        else:  # amt in base
            usd_value = sub_perc(1, total/float(self.config.main.divisor))
            value = quote2base(usd_value, orig_base+'USDT')
            final_symbol = sub_perc(1, quote2base(total, orig_base+'USDT') /
                                    float(self.config.main.divisor))
            final_usd = sub_perc(1, total / float(self.config.main.divisor))
            return_dict['usd'] = final_usd
            return_dict['symbol'] = final_symbol
            return return_dict

        # Use 99% of amount determined by divisor
        # and check if we have exceeded max_borrable amount
        if (orig_quote == 'USDT' and return_dict['usd'] > max_borrow_usd and
                self.config.main.trade_direction == "long"):
            value = sub_perc(10, max_borrow_usd)
            return_dict['usd'] = value
            return_dict['symbol'] = value
            return return_dict

        if (orig_quote != 'USDT' and
                base2quote(return_dict['symbol'], orig_quote+'USDT') > max_borrow_usd and
                self.config.main.trade_direction == "long"):
            usd_value = sub_perc(10, max_borrow_usd)
            base_value = quote2base(usd_value, orig_quote+'USDT')
            return_dict['usd'] = usd_value
            return_dict['symbol'] = base_value
            return return_dict

        return return_dict

    def get_total_amount_to_use(self, dbase, pair=None, account=None):
        """ Get total amount to use as sum of balance_to_use and loan_to_use """


        max_from_db = dbase.get_var_value('max_trade_usd')
        total_max = int(max_from_db) if max_from_db else int(self.config.main.max_trade_usd)
        balance_to_use = self.get_balance_to_use(dbase, account, pair)
        # set default loan to use as 0, may be overwritten if non-spot and not enough balance to
        # cover max, where loan is available
        loan_to_use = {'symbol': 0, 'usd': 0, 'symbol_name': balance_to_use['symbol_name']}
        if balance_to_use['usd'] > total_max:
            balance_to_use['usd'] = total_max
            if balance_to_use['symbol_name'] == 'USDT':
                balance_to_use['symbol'] = balance_to_use['usd']
            else:
                balance_to_use['symbol'] = quote2base(balance_to_use['usd'],
                                                      balance_to_use['symbol_name']+'USDT')
                loan_to_use = {'symbol':0, 'usd':0, 'symbol_name': balance_to_use['symbol_name']}
        else:

            loan_to_use = self.get_amount_to_borrow(pair, dbase) if \
                    self.config.main.trade_type != 'spot' else {'usd': 0,
                                                                'symbol': 0,
                                                                'symbol_name':
                                                                balance_to_use['symbol_name']}
            total_remaining = total_max - balance_to_use['usd']
            if loan_to_use['usd'] > total_remaining:
                loan_to_use['usd'] = total_remaining
                loan_to_use['symbol'] = total_remaining if 'USD' in \
                        balance_to_use['symbol_name'] else \
                        quote2base(total_remaining, balance_to_use['symbol_name']+'USDT')


        return_dict = {"balance_amt": balance_to_use['symbol'],
                       "loan_amt": loan_to_use['symbol']
                       }

        return return_dict

    def __open_margin_long(self, long_list):
        """
        Get item details and attempt to trade according to config
        Returns True|False
        """
        self.logger.info("We have %s potential items to long" % len(long_list))

        dbase = Mysql(test=self.test_data, interval=self.interval)

        for pair, current_time, current_price, event, _ in long_list:
            pair = pair.strip()
            total_amt_to_use = self.get_total_amount_to_use(dbase, account='margin', pair=pair)
            amount_to_borrow = total_amt_to_use['loan_amt']
            current_quote_bal = total_amt_to_use['balance_amt']

            quote = get_quote(pair)

            borrowed_usd = amount_to_borrow if quote == 'USDT' else \
                    base2quote(amount_to_borrow, quote + 'USDT')
            # amt in base
            quote_to_use = current_quote_bal + amount_to_borrow
            base_to_use = quote2base(quote_to_use, pair)


            self.logger.info("Opening margin long %s of %s with %s %s at %s"
                             % (base_to_use, pair, current_quote_bal+amount_to_borrow,
                                quote, current_price))
            if self.prod:

                if float(amount_to_borrow) <= 0:
                    self.logger.critical("Borrow amount is zero for pair open long %s.  Continuing"
                                         % pair)
                    amt_str = get_step_precision(pair, quote2base(current_quote_bal, pair))
                else:  # amount to borrow
                    self.logger.info("Will attempt to borrow %s of %s for long. Balance: %s"
                                     % (amount_to_borrow, quote, current_quote_bal))

                    amt_str = get_step_precision(pair, base_to_use)
                    borrow_res = self.client.margin_borrow(
                        symbol=pair, quantity=amount_to_borrow,
                        isolated=str2bool(self.config.main.isolated),
                        asset=quote)
                    if "msg" in borrow_res:
                        self.logger.error("Borrow error-open long %s: %s while trying to borrow %s %s"
                                          % (pair, borrow_res, amount_to_borrow, quote))
                        return False

                    self.logger.info(borrow_res)

                trade_result = self.client.margin_order(symbol=pair, side=self.client.buy,
                                                        quantity=amt_str,
                                                        order_type=self.client.market,
                                                        isolated=str2bool(
                                                            self.config.main.isolated))
                self.logger.info("%s open margin long result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Trade error-open %s %s: %s" %
                                      (self.config.main.trade_direction, pair, str(trade_result)))
                    self.logger.error("Vars: base quantity:%s, quote_quantity: %s quote bal:%s, "
                                      "quote_borrowed: %s"
                                      % (amt_str, quote_to_use, current_quote_bal,
                                         amount_to_borrow))
                    return False

                # override values from exchange if in prod
                fill_price, amt_str, quote_to_use, order_id = \
                        self.__get_result_details(current_price, trade_result)

            else: # not prod
                amt_str = base_to_use
                order_id = 0
                fill_price = current_price
                trade_result = {}

            commission_usd = self.__get_commission(trade_result)

            if self.test_data or self.test_trade or \
                    (not self.test_trade and 'transactTime' in trade_result):

                try:
                    amt_str = sub_perc(dbase.get_complete_commission()/2, amt_str)
                except (KeyError, TypeError):  # Empty dict, or no commission for base
                    pass


                dbase.insert_trade(pair=pair, price=fill_price, date=current_time,
                                   quote_amount=quote_to_use, base_amount=amt_str,
                                   borrowed=amount_to_borrow, borrowed_usd=borrowed_usd,
                                   divisor=self.config.main.divisor,
                                   direction=self.config.main.trade_direction,
                                   symbol_name=quote, commission=str(commission_usd),
                                   order_id=order_id)

                self.__send_notifications(pair=pair, open_time=current_time,
                                          fill_price=fill_price, interval=self.interval,
                                          event=event, action='OPEN', usd_profit='N/A',
                                          quote=quote_to_use, close_time='N/A')

        del dbase
        return True

    @staticmethod
    @GET_EXCEPTIONS
    def get_test_balance(dbase, account=None):
        """
        Get and return test balance dict in the same format as binance
        """
        balance = defaultdict(lambda: defaultdict(defaultdict))

        balance[account]['BTC']['count'] = 0.47
        balance[account]['ETH']['count'] = 8.92
        balance[account]['USDT']['count'] = 10000
        balance[account]['USDC']['count'] = 10000
        balance[account]['GBP']['count'] = 10000
        balance[account]['BNB']['count'] = 46.06
        for quote in QUOTES:
            last_value = dbase.fetch_sql_data("select quote_in from trades "
                                              "where pair like '%{0}'"
                                              "order by open_time desc limit 1"
                                              .format(quote), header=False)
            last_value = float(last_value[0][0]) if last_value else 0
            balance[account][quote]['count'] = max(last_value, balance[account][quote]['count'])
        return balance

    @GET_EXCEPTIONS
    def __open_spot_long(self, buy_list):
        """
        Get item details and attempt to trade according to config
        Returns True|False
        """
        self.logger.info("We have %s potential items to open spot long" % len(buy_list))

        dbase = Mysql(test=self.test_data, interval=self.interval)

        for pair, current_time, current_price, event, _ in buy_list:
            quote_amount = self.get_total_amount_to_use(dbase, account='binance',
                                                        pair=pair)['balance_amt']
            quote = get_quote(pair)

            if quote_amount <= 0:
                self.logger.critical("Unable to get balance %s for quote %s while trading %s "
                                     "spot long" % (quote_amount, quote, pair))
                return False

            amount = quote2base(quote_amount, pair)

            self.logger.info("Opening spot long %s of %s with %s %s"
                             % (amount, pair, quote_amount, quote))
            self.logger.debug("amount to buy: %s, current_price: %s, amount:%s"
                              % (quote_amount, current_price, amount))
            if self.prod and not self.test_data:
                amt_str = get_step_precision(pair, amount)

                trade_result = self.client.spot_order(symbol=pair, side=self.client.buy,
                                                      quantity=amt_str,
                                                      order_type=self.client.market,
                                                      test=self.test_trade)

                self.logger.info("%s open spot long result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Trade error-open %s: %s" % (pair, str(trade_result)))
                    self.logger.error("Vars: quantity:%s, bal:%s" % (amt_str, quote_amount))
                    return False

                # override values from exchange if in prod
                fill_price, amount, quote_amount, order_id = \
                        self.__get_result_details(current_price, trade_result)

            else:
                trade_result = True
                order_id = 0
                fill_price = current_price
                trade_result = {}

            commission_usd = self.__get_commission(trade_result)

            if self.test_data or self.test_trade or \
                    (not self.test_trade and 'transactTime' in trade_result):
                # only insert into db, if:
                # 1. we are using test_data
                # 2. we performed a test trade which was successful - (empty dict)
                # 3. we proformed a real trade which was successful - (transactTime in dict)
                amt_str = amount

                try:
                    amt_str = sub_perc(dbase.get_complete_commission()/2, amt_str)
                except (KeyError, TypeError):  # Empty dict, or no commission for base
                    pass

                db_result = dbase.insert_trade(pair=pair, price=fill_price, date=current_time,
                                               quote_amount=quote_amount, base_amount=amount,
                                               direction=self.config.main.trade_direction,
                                               symbol_name=quote, commission=str(commission_usd),
                                               order_id=order_id)
                if db_result:
                    self.__send_notifications(pair=pair, open_time=current_time,
                                              fill_price=fill_price, interval=self.interval,
                                              event=event, action='OPEN', usd_profit='N/A',
                                              quote=quote_amount, close_time='N/A')

        del dbase
        return True

    def __send_notifications(self, perc=None, **kwargs):
        """
        Pass given data to trade notification functions
        """
        valid_keys = ["pair", "fill_price", "event", "action", "usd_profit",
                      "quote", "open_time", "close_time"]

        kwargs = AttributeDict(kwargs)
        for key in valid_keys:
            if key not in valid_keys:
                raise KeyError("Missing param %s" % key)

        current_time = kwargs.close_time if kwargs.action == 'CLOSE' else kwargs.open_time
        self.__send_redis_trade(pair=kwargs.pair, current_time=current_time,
                                price=kwargs.fill_price, interval=self.interval,
                                event=kwargs.action, usd_profit=kwargs.usd_profit)

        send_gmail_alert(kwargs.action, kwargs.pair, '%.15f' % float(kwargs.fill_price))
        usd_quote = kwargs.quote if 'USD' in kwargs.pair else \
                base2quote(kwargs.quote, get_quote(kwargs.pair)+'USDT')
        send_slack_trade(channel='trades', event=kwargs.event, perc=perc,
                         pair=kwargs.pair, action=kwargs.action, price=kwargs.fill_price,
                         usd_profit=kwargs.usd_profit, quote=kwargs.quote, usd_quote=usd_quote,
                         open_time=kwargs.open_time, close_time=kwargs.close_time)

    def __get_result_details(self, current_price, trade_result):
        """
        Extract price, base/quote amt and order id from exchange transaction dict
        Returns:
        Tupple: price, base_amt, quote_amt, order_id
        """
        prices = []
        if 'transactTime' in trade_result:
            # Get price from exchange
            for fill in trade_result['fills']:
                prices.append(float(fill['price']))
            fill_price = sum(prices) / len(prices)
            self.logger.info("Current price %s, Fill price: %s" % (current_price, fill_price))

            return (fill_price,
                    trade_result['executedQty'],
                    trade_result['cummulativeQuoteQty'],
                    trade_result['orderId'])

        return [None] * 4

    def __get_commission(self, trade_result):
        """
        Extract and collate commission from trade result dict

        """
        usd_total = 0
        if self.prod and 'fills' in trade_result and not(self.test_trade or self.test_data):
            for fill in trade_result['fills']:
                if 'USD' in fill['commissionAsset']:
                    usd_total += float(fill['commission'])
                else:
                    # convert to usd
                    usd_total += base2quote(float(fill['commission']),
                                            fill['commissionAsset']+'USDT')
        return usd_total

    @GET_EXCEPTIONS
    def __close_margin_short(self, short_list, drawdowns=None, drawups=None):
        """
        Get item details and attempt to close margin short trade according to config
        Returns True|False
        """

        self.logger.info("We need to close margin short %s" % short_list)
        dbase = Mysql(test=self.test_data, interval=self.interval)
        name = self.config.main.name
        for pair, current_time, current_price, event, _ in short_list:
            base = get_base(pair)
            quote = get_quote(pair)

            open_price, quote_in, _, base_in, borrowed, _ = dbase.get_trade_value(pair)[0]
            if not open_price:
                return False
            # Quantity of base_asset we can buy back based on current price
            quantity = base_in


            if not quantity:
                self.logger.info("close_margin_short: unable to get quantity for %s" % pair)
                return False

            perc_inc = - (perc_diff(open_price, current_price))
            quote_out = sub_perc(perc_inc, quote_in)

            self.logger.info("Closing margin short %s of %s for %.15f %s"
                             % (quantity, pair, float(current_price), quantity))
            if self.prod and not self.test_data:
                amt_str = get_step_precision(pair, quantity)

                trade_result = self.client.margin_order(symbol=pair,
                                                        side=self.client.buy,
                                                        quantity=amt_str,
                                                        order_type=self.client.market,
                                                        isolated=str2bool(
                                                            self.config.main.isolated))

                self.logger.info("%s close margin short result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Trade error-close short %s: %s" % (pair, trade_result))
                    return False

                actual_borrowed = self.get_borrowed(pair=pair, symbol=base)
                borrowed = actual_borrowed if float(borrowed) > float(actual_borrowed) else borrowed

                if float(borrowed) > 0:
                    self.logger.info("Trying to repay: %s %s for pair short %s" %(borrowed, base, pair))
                    repay_result = self.client.margin_repay(
                        symbol=pair, quantity=float(borrowed),
                        isolated=str2bool(self.config.main.isolated),
                        asset=base)
                    if "msg" in repay_result:
                        self.logger.error("Repay error-close short %s: %s" % (pair, repay_result))
                        self.logger.error("Params: %s, %s, %s %s" % (pair, borrowed,
                                                                     self.config.main.isolated,
                                                                     base))

                    self.logger.info("Repay result for short %s: %s" % (pair, repay_result))
                else:
                    self.logger.info("No borrowed funds to repay for short %s" % pair)

                # override values from exchange if in prod
                fill_price, quantity, quote_out, order_id = \
                        self.__get_result_details(current_price, trade_result)
            else:
                order_id = 0
                fill_price = current_price
                trade_result = {}

            commission_usd = self.__get_commission(trade_result)


            if self.test_data or self.test_trade or \
                    (not self.test_trade and 'transactTime' in trade_result):
                if name == "api":
                    name = "%"
                dbase.update_trades(pair=pair, close_time=current_time,
                                    close_price=fill_price,
                                    quote=quote_out, base_out=quantity, name=name,
                                    drawdown=drawdowns[pair], drawup=drawups[pair],
                                    symbol_name=quote, commission=commission_usd,
                                    order_id=order_id)

                open_time, profit = dbase.fetch_sql_data("select p.open_time, p.usd_profit from "
                                                         "trades t, profit p where p.id=t.id and "
                                                         "t.pair='{}' and t.closed_by='{}' order "
                                                         "by t.id desc limit 1"
                                                         .format(pair, name), header=False)[0]

                self.__send_notifications(pair=pair, close_time=current_time, perc=perc_inc,
                                          fill_price=current_price, interval=self.interval,
                                          event=event, action='CLOSE', usd_profit=profit,
                                          quote=quote_out, open_time=open_time)
            else:
                self.logger.critical("Close short Failed %s:%s" % (name, pair))
                send_slack_message("alerts", "Close short Failed %s:%s" % (name, pair))

        del dbase
        return True

    @GET_EXCEPTIONS
    def __open_margin_short(self, short_list):
        """
        Get item details and attempt to open margin short trade according to config
        Returns True|False
        """
        self.logger.info("We have %s potential items to open short" % len(short_list))
        dbase = Mysql(test=self.test_data, interval=self.interval)

        for pair, current_time, current_price, event, _ in short_list:
            base = get_base(pair)

            total_amount_to_use = self.get_total_amount_to_use(dbase, account='margin', pair=pair)
            current_base_bal = total_amount_to_use['balance_amt']
            amount_to_borrow = total_amount_to_use['loan_amt']

            borrowed_usd = amount_to_borrow if base == 'USDT' else \
                    base2quote(amount_to_borrow, base+'USDT')

            total_base_amount = get_step_precision(pair, sub_perc(1, amount_to_borrow +
                                                                  current_base_bal))
            total_quote_amount = base2quote(total_base_amount, pair)
            self.logger.info("Opening margin short %s of %s with %s at %s"
                             % (total_base_amount, pair, total_quote_amount, current_price))
            if self.prod:

                if float(amount_to_borrow) <= 0:
                    self.logger.critical("Borrow amount is zero for short pair %s.  Continuing" % pair)
                    amt_str = current_base_bal

                else:  # amount to borrow
                    self.logger.info("Will attempt to borrow %s of %s. Balance: %s"
                                     % (amount_to_borrow, base, total_base_amount))
                    amt_str = total_base_amount
                    borrow_res = self.client.margin_borrow(
                        symbol=pair, quantity=amount_to_borrow,
                        isolated=str2bool(self.config.main.isolated),
                        asset=base)
                    if "msg" in borrow_res:
                        self.logger.error("Borrow error-open %s: %s while trying to borrow short %s %s"
                                          % (pair, borrow_res, amount_to_borrow, base))
                        return False

                    self.logger.info(borrow_res)

                trade_result = self.client.margin_order(symbol=pair, side=self.client.sell,
                                                        quantity=amt_str,
                                                        order_type=self.client.market,
                                                        isolated=str2bool(
                                                            self.config.main.isolated))
                self.logger.info("%s open margin short result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Short Trade error-open %s: %s" % (pair, str(trade_result)))
                    self.logger.error("Vars: quantity:%s, bal:%s, borrowed: %s"
                                      % (amt_str, current_base_bal, amount_to_borrow))
                    return False

                # override values from exchange if in prod
                fill_price, amt_str, total_quote_amount, order_id = \
                        self.__get_result_details(current_price, trade_result)

            else:  # not prod
                amt_str = total_base_amount
                order_id = 0
                fill_price = current_price
                trade_result = {}

            commission_usd = self.__get_commission(trade_result)

            if self.test_data or self.test_trade or \
                    (not self.test_trade and 'transactTime' in trade_result):

                try:
                    amt_str = sub_perc(dbase.get_complete_commission()/2, amt_str)
                except (KeyError, TypeError):  # Empty dict, or no commission for base
                    pass

                dbase.insert_trade(pair=pair, price=fill_price, date=current_time,
                                   quote_amount=total_quote_amount,
                                   base_amount=amt_str, borrowed=amount_to_borrow,
                                   borrowed_usd=borrowed_usd,
                                   divisor=self.config.main.divisor,
                                   direction=self.config.main.trade_direction,
                                   symbol_name=get_quote(pair), commission=str(commission_usd),
                                   order_id=order_id)

                self.__send_notifications(pair=pair, open_time=current_time,
                                          fill_price=current_price, interval=self.interval,
                                          event=event, action='OPEN', usd_profit='N/A',
                                          quote=total_quote_amount, close_time='N/A')
        del dbase
        return True

    @GET_EXCEPTIONS
    def __close_spot_long(self, sell_list, drawdowns=None, drawups=None, update_db=True):
        """
        Get item details and attempt to close spot trade according to config
        Returns True|False
        """

        self.logger.info("We need to close spot long %s" % sell_list)
        dbase = Mysql(test=self.test_data, interval=self.interval)
        name = self.config.main.name
        for pair, current_time, current_price, event, _ in sell_list:
            quantity = dbase.get_quantity(pair)

            if not quantity:
                self.logger.info("close_spot_long: unable to find quantity for %s" % pair)
                return False

            open_price, quote_in, _, _, _, _ = dbase.get_trade_value(pair)[0]
            if not open_price:
                return False

            perc_inc = perc_diff(open_price, current_price)
            quote_out = add_perc(perc_inc, quote_in)

            self.logger.info("Closing spot long %s of %s for %.15f %s"
                             % (quantity, pair, float(current_price), quote_out))
            if self.prod and not self.test_data:

                amt_str = get_step_precision(pair, quantity)

                trade_result = self.client.spot_order(
                    symbol=pair, side=self.client.sell, quantity=amt_str,
                    order_type=self.client.market, test=self.test_trade)

                self.logger.info("%s close spot long result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Long Trade error-close %s: %s" % (pair, trade_result))
                    return False

                # override values from exchange if in prod
                fill_price, quantity, quote_out, order_id = \
                        self.__get_result_details(current_price, trade_result)

            else:  # not prod
                order_id = 0
                fill_price = current_price
                trade_result = {}

            commission_usd = self.__get_commission(trade_result)

            if self.test_data or self.test_trade or \
                    (not self.test_trade and 'transactTime' in trade_result):
                if name == "api":
                    name = "%"
                if update_db:
                    dbase.update_trades(pair=pair, close_time=current_time,
                                        close_price=fill_price, quote=quote_out,
                                        base_out=quantity, name=name,
                                        drawdown=drawdowns[pair], drawup=drawups[pair],
                                        symbol_name=get_quote(pair), commission=commission_usd,
                                        order_id=order_id)

                    open_time, profit = dbase.fetch_sql_data("select p.open_time, p.usd_profit "
                                                             "from trades t, profit p where "
                                                             "p.id=t.id and t.pair='{}' and "
                                                             "t.closed_by='{}' order by t.id desc "
                                                             "limit 1".format(pair, name),
                                                             header=False)[0]

                    self.__send_notifications(pair=pair, close_time=current_time, perc=perc_inc,
                                              fill_price=fill_price, interval=self.interval,
                                              event=event, action='CLOSE', usd_profit=profit,
                                              quote=quote_out, open_time=open_time)
            else:
                self.logger.critical("Close spot long Failed %s:%s" % (name, pair))
                send_slack_message("alerts", "Close spot long Failed %s:%s" % (name, pair))
                return False
        del dbase
        return True

    @GET_EXCEPTIONS
    def __close_margin_long(self, sell_list, drawdowns=None, drawups=None):
        """
        Get item details and attempt to close margin long trade according to config
        Returns True|False
        """

        self.logger.info("We need to close margin long %s" % sell_list)
        dbase = Mysql(test=self.test_data, interval=self.interval)
        name = self.config.main.name
        for pair, current_time, current_price, event, _ in sell_list:
            quantity = dbase.get_quantity(pair)
            if not quantity:
                self.logger.info("close_margin_long: unable to find quantity for %s" % pair)
                return False

            open_price, quote_in, _, _, borrowed, _, = dbase.get_trade_value(pair)[0]
            if not open_price:
                return False

            perc_inc = perc_diff(open_price, current_price)
            quote_out = add_perc(perc_inc, quote_in)

            self.logger.info("Closing margin long %s of %s for %.15f %s"
                             % (quantity, pair, float(current_price), quote_out))
            quote = get_quote(pair)

            if self.prod:
                amt_str = get_step_precision(pair, quantity)

                trade_result = self.client.margin_order(symbol=pair, side=self.client.sell,
                                                        quantity=amt_str,
                                                        order_type=self.client.market,
                                                        isolated=str2bool(
                                                            self.config.main.isolated))

                self.logger.info("%s close margin long result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Margin long Trade error-close %s: %s" % (pair, trade_result))
                    return False
                actual_borrowed = self.get_borrowed(pair=pair, symbol=quote)
                borrowed = actual_borrowed if float(borrowed) > float(actual_borrowed) else borrowed

                if float(borrowed) > 0:
                    self.logger.info("Trying to repay: %s %s for pair %s" %(borrowed, quote, pair))
                    repay_result = self.client.margin_repay(
                        symbol=pair, quantity=float(borrowed),
                        isolated=str2bool(self.config.main.isolated),
                        asset=quote)
                    if "msg" in repay_result:
                        self.logger.error("Repay error-close %s: %s" % (pair, repay_result))
                        self.logger.error("Params: %s, %s, %s %s" % (pair, borrowed,
                                                                     self.config.main.isolated,
                                                                     quote))
                    self.logger.info("Repay result for %s: %s" % (pair, repay_result))
                else:
                    self.logger.info("No borrowed funds to repay for %s" % pair)

                # override values from exchange if in prod
                fill_price, quantity, quote_out, order_id = \
                        self.__get_result_details(current_price, trade_result)
            else:
                order_id = 0
                fill_price = current_price
                trade_result = {}

            commission_usd = self.__get_commission(trade_result)

            if self.test_data or self.test_trade or not self.test_trade:
                if name == "api":
                    name = "%"

                dbase.update_trades(pair=pair, close_time=current_time,
                                    close_price=fill_price, quote=quote_out,
                                    base_out=quantity, name=name,
                                    drawdown=drawdowns[pair],
                                    drawup=drawups[pair], symbol_name=quote,
                                    commission=commission_usd, order_id=order_id)

                open_time, profit = dbase.fetch_sql_data("select p.open_time, p.usd_profit "
                                                         "from trades t, profit p where "
                                                         "p.id=t.id and t.pair='{}' and "
                                                         "t.closed_by='{}' order by t.id desc "
                                                         "limit 1".format(pair, name),
                                                         header=False)[0]

                self.__send_notifications(pair=pair, close_time=current_time, perc=perc_inc,
                                          fill_price=fill_price, interval=self.interval,
                                          event=event, action='CLOSE', usd_profit=profit,
                                          quote=quote_out, open_time=open_time)
            else:
                self.logger.critical("Close margin long Failed %s:%s" % (name, pair))
                send_slack_message("alerts", "Close margin long Failed %s:%s" % (name, pair))
                return False

        del dbase
        return True
