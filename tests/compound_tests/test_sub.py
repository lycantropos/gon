from typing import Tuple

from hypothesis import given

from gon.compound import Compound
from gon.degenerate import EMPTY
from tests.utils import (are_compounds_equivalent,
                         implication)
from . import strategies


@given(strategies.compounds_pairs)
def test_basic(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound - right_compound

    assert isinstance(result, Compound)


@given(strategies.compounds)
def test_self_inverse(compound: Compound) -> None:
    result = compound - compound

    assert result is EMPTY


@given(strategies.empty_compounds_with_compounds)
def test_left_absorbing_element(empty_compound_with_compound
                                : Tuple[Compound, Compound]) -> None:
    empty_compound, compound = empty_compound_with_compound

    result = empty_compound - compound

    assert result is EMPTY


@given(strategies.empty_compounds_with_compounds)
def test_right_neutral_element(empty_compound_with_compound
                               : Tuple[Compound, Compound]) -> None:
    empty_compound, compound = empty_compound_with_compound

    result = compound - empty_compound

    assert result == compound


@given(strategies.compounds_pairs)
def test_equivalents(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound - right_compound

    assert implication(left_compound.disjoint(right_compound),
                       are_compounds_equivalent(result, left_compound))


@given(strategies.rational_compounds_pairs)
def test_connection_with_subset_relation(compounds_pair
                                         : Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound - right_compound

    assert result <= left_compound
