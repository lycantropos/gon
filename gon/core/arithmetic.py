from fractions import Fraction
from typing import Iterable

from symba.base import sqrt

from .hints import Coordinate


def robust_divide(dividend: Coordinate, divisor: int) -> Coordinate:
    return (Fraction(dividend, divisor)
            if isinstance(dividend, int)
            else dividend / divisor)


sqrt = sqrt
ZERO = sqrt(0)


def non_negative_min(numbers: Iterable[Coordinate]) -> Coordinate:
    iterator = iter(numbers)
    result = next(iterator)
    if not result:
        return result
    for number in iterator:
        if not number:
            return number
        elif number < result:
            result = number
    return result
