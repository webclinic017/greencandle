"""
Common functions that don't belong anywhere else
"""

from decimal import Decimal
import numpy

def make_float(arr):
    """Convert dataframe array into float array"""
    return numpy.array([float(x) for x in arr.values])

def pip_calc(open_val, close_val):
    open_val = Decimal(open_val)
    close_val = Decimal(close_val)
    if "." not in str(open_val):
        multiplier = Decimal(0.0001)
    elif str(open_val).index(".") >= 3:  # JPY pair
        multiplier = Decimal(0.01)
    else:
        multiplier = Decimal(0.0001)

    pips = round((close_val - open_val) / multiplier)
    return int(pips)

def pipify(value):
    """
    return 4 digits after decimal point
    representing the pip
    as an int
    """
    value = Decimal(value)
    try:
        pip_value = int((str(value) + "000").split(".")[-1][:4])
        return pip_value
    except ValueError:
        print("Value Error", value)
        return None

def add_perc(perc, num):
    """
    Add a percentage to a number
    Args:
        perc: Percent num to add
        num: number to add to
    Returns:
        total: num + perc%
    """
    return num * (1 + perc/100)

def sub_perc(perc, num):
    """
    Subtractsa percentage to a number
    Args:
        perc: Percent num to subtract
        num: number to subtract from
    Returns:
        total: num - perc%
    """
    return num * (1 - perc/100)
