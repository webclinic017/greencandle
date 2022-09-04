#pylint: disable=wrong-import-position,import-error,no-member,logging-not-lazy
#pylint: disable=wrong-import-order,no-else-return,no-else-break,no-else-continue
#pylint: disable=too-many-locals,consider-using-ternary
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
from greencandle.lib.binance_accounts import get_binance_spot, get_binance_cross, \
    get_binance_isolated, base2quote, quote2base
from greencandle.lib.balance_common import get_base, get_quote, get_step_precision
from greencandle.lib.common import perc_diff, add_perc, sub_perc, AttributeDict, QUOTES
from greencandle.lib.alerts import send_gmail_alert, send_push_notif, send_slack_trade, \
        send_slack_message

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
        return (drain and time_range[0] <= time_str <= time_range[1]) or manual_drain

    def __send_redis_trade(self, **kwargs):
        """
        Send trade event to redis
        """
        valid_keys = ["pair", "current_time", "price", "interval", "event"]
        kwargs = AttributeDict(kwargs)
        for key in valid_keys:
            if key not in valid_keys:
                raise KeyError("Missing param %s" % key)

        self.logger.debug('Strategy - Adding to redis')
        redis = Redis()
        # Change time back to milliseconds to line up with entries in redis
        mepoch = int(time.mktime(time.strptime(kwargs.current_time,
                                               '%Y-%m-%d %H:%M:%S'))) * 1000 + 999

        # if we are in an intermittent check - use previous timeframe
        if not str(mepoch).endswith('99999'):
            try:
                mepoch = redis.get_items(kwargs.pair, kwargs.interval)[-1].decode().split(':')[-1]
            except IndexError:
                self.logger.debug("Unable to get last epoch time for %s %s" % (kwargs.pair,
                                                                               kwargs.interval))
                return

        data = {"event":{"result": kwargs.event,
                         "current_price": format(float(kwargs.price), ".20f"),
                         "date": mepoch,
                        }}

        redis.redis_conn(kwargs.pair, kwargs.interval, data, mepoch)
        del redis

    def check_pairs(self, items_list):
        """
        Check we can trade which each of given trading pairs
        Return filtered list
        """
        dbase = Mysql(test=self.test_data, interval=self.interval)
        current_trades = dbase.get_trades()
        avail_slots = int(self.config.main.max_trades) - len(current_trades)
        self.logger.info("%s buy slots available" % avail_slots)
        if avail_slots <= 0:
            self.logger.warning("Too many trades, skipping")
            send_slack_message("alerts", "Too many trades, skipping")
            return []
        elif self.is_in_drain() and not self.test_data:
            self.logger.warning("strategy is in drain, skipping...")
            send_slack_message("alerts", "strategy is in drain, skipping")
            return []

        final_list = []
        manual = "any" in self.config.main.name
        for item in items_list:
            if current_trades and [trade for trade in current_trades if item[0] in trade]:
                self.logger.warning("We already have a trade of %s, skipping..." % item[0])
            elif not manual and (item[0] not in self.config.main.pairs and not self.test_data):
                self.logger.error("Pair %s not in main_pairs, skipping..." % item[0])
            else:
                final_list.append(item)
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
        else:

            for item in items_list:

                # Number of trades within scope
                dbase = Mysql(test=self.test_data, interval=self.interval)
                count = dbase.fetch_sql_data("select count(*) from trades where close_price "
                                             "is NULL and pair like '%{0}' and name='{1}'"
                                             .format(item[0], self.config.main.name),
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
            details = self.client.get_cross_margin_details()
            for item in details['userAssets']:
                borrowed = float(item['borrowed'])
                asset = item['asset']
                if asset == symbol:
                    return borrowed if borrowed else 0

        elif str2bool(self.config.main.isolated):
            details = self.client.get_isolated_margin_details(pair)
            if details['assets'][0]['quoteAsset']['asset'] == symbol:
                return float(details['assets'][0]['quoteAsset']['borrowed'])
            elif details['assets'][0]['baseAsset']['asset'] == symbol:
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
        test_balances = self.__get_test_balance(dbase, account=account)[account]
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
                final = float(get_binance_isolated()['isolated'][pair][symbol])
            except KeyError:
                pass

        elif account == 'margin' and not str2bool(self.config.main.isolated):
            try:
                final = float(get_binance_cross()[account][symbol]['count'])
            except KeyError:
                pass

        # Use 99% of amount determined by divisor
        return sub_perc(1, final / float(self.config.main.divisor)) if final else 0

    def get_amount_to_borrow(self, pair, dbase):
        """
        Get amount to borrow based on pair, and trade direction
        divide by divisor and return in the symbol we need to borrow
        Only return 99% of the value
        Returns: float in base if short, or quote if long
        """
        orig_base = get_base(pair)
        orig_quote = get_quote(pair)
        orig_direction = self.config.main.trade_direction

        # if isolated strategy
        # get current borrowed
        strategy = self.config.main.name.split('-')[2]
        mode = "isolated" if str2bool(self.config.main.isolated) else "cross"
        rows = dbase.get_current_borrowed(strategy, mode)
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
            borrow_usd = max_borrow if 'USD' in asset else base2quote(max_borrow, asset+'USDT')
        else:
            # cross always returns USD
            borrow_usd = self.client.get_max_borrow()

        # sum of total borrowed and total borrowable
        total = (float(borrowed_usd) + float(borrow_usd))

        # divide total by divisor
        # convert to quote asset if not USDT
        if self.config.main.trade_direction == "long":
            if "USD" in orig_quote:
                final = total
            else:
                final = quote2base(total, orig_quote+"USDT")

        #convert to base asset if we are short
        else:
            final = quote2base(total, orig_base+"USDT")

        # Use 99% of amount determined by divisor
        return sub_perc(1, final / float(self.config.main.divisor))

    def __open_margin_long(self, long_list):
        """
        Get item details and attempt to trade according to config
        Returns True|False
        """
        self.logger.info("We have %s potential items to long" % len(long_list))

        dbase = Mysql(test=self.test_data, interval=self.interval)

        for pair, current_time, current_price, event in long_list:
            amount_to_borrow = self.get_amount_to_borrow(pair, dbase)
            current_quote_bal = self.get_balance_to_use(dbase, account='margin', pair=pair)
            quote = get_quote(pair)

            borrowed_usd = amount_to_borrow if quote == 'USDT' else \
                    base2quote(amount_to_borrow, quote + 'USDT')
            # amt in base
            quote_to_use = current_quote_bal + amount_to_borrow
            base_to_use = quote2base(quote_to_use, pair)

            self.logger.info("Buying %s of %s with %s %s at %s"
                             % (base_to_use, pair, current_quote_bal+amount_to_borrow,
                                quote, current_price))
            if self.prod:

                if float(amount_to_borrow) <= 0:
                    self.logger.critical("Insufficient funds to borrow for %s" % pair)
                    return False

                self.logger.info("Will attempt to borrow %s of %s. Balance: %s"
                                 % (amount_to_borrow, quote, current_quote_bal))


                borrow_res = self.client.margin_borrow(
                    symbol=pair, quantity=amount_to_borrow,
                    isolated=str2bool(self.config.main.isolated),
                    asset=quote)
                if "msg" in borrow_res:
                    self.logger.error("Borrow error-open %s: %s while trying to borrow %s %s"
                                      % (pair, borrow_res, amount_to_borrow, quote))
                    return False

                self.logger.info(borrow_res)
                amt_str = get_step_precision(pair, base_to_use)
                trade_result = self.client.margin_order(symbol=pair, side=self.client.buy,
                                                        quantity=amt_str,
                                                        order_type=self.client.market,
                                                        isolated=str2bool(
                                                            self.config.main.isolated))
                self.logger.info("%s result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Trade error-open %s: %s" % (pair, str(trade_result)))
                    self.logger.error("Vars: base quantity:%s, quote_quantity: %s quote bal:%s, "
                                      "quote_borrowed: %s"
                                      % (amt_str, quote_to_use, current_quote_bal,
                                         amount_to_borrow))
                    return False

                quote_to_use = trade_result.get('cummulativeQuoteQty', quote_to_use)
                order_id = trade_result.get('orderId')
                amt_str = trade_result.get('executedQty')
            else: # not prod
                amt_str = base_to_use
                order_id = 0

            fill_price = current_price if self.test_trade or self.test_data else \
                    self.__get_fill_price(current_price, trade_result)
            commission_usd = self.__get_commission(trade_result) if self.prod else 0

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

                self.__send_notifications(pair=pair, current_time=current_time,
                                          fill_price=fill_price, interval=self.interval,
                                          event=event, action='OPEN', usd_profit='N/A',
                                          quote=quote_to_use)

        del dbase
        return True

    @GET_EXCEPTIONS
    def __get_test_balance(self, dbase, account=None):
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
            db_result = dbase.fetch_sql_data("select sum(quote_out-quote_in) from trades "
                                             "where pair like '%{0}' and name='{1}'"
                                             .format(quote, self.config.main.name),
                                             header=False)[0][0]
            db_result = float(db_result) if db_result and db_result > 0 else 0
            current_trade_values = dbase.fetch_sql_data("select sum(quote_in) from trades "
                                                        "where pair like '%{0}' and "
                                                        "quote_out is null"
                                                        .format(quote), header=False)[0][0]
            current_trade_values = float(current_trade_values) if \
                    current_trade_values else 0
            balance[account][quote]['count'] = max(db_result, current_trade_values,
                                                   balance[account][quote]['count'])
        return balance

    @GET_EXCEPTIONS
    def __open_spot_long(self, buy_list):
        """
        Get item details and attempt to trade according to config
        Returns True|False
        """
        self.logger.info("We have %s potential items to buy" % len(buy_list))

        dbase = Mysql(test=self.test_data, interval=self.interval)

        for pair, current_time, current_price, event in buy_list:
            quote_amount = self.get_balance_to_use(dbase, 'binance', pair=pair)
            quote = get_quote(pair)

            if quote_amount <= 0:
                self.logger.critical("Unable to get balance %s for quote %s while trading %s"
                                     % (quote_amount, quote, pair))
                return False

            amount = quote2base(quote_amount, pair)

            self.logger.info("Buying %s of %s with %s %s"
                             % (amount, pair, quote_amount, quote))
            self.logger.debug("amount to buy: %s, current_price: %s, amount:%s"
                              % (quote_amount, current_price, amount))
            if self.prod and not self.test_data:
                amt_str = get_step_precision(pair, amount)

                trade_result = self.client.spot_order(symbol=pair, side=self.client.buy,
                                                      quantity=amt_str,
                                                      order_type=self.client.market,
                                                      test=self.test_trade)

                self.logger.info("%s result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Trade error-open %s: %s" % (pair, str(trade_result)))
                    self.logger.error("Vars: quantity:%s, bal:%s" % (amt_str, quote_amount))
                    return False

                quote_amount = trade_result.get('cummulativeQuoteQty', quote_amount)
                order_id = trade_result.get('orderId')

            else:
                trade_result = True
                order_id = 0

            fill_price = current_price if self.test_trade or self.test_data else \
                    self.__get_fill_price(current_price, trade_result)
            commission_usd = self.__get_commission(trade_result) if self.prod else 0

            if self.test_data or self.test_trade or \
                    (not self.test_trade and 'transactTime' in trade_result):
                # only insert into db, if:
                # 1. we are using test_data
                # 2. we performed a test trade which was successful - (empty dict)
                # 3. we proformed a real trade which was successful - (transactTime in dict)

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
                    self.__send_notifications(pair=pair, current_time=current_time,
                                              fill_price=fill_price, interval=self.interval,
                                              event=event, action='OPEN', usd_profit='N/A',
                                              quote=quote_amount)

        del dbase
        return True

    def __send_notifications(self, perc=None, **kwargs):
        """
        Pass given data to trade notification functions
        """
        valid_keys = ["pair", "current_time", "fill_price", "event", "action", "usd_profit",
                      "quote"]
        kwargs = AttributeDict(kwargs)
        for key in valid_keys:
            if key not in valid_keys:
                raise KeyError("Missing param %s" % key)

        self.__send_redis_trade(pair=kwargs.pair, current_time=kwargs.current_time,
                                price=kwargs.fill_price, interval=self.interval,
                                event=kwargs.action, usd_profit=kwargs.usd_profit)

        send_push_notif(kwargs.action, kwargs.pair, '%.15f' % float(kwargs.fill_price))
        send_gmail_alert(kwargs.action, kwargs.pair, '%.15f' % float(kwargs.fill_price))
        usd_quote = kwargs.quote if 'USD' in kwargs.pair else \
                base2quote(kwargs.quote, get_quote(kwargs.pair)+'USDT')
        send_slack_trade(channel='trades', event=kwargs.event, perc=perc,
                         pair=kwargs.pair, action=kwargs.action, price=kwargs.fill_price,
                         usd_profit=kwargs.usd_profit, quote=kwargs.quote, usd_quote=usd_quote)

    def __get_fill_price(self, current_price, trade_result):
        """
        Extract and average trade result from exchange output
        """
        prices = []
        if 'transactTime' in trade_result:
            # Get price from exchange
            for fill in trade_result['fills']:
                prices.append(float(fill['price']))
            fill_price = sum(prices) / len(prices)
            self.logger.info("Current price %s, Fill price: %s" % (current_price, fill_price))
            return fill_price
        return None

    def __get_commission(self, trade_result):
        """
        Extract and collate commission from trade result dict

        """
        usd_total = 0
        if 'fills' in trade_result and not(self.test_trade or self.test_data):
            for fill in trade_result['fills']:
                if 'USD' in fill['commissionAsset']:
                    usd_total += fill['commission']
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
        for pair, current_time, current_price, event in short_list:
            base = get_base(pair)
            quote = get_quote(pair)

            open_price, quote_in, _, _, borrowed, _, = dbase.get_trade_value(pair)[0]
            if not open_price:
                return False
            # Quantity of base_asset we can buy back based on current price
            quantity = quote2base(quote_in, pair)

            if not quantity:
                self.logger.info("close_margin_short: unable to get quantity for %s" % pair)
                return False

            perc_inc = - (perc_diff(open_price, current_price))
            quote_out = sub_perc(perc_inc, quote_in)

            self.logger.info("Closing %s of %s for %.15f %s"
                             % (quantity, pair, float(current_price), quantity))
            if self.prod and not self.test_data:
                amt_str = get_step_precision(pair, quantity)

                trade_result = self.client.margin_order(symbol=pair,
                                                        side=self.client.buy,
                                                        quantity=amt_str,
                                                        order_type=self.client.market,
                                                        isolated=str2bool(
                                                            self.config.main.isolated))

                order_id = trade_result.get('orderId')
                self.logger.info("%s result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Trade error-close %s: %s" % (pair, trade_result))
                    return False

                actual_borrowed = self.get_borrowed(pair=pair, symbol=base)
                borrowed = actual_borrowed if float(borrowed) > float(actual_borrowed) else borrowed

                if float(borrowed) > 0:
                    self.logger.info("Trying to repay: %s %s for pair %s" %(borrowed, base, pair))
                    repay_result = self.client.margin_repay(
                        symbol=pair, quantity=float(borrowed),
                        isolated=str2bool(self.config.main.isolated),
                        asset=base)
                    if "msg" in repay_result:
                        self.logger.error("Repay error-close %s: %s" % (pair, repay_result))
                        self.logger.error("Params: %s, %s, %s %s" % (pair, borrowed,
                                                                     self.config.main.isolated,
                                                                     base))

                    self.logger.info("Repay result for %s: %s" % (pair, repay_result))
                else:
                    self.logger.info("No borrowed funds to repay for %s" % pair)

            else:
                order_id = 0

            fill_price = current_price if self.test_trade or self.test_data else \
                    self.__get_fill_price(current_price, trade_result)
            commission_usd = self.__get_commission(trade_result) if self.prod else 0


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

                profit = dbase.fetch_sql_data("select p.usd_profit from trades t, profit p where "
                                              "p.id=t.id and t.pair='{}' and t.closed_by='{}' "
                                              "order by t.id desc limit 1".format(pair, name),
                                              header=False)[0][0]

                self.__send_notifications(pair=pair, current_time=current_time, perc=perc_inc,
                                          fill_price=current_price, interval=self.interval,
                                          event=event, action='CLOSE', usd_profit=profit,
                                          quote=quote_out)
            else:
                self.logger.critical("Sell Failed %s:%s" % (name, pair))
                send_slack_message("alerts", "Sell Failed %s:%s" % (name, pair))

        del dbase
        return True

    @GET_EXCEPTIONS
    def __open_margin_short(self, short_list):
        """
        Get item details and attempt to open margin short trade according to config
        Returns True|False
        """
        self.logger.info("We have %s potential items to short" % len(short_list))
        dbase = Mysql(test=self.test_data, interval=self.interval)

        for pair, current_time, current_price, event in short_list:
            base = get_base(pair)
            current_base_bal = self.get_balance_to_use(dbase, account='margin', pair=pair)

            amount_to_borrow = self.get_amount_to_borrow(pair, dbase)
            borrowed_usd = amount_to_borrow if base == 'USDT' else \
                    base2quote(amount_to_borrow, base+'USDT')

            total_base_amount = get_step_precision(pair, amount_to_borrow + current_base_bal)
            total_quote_amount = base2quote(total_base_amount, pair)

            if self.prod:
                self.logger.info("Will attempt to borrow %s of %s. Balance: %s"
                                 % (amount_to_borrow, base, total_base_amount))
                amt_str = total_base_amount
                borrow_res = self.client.margin_borrow(
                    symbol=pair, quantity=amount_to_borrow,
                    isolated=str2bool(self.config.main.isolated),
                    asset=base)
                if "msg" in borrow_res:
                    self.logger.error("Borrow error-open %s: %s while trying to borrow %s %s"
                                      % (pair, borrow_res, amount_to_borrow, base))
                    return False

                self.logger.info(borrow_res)
                trade_result = self.client.margin_order(symbol=pair, side=self.client.sell,
                                                        quantity=amt_str,
                                                        order_type=self.client.market,
                                                        isolated=str2bool(
                                                            self.config.main.isolated))
                order_id = trade_result.get('orderId')
                self.logger.info("%s result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Trade error-open %s: %s" % (pair, str(trade_result)))
                    self.logger.error("Vars: quantity:%s, bal:%s, borrowed: %s"
                                      % (amt_str, current_base_bal, amount_to_borrow))
                    return False

            else:
                amt_str = total_base_amount
                order_id = 0
            fill_price = current_price if self.test_trade or self.test_data else \
                    self.__get_fill_price(current_price, trade_result)
            commission_usd = self.__get_commission(trade_result) if self.prod else 0

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

                self.__send_notifications(pair=pair, current_time=current_time,
                                          fill_price=current_price, interval=self.interval,
                                          event=event, action='OPEN', usd_profit='N/A',
                                          quote=total_quote_amount)
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
        for pair, current_time, current_price, event in sell_list:
            quantity = dbase.get_quantity(pair)

            if not quantity:
                self.logger.info("close_spot_long: unable to find quantity for %s" % pair)
                return False

            open_price, quote_in, _, _, _, _ = dbase.get_trade_value(pair)[0]
            if not open_price:
                return False

            perc_inc = perc_diff(open_price, current_price)
            quote_out = add_perc(perc_inc, quote_in)

            self.logger.info("Selling %s of %s for %.15f %s"
                             % (quantity, pair, float(current_price), quote_out))
            if self.prod and not self.test_data:

                amt_str = get_step_precision(pair, quantity)

                trade_result = self.client.spot_order(
                    symbol=pair, side=self.client.sell, quantity=amt_str,
                    order_type=self.client.market, test=self.test_trade)

                order_id = trade_result.get('orderId')
                self.logger.info("%s result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Trade error-close %s: %s" % (pair, trade_result))
                    return False
            else:
                order_id = 0

            commission_usd = self.__get_commission(trade_result) if self.prod else 0
            fill_price = current_price if self.test_trade or self.test_data else \
                    self.__get_fill_price(current_price, trade_result)

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

                    profit = dbase.fetch_sql_data("select p.usd_profit from trades t, "
                                                  "profit p where p.id=t.id and t.pair='{}' "
                                                  "and t.closed_by='{}' order by t.id desc "
                                                  "limit 1".format(pair, name),
                                                  header=False)[0][0]

                    self.__send_notifications(pair=pair, current_time=current_time, perc=perc_inc,
                                              fill_price=fill_price, interval=self.interval,
                                              event=event, action='CLOSE', usd_profit=profit,
                                              quote=quote_out)
            else:
                self.logger.critical("Sell Failed %s:%s" % (name, pair))
                send_slack_message("alerts", "Sell Failed %s:%s" % (name, pair))
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
        for pair, current_time, current_price, event in sell_list:
            quantity = dbase.get_quantity(pair)
            if not quantity:
                self.logger.info("close_margin_long: unable to find quantity for %s" % pair)
                return False

            open_price, quote_in, _, _, borrowed, _, = dbase.get_trade_value(pair)[0]
            if not open_price:
                return False

            perc_inc = perc_diff(open_price, current_price)
            quote_out = add_perc(perc_inc, quote_in)

            self.logger.info("Selling %s of %s for %.15f %s"
                             % (quantity, pair, float(current_price), quote_out))
            quote = get_quote(pair)

            if self.prod:
                amt_str = get_step_precision(pair, quantity)

                trade_result = self.client.margin_order(symbol=pair, side=self.client.sell,
                                                        quantity=amt_str,
                                                        order_type=self.client.market,
                                                        isolated=str2bool(
                                                            self.config.main.isolated))

                order_id = trade_result.get('orderId')
                self.logger.info("%s result: %s" %(pair, trade_result))
                if "msg" in trade_result:
                    self.logger.error("Trade error-close %s: %s" % (pair, trade_result))
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
            else:
                order_id = 0

            fill_price = current_price if self.test_trade or self.test_data else \
                    self.__get_fill_price(current_price, trade_result)
            commission_usd = self.__get_commission(trade_result) if self.prod else 0

            if self.test_data or self.test_trade or not self.test_trade:
                if name == "api":
                    name = "%"

                dbase.update_trades(pair=pair, close_time=current_time,
                                    close_price=fill_price, quote=quote_out,
                                    base_out=quantity, name=name,
                                    drawdown=drawdowns[pair],
                                    drawup=drawups[pair], symbol_name=quote,
                                    commission=commission_usd, order_id=order_id)

                profit = dbase.fetch_sql_data("select p.usd_profit from trades t, "
                                              "profit p where p.id=t.id and t.pair='{}' "
                                              "and t.closed_by='{}' order by t.id desc "
                                              "limit 1".format(pair, name),
                                              header=False)[0][0]

                self.__send_notifications(pair=pair, current_time=current_time, perc=perc_inc,
                                          fill_price=fill_price, interval=self.interval,
                                          event=event, action='CLOSE', usd_profit=profit,
                                          quote=quote_out)
            else:
                self.logger.critical("Sell Failed %s:%s" % (name, pair))
                send_slack_message("alerts", "Sell Failed %s:%s" % (name, pair))
                return False

        del dbase
        return True
