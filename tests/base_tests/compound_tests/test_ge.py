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
    first, second = compounds_pair

    assert equivalence(first >= second >= first, first == second)


@given(strategies.compounds_triplets)
def test_transitivity(compounds_triplet: Tuple[Compound, Compound, Compound]
                      ) -> None:
    first, second, third = compounds_triplet

    assert implication(first >= second >= third, first >= third)


@given(strategies.compounds_pairs)
def test_equivalents(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first >= second

    assert equivalence(result, second <= first)
    assert equivalence(result, first > second or first == second)
    assert equivalence(result, second < first or first == second)
