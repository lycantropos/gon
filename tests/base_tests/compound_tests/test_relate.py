from typing import Tuple

from hypothesis import given

from gon.base import (Compound,
                      Relation)
from . import strategies


@given(strategies.compounds_pairs)
def test_basic(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first.relate(second)

    assert isinstance(result, Relation)


@given(strategies.empty_compounds)
def test_empty_self(compound: Compound) -> None:
    assert compound.relate(compound) is Relation.DISJOINT


@given(strategies.non_empty_compounds)
def test_non_empty_self(compound: Compound) -> None:
    assert compound.relate(compound) is Relation.EQUAL


@given(strategies.compounds_pairs)
def test_complement(compounds_pair: Tuple[Compound, Compound]) -> None:
    first, second = compounds_pair

    result = first.relate(second)

    assert result.complement is second.relate(first)
