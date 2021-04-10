from hypothesis import given

from gon.base import Compound
from . import strategies


@given(strategies.compounds)
def test_regularity(compound: Compound) -> None:
    assert compound not in compound
