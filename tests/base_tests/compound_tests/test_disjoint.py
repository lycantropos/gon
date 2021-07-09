from typing import Tuple

from hypothesis import given

from gon.base import (Compound, EMPTY)
from tests.utils import equivalence
from . import strategies


@given(strategies.compounds_pairs)
def test_basic(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first.disjoint(second)

    assert isinstance(result, bool)


@given(strategies.compounds)
def test_reflexivity_criteria(compound: Compound) -> None:
    assert equivalence(compound.disjoint(compound),
                       compound is EMPTY)


@given(strategies.compounds_pairs)
def test_symmetry(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    assert equivalence(first.disjoint(second), second.disjoint(first))
