from itertools import product
from typing import Tuple

from hypothesis import given

from gon.base import (EMPTY,
                      Mix,
                      Relation)
from tests.utils import (equivalence,
                         implication,
                         mix_to_components)
from . import strategies


@given(strategies.mixes)
def test_components(mix: Mix) -> None:
    assert all(component is EMPTY
               or mix.relate(component) is Relation.COMPONENT
               for component in mix_to_components(mix))
    assert (mix.linear is EMPTY
            or all(mix.relate(segment) is Relation.COMPONENT
                   for segment in mix.linear.segments))
    assert (mix.shaped is EMPTY
            or all(mix.relate(polygon) is Relation.COMPONENT
                   for polygon in mix.shaped.polygons))


@given(strategies.mixes_pairs)
def test_mixes_relations(mixes_pair: Tuple[Mix, Mix]) -> None:
    left_mix, right_mix = mixes_pair

    result = left_mix.relate(right_mix)

    assert equivalence(result is Relation.DISJOINT,
                       all(left_component.relate(right_component)
                           is Relation.DISJOINT
                           for left_component, right_component in product(
                               mix_to_components(left_mix),
                               mix_to_components(right_mix))))
    assert implication(result is Relation.OVERLAP,
                       left_mix.shaped is right_mix.shaped is EMPTY
                       or left_mix.shaped is not EMPTY
                       and right_mix.shaped is not EMPTY)
    assert implication(result in (Relation.COVER, Relation.ENCLOSES),
                       right_mix.shaped is not EMPTY)
    assert implication(result is Relation.COMPOSITE,
                       all(component is EMPTY
                           or right_mix.relate(component) is Relation.COMPONENT
                           for component in mix_to_components(left_mix)))
    assert equivalence(result is Relation.EQUAL,
                       all(left_component is right_component is EMPTY
                           or (left_component.relate(right_component)
                               is Relation.EQUAL)
                           for left_component, right_component in zip(
                               mix_to_components(left_mix),
                               mix_to_components(right_mix))))
    assert implication(result is Relation.COMPONENT,
                       all(component is EMPTY
                           or left_mix.relate(component) is Relation.COMPONENT
                           for component in mix_to_components(right_mix)))
    assert implication(result in (Relation.ENCLOSED, Relation.WITHIN),
                       left_mix.shaped is not EMPTY)
