from hypothesis import given

from gon.base import Empty
from tests.utils import implication
from . import strategies


@given(strategies.empty_geometries, strategies.empty_geometries)
def test_singularity(first: Empty, third: Empty) -> None:
    assert first is third


@given(strategies.empty_geometries)
def test_reflexivity(empty: Empty) -> None:
    assert empty == empty


@given(strategies.empty_geometries, strategies.empty_geometries)
def test_symmetry(first: Empty, third: Empty) -> None:
    assert implication(first == third,
                       third == first)


@given(strategies.empty_geometries, strategies.empty_geometries,
       strategies.empty_geometries)
def test_transitivity(first: Empty, second: Empty, third: Empty
                      ) -> None:
    assert implication(first == second == third,
                       first == third)
