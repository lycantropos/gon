from typing import Tuple

from hypothesis import given

from gon.base import (Compound, EMPTY)
from tests.utils import (are_compounds_equivalent,
                         equivalence,
                         not_raises)
from . import strategies


@given(strategies.compounds_pairs)
def test_basic(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first & second

    assert isinstance(result, Compound)


@given(strategies.compounds_pairs)
def test_validity(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first & second

    with not_raises(ValueError):
        result.validate()


@given(strategies.compounds)
def test_idempotence(compound: Compound) -> None:
    assert are_compounds_equivalent(compound & compound, compound)


@given(strategies.empty_compounds_with_compounds)
def test_first(empty_compound_with_compound
               : Tuple[Compound, Compound]) -> None:
    empty_compound, compound = empty_compound_with_compound

    result = empty_compound & compound

    assert result is EMPTY


@given(strategies.empty_compounds_with_compounds)
def test_third(empty_compound_with_compound
               : Tuple[Compound, Compound]) -> None:
    empty_compound, compound = empty_compound_with_compound

    result = compound & empty_compound

    assert result is EMPTY


@given(strategies.compounds_pairs)
def test_absorption_identity(compounds_pair: Tuple[Compound, Compound]
                             ) -> None:
    first, second = compounds_pair

    result = first & (first | second)

    assert are_compounds_equivalent(result, first)


@given(strategies.compounds_pairs)
def test_commutativity(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first & second

    assert result == second & first


@given(strategies.compounds_triplets)
def test_associativity(compounds_triplet: Tuple[Compound, Compound, Compound]
                       ) -> None:
    first, second, third = compounds_triplet

    result = (first & second) & third

    assert are_compounds_equivalent(
            result, first & (second & third))


@given(strategies.compounds_triplets)
def test_distribution_over_union(compounds_triplet
                                 : Tuple[Compound, Compound, Compound]
                                 ) -> None:
    first, second, third = compounds_triplet

    result = first & (second | third)

    assert are_compounds_equivalent(result,
                                    (first & second)
                                    | (first & third))


@given(strategies.compounds_pairs)
def test_connection_with_disjoint(compounds_pair: Tuple[Compound, Compound]
                                  ) -> None:
    first, second = compounds_pair

    result = first & second

    assert equivalence(first.disjoint(second), result is EMPTY)


@given(strategies.compounds_pairs)
def test_connection_with_subset_relation(compounds_pair
                                         : Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first & second

    assert result <= first and result <= second
