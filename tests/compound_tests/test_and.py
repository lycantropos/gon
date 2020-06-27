from typing import Tuple

from hypothesis import given

from gon.compound import (Compound,
                          Relation)
from gon.degenerate import EMPTY
from . import strategies


@given(strategies.compounds_pairs)
def test_basic(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound & right_compound

    assert isinstance(result, Compound)


@given(strategies.rational_compounds)
def test_idempotence(compound: Compound) -> None:
    result = compound & compound

    assert (compound is result is EMPTY
            or result.relate(compound) is Relation.EQUAL)


@given(strategies.empty_compounds_with_compounds)
def test_left_absorbing_element(empty_compound_with_compound
                                : Tuple[Compound, Compound]) -> None:
    empty_compound, compound = empty_compound_with_compound

    result = empty_compound & compound

    assert result is EMPTY


@given(strategies.empty_compounds_with_compounds)
def test_right_absorbing_element(empty_compound_with_compound
                                 : Tuple[Compound, Compound]) -> None:
    empty_compound, compound = empty_compound_with_compound

    result = compound & empty_compound

    assert result is EMPTY


@given(strategies.rational_compounds_pairs)
def test_absorption_identity(compounds_pair: Tuple[Compound, Compound]
                             ) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound & (left_compound | right_compound)

    assert (result is left_compound is EMPTY
            or result.relate(left_compound) is Relation.EQUAL)


@given(strategies.compounds_pairs)
def test_commutativity(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound & right_compound

    assert result == right_compound & left_compound


@given(strategies.compounds_triplets)
def test_associativity(compounds_triplet: Tuple[Compound, Compound, Compound]
                       ) -> None:
    left_compound, mid_compound, right_compound = compounds_triplet

    result = (left_compound & mid_compound) & right_compound

    assert result == left_compound & (mid_compound & right_compound)


@given(strategies.rational_compounds_pairs)
def test_connection_with_subset_relation(compounds_pair
                                         : Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound & right_compound

    assert result <= left_compound and result <= right_compound
