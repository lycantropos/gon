from hypothesis import given

from gon.discrete import Multipoint
from . import strategies


@given(strategies.multipoints)
def test_points(multipoint: Multipoint) -> None:
    assert all(point in multipoint
               for point in multipoint.points)
