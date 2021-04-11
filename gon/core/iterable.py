import sys
from itertools import chain
from typing import (Iterable,
                    List,
                    Sequence,
                    Tuple,
                    TypeVar)

_T = TypeVar('_T')

flatten = chain.from_iterable


def shift_sequence(sequence: Sequence[_T], step: int) -> Sequence[_T]:
    return (sequence[step:] + sequence[:step]
            if step
            else sequence)


def to_pairs_iterable(sequence: Sequence[_T]) -> Iterable[Tuple[_T, _T]]:
    return ((sequence[index - 1], sequence[index])
            for index in range(len(sequence)))


def to_pairs_sequence(sequence: Sequence[_T]) -> List[Tuple[_T, _T]]:
    return [(sequence[index - 1], sequence[index])
            for index in range(len(sequence))]


if sys.version_info < (3, 6):
    OrderedDict = dict
else:
    from collections import OrderedDict
unique_ever_seen = OrderedDict.fromkeys
del OrderedDict, sys
