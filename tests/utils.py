from functools import partial
from itertools import repeat
from typing import (Callable,
                    Hashable,
                    Iterable,
                    Tuple)

from hypothesis import strategies
from hypothesis.strategies import SearchStrategy
from lz.functional import (cleave,
                           compose,
                           pack)
from lz.hints import (Domain,
                      Map,
                      Range)
from lz.replication import replicator

from gon.hints import Coordinate
from gon.point import Point
from gon.segment import (Segment)

Strategy = SearchStrategy


def equivalence(left_statement: bool, right_statement: bool) -> bool:
    return left_statement is right_statement


def implication(antecedent: bool, consequent: bool) -> bool:
    return not antecedent or consequent


def unique_everseen(iterable: Iterable[Domain],
                    *,
                    key: Map[Domain, Hashable] = None) -> Iterable[Domain]:
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in iterable:
            if element not in seen:
                seen_add(element)
                yield element
    else:
        for element in iterable:
            value = key(element)
            if value not in seen:
                seen_add(value)
                yield element


triplicate = replicator(3)


def to_tuples(elements: Strategy[Domain],
              *,
              size: int) -> Strategy[Tuple[Domain, ...]]:
    return strategies.tuples(*repeat(elements,
                                     times=size))


to_pairs = partial(to_tuples,
                   size=2)
to_triplets = partial(to_tuples,
                      size=3)


def cleave_in_tuples(*functions: Callable[[Strategy[Domain]], Strategy[Range]]
                     ) -> Callable[[Strategy[Domain]],
                                   Strategy[Tuple[Range, ...]]]:
    return compose(pack(strategies.tuples), cleave(*functions))


def scale_segment(segment: Segment,
                  *,
                  scale: Coordinate) -> Segment:
    return Segment(segment.start,
                   Point(segment.start.x
                         + scale * (segment.end.x - segment.start.x),
                         segment.start.y
                         + scale * (segment.end.y - segment.start.y)))


def reflect_segment(segment: Segment) -> Segment:
    return scale_segment(segment,
                         scale=-1)


def reverse_segment(segment: Segment) -> Segment:
    return Segment(segment.end, segment.start)
