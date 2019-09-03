from hypothesis import given

from gon.shaped.subdivisional import QuadEdge
from tests.utils import implication
from . import strategies


@given(strategies.quad_edges)
def test_reflexivity(quad_edge: QuadEdge) -> None:
    assert quad_edge == quad_edge


@given(strategies.quad_edges, strategies.quad_edges)
def test_symmetry(left_quad_edge: QuadEdge, right_quad_edge: QuadEdge) -> None:
    assert implication(left_quad_edge == right_quad_edge,
                       right_quad_edge == left_quad_edge)


@given(strategies.quad_edges, strategies.quad_edges, strategies.quad_edges)
def test_transitivity(left_quad_edge: QuadEdge,
                      mid_quad_edge: QuadEdge,
                      right_quad_edge: QuadEdge) -> None:
    assert implication(left_quad_edge == mid_quad_edge == right_quad_edge,
                       left_quad_edge == right_quad_edge)
