from typing import Tuple

from hypothesis import given

from gon.linear import (IntersectionKind,
                        Interval)
from tests.utils import (equivalence,
                         inverse_inclusion,
                         is_non_origin_point,
                         reflect_interval)
from . import strategies


@given(strategies.intervals)
def test_relationship_with_self(interval: Interval) -> None:
    assert interval.relationship_with(interval) is IntersectionKind.OVERLAP


@given(strategies.intervals)
def test_inversed_inclusion(interval: Interval) -> None:
    assert (interval.relationship_with(inverse_inclusion(interval))
            is IntersectionKind.OVERLAP)


@given(strategies.intervals_pairs)
def test_commutativity(intervals_pair: Tuple[Interval, Interval]) -> None:
    interval, other_interval = intervals_pair

    assert (interval.relationship_with(other_interval)
            is other_interval.relationship_with(interval))


@given(strategies.intervals_pairs)
def test_independence_from_ends_order(intervals_pair: Tuple[Interval, Interval]
                                      ) -> None:
    interval, other_interval = intervals_pair

    assert (interval.relationship_with(other_interval)
            is interval.reversed.relationship_with(other_interval))


@given(strategies.same_quadrant_intervals)
def test_same_quadrant_interval_reflection(interval: Interval) -> None:
    reflected_interval = reflect_interval(interval)

    one_of_endpoints_is_included_origin = (
            interval.start_inclusive
            and not is_non_origin_point(interval.start)
            or interval.end_inclusive
            and not is_non_origin_point(interval.end))

    assert equivalence(one_of_endpoints_is_included_origin,
                       interval.relationship_with(reflected_interval)
                       is IntersectionKind.CROSS)
    assert equivalence(not one_of_endpoints_is_included_origin,
                       interval.relationship_with(reflected_interval)
                       is IntersectionKind.NONE)
