#!/usr/bin/env python
#pylint: disable=no-member
"""
Collect OHLC and strategy data for later analysis
"""
import os
from pathlib import Path
import setproctitle
from greencandle.lib import config
from greencandle.lib.alerts import send_slack_message
from greencandle.lib.run import ProdRunner
from greencandle.lib.logger import get_logger, exception_catcher
from greencandle.lib.common import arg_decorator

config.create_config()
LOGGER = get_logger(__name__)
PAIRS = config.main.pairs.split()
MAIN_INDICATORS = config.main.indicators.split()
GET_EXCEPTIONS = exception_catcher((Exception))
RUNNER = ProdRunner()

def keepalive():
    """
    Periodically touch file for docker healthcheck
    """
    Path(f'/var/local/gc_get_{config.main.interval}.lock').touch()

@GET_EXCEPTIONS
def get_data():
    """
    Get-data run
    """
    LOGGER.info("Starting prod run")
    interval = config.main.interval
    RUNNER.prod_loop(interval, test=True, data=True, analyse=False)
    keepalive()
    LOGGER.info("Finished prod run")

@GET_EXCEPTIONS
@arg_decorator
def main():
    """
    Collect data:
    * OHLCs
    * Indicators

    This is stored on redis, and analysed by other services later.
    This service runs in a loop and executes periodically depending on timeframe used

    Usage: get_data
    """

    interval = config.main.interval
    setproctitle.setproctitle(f"get_data-{interval}")
    send_slack_message('alerts', "Starting initial prod run")
    LOGGER.info("Starting initial prod run")
    name = config.main.name.split('-')[-1]
    Path(f'/var/run/{config.main.base_env}-data-{interval}-{name}').touch()


    # only fetch historic indicator data for higher timeframes
    # as it will take hours/days to catch up in real time
    # lower timeframes with catch up after 4 candles have been processed

    # initial run, before scheduling begins
    RUNNER.prod_initial(interval, test=True, first_run=True, no_of_runs=4)
    if os.path.exists(f'/var/run/{config.main.base_env}-data-{interval}-{name}'):
        os.remove(f'/var/run/{config.main.base_env}-data-{interval}-{name}')
    send_slack_message('alerts', "Finished initial prod run")
    LOGGER.info("Finished initial prod run")

    while True:
        get_data()

if __name__ == '__main__':
    main()
