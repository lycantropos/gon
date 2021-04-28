from typing import Iterable

from .hints import Coordinate


def non_negative_min(values: Iterable[Coordinate]) -> Coordinate:
    iterator = iter(values)
    result = next(iterator)
    if not result:
        return result
    for number in iterator:
        if not number:
            return number
        elif number < result:
            result = number
    return result
