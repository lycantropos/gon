from typing import Tuple

from hypothesis import given

from gon.base import Compound
from tests.utils import (are_compounds_equivalent,
                         not_raises)
from . import strategies


@given(strategies.compounds_pairs)
def test_basic(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound | right_compound

    assert isinstance(result, Compound)


@given(strategies.compounds_pairs)
def test_validity(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound | right_compound

    with not_raises(ValueError):
        result.validate()


@given(strategies.compounds)
def test_idempotence(compound: Compound) -> None:
    result = compound | compound

    assert are_compounds_equivalent(result, compound)


@given(strategies.empty_compounds_with_compounds)
def test_left_neutral_element(empty_compound_with_compound
                              : Tuple[Compound, Compound]) -> None:
    empty_compound, compound = empty_compound_with_compound

    result = empty_compound | compound

    assert result == compound


@given(strategies.empty_compounds_with_compounds)
def test_right_neutral_element(empty_compound_with_compound
                               : Tuple[Compound, Compound]) -> None:
    empty_compound, compound = empty_compound_with_compound

    result = compound | empty_compound

    assert result == compound


@given(strategies.compounds_pairs)
def test_absorption_identity(compounds_pair: Tuple[Compound, Compound]
                             ) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound | (left_compound & right_compound)

    assert are_compounds_equivalent(result, left_compound)


@given(strategies.compounds_pairs)
def test_commutativity(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound | right_compound

    assert result == right_compound | left_compound


@given(strategies.compounds_triplets)
def test_associativity(compounds_triplet: Tuple[Compound, Compound, Compound]
                       ) -> None:
    left_compound, mid_compound, right_compound = compounds_triplet

    result = (left_compound | mid_compound) | right_compound

    assert are_compounds_equivalent(
            result, left_compound | (mid_compound | right_compound))


@given(strategies.compounds_triplets)
def test_distribution_over_intersection(compounds_triplet
                                        : Tuple[Compound, Compound, Compound]
                                        ) -> None:
    left_compound, mid_compound, right_compound = compounds_triplet

    result = left_compound | (mid_compound & right_compound)

    assert are_compounds_equivalent(result,
                                    (left_compound | mid_compound)
                                    & (left_compound | right_compound))


@given(strategies.compounds_pairs)
def test_equivalents(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound | right_compound

    assert are_compounds_equivalent(result,
                                    (left_compound ^ right_compound)
                                    ^ (left_compound & right_compound))


@given(strategies.compounds_pairs)
def test_connection_with_subset_relation(compounds_pair
                                         : Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound | right_compound

    assert left_compound <= result and right_compound <= result
