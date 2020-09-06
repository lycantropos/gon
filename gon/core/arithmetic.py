from decimal import Decimal
from fractions import Fraction
from typing import Iterable

from gon.hints import Coordinate


def robust_divide(dividend: Coordinate, divisor: int) -> Coordinate:
    return (Fraction(dividend, divisor)
            if isinstance(dividend, int)
            else dividend / divisor)


def robust_sqrt(value: Coordinate) -> Coordinate:
    return Fraction.from_decimal(_to_decimal(value).sqrt())


def _to_decimal(value: Coordinate) -> Decimal:
    return (Decimal(value.numerator) / value.denominator
            if isinstance(value, Fraction)
            else Decimal(value))


def non_negative_min(numbers: Iterable[Coordinate]) -> Coordinate:
    numbers = iter(numbers)
    result = next(numbers)
    if not result:
        return result
    for number in numbers:
        if not number:
            return number
        elif number < result:
            result = number
    return result
