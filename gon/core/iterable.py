from itertools import chain
from typing import (Iterable,
                    Sequence,
                    TypeVar)

_T = TypeVar('_T')

flatten = chain.from_iterable


def non_negative_min(values: Iterable[_T]) -> _T:
    iterator = iter(values)
    result = next(iterator)
    if not result:
        return result
    for value in iterator:
        if not value:
            return value
        elif value < result:
            result = value
    return result


def shift_sequence(sequence: Sequence[_T], step: int) -> Sequence[_T]:
    return (sequence[step:] + sequence[:step]
            if step
            else sequence)


unique_ever_seen = dict.fromkeys
