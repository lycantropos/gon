from itertools import product
from typing import Tuple

from hypothesis import given

from gon.base import (EMPTY,
                      Mix,
                      Relation)
from tests.utils import (equivalence,
                         implication,
                         mix_to_components,
                         mix_to_polygons,
                         mix_to_segments)
from . import strategies


@given(strategies.mixes)
def test_components(mix: Mix) -> None:
    assert all(component is EMPTY
               or mix.relate(component) is Relation.COMPONENT
               for component in mix_to_components(mix))
    assert all(mix.relate(segment) is Relation.COMPONENT
               for segment in mix_to_segments(mix))
    assert all(mix.relate(polygon) is Relation.COMPONENT
               for polygon in mix_to_polygons(mix))


@given(strategies.mixes_pairs)
def test_mixes_relations(mixes_pair: Tuple[Mix, Mix]) -> None:
    first, second = mixes_pair

    result = first.relate(second)

    assert equivalence(result is Relation.DISJOINT,
                       all(first_component.relate(second_component)
                           is Relation.DISJOINT
                           for first_component, second_component in product(
                               mix_to_components(first),
                               mix_to_components(second))))
    assert implication(result is Relation.OVERLAP,
                       first.shaped is second.shaped is EMPTY
                       or first.shaped is not EMPTY
                       and second.shaped is not EMPTY)
    assert implication(result in (Relation.COVER, Relation.ENCLOSES),
                       second.shaped is not EMPTY)
    assert implication(result is Relation.COMPOSITE,
                       all(component is EMPTY
                           or second.relate(component) is Relation.COMPONENT
                           for component in mix_to_components(first)))
    assert equivalence(result is Relation.EQUAL,
                       all(first_component is second_component is EMPTY
                           or (first_component.relate(second_component)
                               is Relation.EQUAL)
                           for first_component, second_component in zip(
                               mix_to_components(first),
                               mix_to_components(second))))
    assert implication(result is Relation.COMPONENT,
                       all(component is EMPTY
                           or first.relate(component) is Relation.COMPONENT
                           for component in mix_to_components(second)))
    assert implication(result in (Relation.ENCLOSED, Relation.WITHIN),
                       first.shaped is not EMPTY)
