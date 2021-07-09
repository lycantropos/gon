import pytest
from hypothesis import given

from gon.base import Angle
from . import strategies


@given(strategies.angles)
def test_basic(angle: Angle) -> None:
    result = angle.validate()

    assert result is None


@given(strategies.invalid_angles)
def test_invalid_angle(angle: Angle) -> None:
    with pytest.raises(ValueError):
        angle.validate()
