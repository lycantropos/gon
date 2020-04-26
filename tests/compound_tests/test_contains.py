from hypothesis import given

from gon.compound import Compound
from . import strategies


@given(strategies.compounds)
def test_regularity(compound: Compound) -> None:
    assert compound not in compound
