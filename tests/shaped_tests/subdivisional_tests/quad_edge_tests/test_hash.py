from typing import Tuple

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


@given(strategies.quad_edges_pairs)
def test_connection_with_equality(quad_edges_pair: Tuple[QuadEdge, QuadEdge]
                                  ) -> None:
    left_quad_edge, right_quad_edge = quad_edges_pair

    assert implication(left_quad_edge == right_quad_edge,
                       hash(left_quad_edge) == hash(right_quad_edge))
