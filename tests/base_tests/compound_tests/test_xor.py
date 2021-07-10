from typing import Tuple

from hypothesis import given

from gon.base import (EMPTY,
                      Compound,
                      Relation)
from tests.utils import (are_compounds_equivalent,
                         implication,
                         not_raises)
from . import strategies


@given(strategies.compounds_pairs)
def test_basic(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first ^ second

    assert isinstance(result, Compound)


@given(strategies.compounds_pairs)
def test_validity(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first ^ second

    with not_raises(ValueError):
        result.validate()


@given(strategies.compounds)
def test_self_inverse(compound: Compound) -> None:
    result = compound ^ compound

    assert result is EMPTY


@given(strategies.empty_compounds_with_compounds)
def test_first(empty_compound_with_compound
               : Tuple[Compound, Compound]) -> None:
    empty_compound, compound = empty_compound_with_compound

    result = empty_compound ^ compound

    assert result == compound


@given(strategies.empty_compounds_with_compounds)
def test_third(empty_compound_with_compound
               : Tuple[Compound, Compound]) -> None:
    empty_compound, compound = empty_compound_with_compound

    result = compound ^ empty_compound

    assert result == compound


@given(strategies.compounds_pairs)
def test_commutativity(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first ^ second

    assert result == second ^ first


@given(strategies.equidimensional_compounds_triplets)
def test_associativity(compounds_triplet: Tuple[Compound, Compound, Compound]
                       ) -> None:
    first, second, third = compounds_triplet

    result = (first ^ second) ^ third

    assert are_compounds_equivalent(
            result, first ^ (second ^ third))


@given(strategies.compounds_pairs)
def test_equivalents(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first ^ second

    assert are_compounds_equivalent(result,
                                    (first - second) | (second - first))
    assert are_compounds_equivalent(result,
                                    (first | second) - (first & second))


@given(strategies.compounds_pairs)
def test_connection_with_disjoint(compounds_pair: Tuple[Compound, Compound]
                                  ) -> None:
    first, second = compounds_pair

    result = first ^ second

    assert implication(first.disjoint(second),
                       result.relate(first | second) is Relation.EQUAL)
