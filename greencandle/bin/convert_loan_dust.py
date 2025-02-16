#pylint:disable=too-many-locals
"""
Find pairs with small loans and no open trades to convert to USDT
"""

from greencandle.lib.auth import binance_auth
from greencandle.lib.mysql import Mysql
from greencandle.lib.binance_accounts import get_cross_assets_with_debt
from greencandle.lib.common import arg_decorator
from greencandle.lib.logger import get_logger


@arg_decorator
def main():
    """
    Find pairs with small loans and no open trades to convert to USDT
    """

    logger = get_logger("convert_loan_dust")
    dbase = Mysql()
    client = binance_auth()
    borrowed_set = get_cross_assets_with_debt(debt_type='borrowed')
    open_set = dbase.get_main_open_assets()
    # get assets with loan which are not in a trade
    main_set = set(borrowed_set - open_set)

    # get set of assets which we can convert (smaller than 10USDT)
    redeemable = client.get_small_liability_set()

    # get final list of assets which can be redeemed
    # and are in our earlier set
    final = list(main_set.intersection(redeemable))

    li_of_lis = []
    start = 0
    end = len(final)
    step = 10
    for item in range(start, end, step):
        li_of_lis.append(final[item:item+step])
    # get list of lists containing assets to convert
    # maximum 10 assets per list
    # maximum 3 lists
    # The rest will be discarded, likely picked up on next run
    if len(li_of_lis) > 3:
        logger.info("Some debts will be discarded in current run due to max size reached")

    for current_li in li_of_lis[:3]:
        logger.info("Converting the following small debts to USD: %s", str(current_li))
        client.small_liability_exchange(current_li)

if __name__ == '__main__':
    main()
