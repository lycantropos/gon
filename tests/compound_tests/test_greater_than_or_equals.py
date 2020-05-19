from typing import Tuple

from hypothesis import given

from gon.shaped import Compound
from tests.utils import (equivalence,
                         implication)
from . import strategies


@given(strategies.compounds)
def test_reflexivity(compound: Compound) -> None:
    assert compound >= compound


@given(strategies.compounds_pairs)
def test_antisymmetry(compounds_pair: Tuple[Compound, Compound]) -> None:
    first_compound, second_compound = compounds_pair

    assert equivalence(first_compound >= second_compound >= first_compound,
                       first_compound == second_compound)


@given(strategies.compounds_triplets)
def test_transitivity(compounds_triplet: Tuple[Compound, Compound, Compound]
                      ) -> None:
    first_compound, second_compound, third_compound = compounds_triplet

    assert implication(first_compound >= second_compound >= third_compound,
                       first_compound >= third_compound)


@given(strategies.compounds_pairs)
def test_connection_with_greater_than(compounds_pair: Tuple[Compound, Compound]
                                      ) -> None:
    first_compound, second_compound = compounds_pair

    assert implication(first_compound > second_compound,
                       first_compound >= second_compound)


@given(strategies.compounds_pairs)
def test_connection_with_lower_than_or_equals(compounds_pair: Tuple[Compound,
                                                                    Compound]
                                              ) -> None:
    first_compound, second_compound = compounds_pair

    assert equivalence(first_compound >= second_compound,
                       second_compound <= first_compound)
