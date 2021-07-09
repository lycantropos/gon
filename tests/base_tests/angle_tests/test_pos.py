from hypothesis import given

from gon.base import Angle
from . import strategies


@given(strategies.angles)
def test_basic(angle: Angle) -> None:
    result = +angle

    assert isinstance(result, Angle)


@given(strategies.angles)
def test_identity(angle: Angle) -> None:
    result = +angle

    assert result == angle
