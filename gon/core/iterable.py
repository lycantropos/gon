import sys
from itertools import chain
from typing import (Iterable,
                    List,
                    Sequence,
                    Tuple)

from gon.hints import Domain

flatten = chain.from_iterable


def shift_sequence(sequence: Sequence[Domain], step: int) -> Sequence[Domain]:
    return (sequence[step:] + sequence[:step]
            if step
            else sequence)


def to_pairs_iterable(sequence: Sequence[Domain]
                      ) -> Iterable[Tuple[Domain, Domain]]:
    return ((sequence[index - 1], sequence[index])
            for index in range(len(sequence)))


def to_pairs_sequence(sequence: Sequence[Domain]
                      ) -> List[Tuple[Domain, Domain]]:
    return [(sequence[index - 1], sequence[index])
            for index in range(len(sequence))]


if sys.version_info < (3, 6):
    OrderedDict = dict
else:
    from collections import OrderedDict
unique_ever_seen = OrderedDict.fromkeys
del OrderedDict, sys
