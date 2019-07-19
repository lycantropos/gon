from hypothesis import given

from gon.angular import Angle
from . import strategies


@given(strategies.angles)
def test_alternatives(angle: Angle) -> None:
    assert angle.is_acute ^ angle.is_right ^ angle.is_obtuse
