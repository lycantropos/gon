from hypothesis import given

from gon.shaped.subdivisional import QuadEdge
from tests.utils import edge_to_relatives_endpoints
from . import strategies


@given(strategies.quad_edges_with_neighbours)
def test_basic(quad_edge: QuadEdge) -> None:
    result = quad_edge.swap()

    assert result is None


@given(strategies.quad_edges_with_neighbours)
def test_single(quad_edge: QuadEdge) -> None:
    start_before = quad_edge.start

    quad_edge.swap()

    assert quad_edge.start != start_before


@given(strategies.quad_edges_with_neighbours)
def test_twice(quad_edge: QuadEdge) -> None:
    end_before = quad_edge.end

    quad_edge.swap()
    quad_edge.swap()

    assert quad_edge.start == end_before


@given(strategies.quad_edges_with_neighbours)
def test_fourfold(quad_edge: QuadEdge) -> None:
    start_before = quad_edge.start
    relatives_endpoints_before = edge_to_relatives_endpoints(quad_edge)

    for _ in range(4):
        quad_edge.swap()

    assert quad_edge.start == start_before
    assert edge_to_relatives_endpoints(quad_edge) == relatives_endpoints_before
