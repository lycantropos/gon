from typing import Tuple

from hypothesis import given

from gon.compound import Compound
from gon.degenerate import EMPTY
from tests.utils import equivalence
from . import strategies


@given(strategies.compounds_pairs)
def test_basic(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound.disjoint(right_compound)

    assert isinstance(result, bool)


@given(strategies.compounds)
def test_reflexivity_criteria(compound: Compound) -> None:
    assert equivalence(compound.disjoint(compound),
                       compound is EMPTY)


@given(strategies.compounds_pairs)
def test_symmetry(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    assert equivalence(left_compound.disjoint(right_compound),
                       right_compound.disjoint(left_compound))
