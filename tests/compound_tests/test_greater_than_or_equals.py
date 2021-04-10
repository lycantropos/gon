from typing import Tuple

from hypothesis import given

from gon.base import Compound
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
def test_equivalents(compounds_pair: Tuple[Compound, Compound]) -> None:
    first_compound, second_compound = compounds_pair

    result = first_compound >= second_compound

    assert equivalence(result, second_compound <= first_compound)
    assert equivalence(result,
                       first_compound > second_compound
                       or first_compound == second_compound)
    assert equivalence(result,
                       second_compound < first_compound
                       or first_compound == second_compound)
