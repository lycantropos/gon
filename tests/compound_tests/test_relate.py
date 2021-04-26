from typing import Tuple

from ground.base import Relation
from hypothesis import given

from gon.base import Compound
from . import strategies


@given(strategies.compounds_pairs)
def test_basic(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound.relate(right_compound)

    assert isinstance(result, Relation)


@given(strategies.empty_compounds)
def test_empty_self(compound: Compound) -> None:
    assert compound.relate(compound) is Relation.DISJOINT


@given(strategies.non_empty_compounds)
def test_non_empty_self(compound: Compound) -> None:
    assert compound.relate(compound) is Relation.EQUAL


@given(strategies.compounds_pairs)
def test_complement(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound.relate(right_compound)

    assert result.complement is right_compound.relate(left_compound)
