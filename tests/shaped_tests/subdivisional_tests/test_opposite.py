from hypothesis import given

from gon.shaped.subdivisional import QuadEdge
from . import strategies


@given(strategies.quad_edges)
def test_basic(edge: QuadEdge) -> None:
    assert isinstance(edge.opposite, QuadEdge)
    assert edge.opposite != edge


@given(strategies.quad_edges)
def test_endpoints(edge: QuadEdge) -> None:
    assert edge.opposite.start == edge.end
    assert edge.opposite.end == edge.start


@given(strategies.quad_edges)
def test_involution(edge: QuadEdge) -> None:
    assert edge.opposite.opposite == edge


@given(strategies.quad_edges)
def test_connection_with_rotated(edge: QuadEdge) -> None:
    assert edge.opposite == edge.rotated.rotated
