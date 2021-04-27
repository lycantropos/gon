from typing import Iterable

from .hints import Coordinate


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
