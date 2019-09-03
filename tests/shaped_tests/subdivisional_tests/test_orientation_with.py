from typing import Tuple

from hypothesis import given

from gon.angular import Orientation
from gon.base import Point
from gon.shaped.subdivisional import QuadEdge
from tests.utils import equivalence
from . import strategies


@given(strategies.quad_edges_with_points)
def test_basic(edge_with_point: Tuple[QuadEdge, Point]) -> None:
    edge, point = edge_with_point

    assert isinstance(edge.orientation_with(point), Orientation)


@given(strategies.quad_edges_with_points)
def test_opposite(edge_with_point: Tuple[QuadEdge, Point]) -> None:
    edge, point = edge_with_point

    result = edge.opposite.orientation_with(point)

    assert equivalence(result is edge.orientation_with(point),
                       result is Orientation.COLLINEAR)


@given(strategies.quad_edges)
def test_endpoints(edge: QuadEdge) -> None:
    assert edge.orientation_with(edge.start) is Orientation.COLLINEAR
    assert edge.orientation_with(edge.end) is Orientation.COLLINEAR
