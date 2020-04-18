from typing import Tuple

from hypothesis import given
from orient.planar import Relation

from gon.compound import Compound
from tests.geometry_tests.compounds_tests import strategies


@given(strategies.compounds_pairs)
def test_basic(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound.relate(right_compound)

    assert isinstance(result, Relation)


@given(strategies.compounds)
def test_self(compound: Compound) -> None:
    assert compound.relate(compound) is Relation.EQUAL


@given(strategies.compounds_pairs)
def test_complement(compounds_pair: Tuple[Compound, Compound]) -> None:
    left_compound, right_compound = compounds_pair

    result = left_compound.relate(right_compound)

    assert result.complement is right_compound.relate(left_compound)
