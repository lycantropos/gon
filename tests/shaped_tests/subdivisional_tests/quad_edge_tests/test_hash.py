from hypothesis import given

from gon.shaped.subdivisional import QuadEdge
from tests.utils import implication
from . import strategies


@given(strategies.quad_edges)
def test_basic(quad_edge: QuadEdge) -> None:
    result = hash(quad_edge)

    assert isinstance(result, int)


@given(strategies.quad_edges)
def test_determinism(quad_edge: QuadEdge) -> None:
    result = hash(quad_edge)

    assert result == hash(quad_edge)


@given(strategies.quad_edges, strategies.quad_edges)
def test_connection_with_equality(left_quad_edge: QuadEdge,
                                  right_quad_edge: QuadEdge) -> None:
    assert implication(left_quad_edge == right_quad_edge,
                       hash(left_quad_edge) == hash(right_quad_edge))
