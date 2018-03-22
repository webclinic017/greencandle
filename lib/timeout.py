#pylint: disable=unused-argument

import signal
from contextlib import contextmanager
from lib.logger import getLogger

LOGGER = getLogger(__name__)


def timeout_handler(signum, frame):
    """ Register a handler for the timeout"""
    raise TimeoutException()

class TimeoutException(Exception):
    """Custom timeout exception for use in timeout handler """
    pass

@contextmanager
def restrict_timeout(time, name):
    """
    context to handle timeout
    Args:
        time: int seconds until timeout
        name: string function or code block name
    Returns:
        None
    Usage Example:
        with restrict_timeout(5, "my function"):
            run_function()
    This will execute run_run function for only 5 seconds then log error containg name and timeout
    value

    """

    signal.alarm(time)

    signal.alarm(time)
    signal.signal(signal.SIGALRM, timeout_handler)
    try:
        yield None
    except TimeoutException:
        LOGGER.critical("Timed out waiting {0} seconds for {1}".format(time, name))
    finally:
        signal.alarm(0)
