from typing import Sequence

import pytest
from hypothesis import given

from gon.base import Point
from gon.shaped import Polygon
from tests import strategies


@given(strategies.invalid_vertices)
def test_invalid_vertices(vertices: Sequence[Point]) -> None:
    with pytest.raises(ValueError):
        Polygon(vertices)
