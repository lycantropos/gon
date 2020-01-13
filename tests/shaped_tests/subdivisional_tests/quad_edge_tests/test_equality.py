from typing import (Any,
                    Tuple)

from hypothesis import given

from gon.shaped.subdivisional import QuadEdge
from tests.utils import implication
from . import strategies


@given(strategies.quad_edges)
def test_reflexivity(quad_edge: QuadEdge) -> None:
    assert quad_edge == quad_edge


@given(strategies.quad_edges_pairs)
def test_symmetry(quad_edges_pair: Tuple[QuadEdge, QuadEdge]) -> None:
    left_quad_edge, right_quad_edge = quad_edges_pair

    assert implication(left_quad_edge == right_quad_edge,
                       right_quad_edge == left_quad_edge)


@given(strategies.quad_edges_triplets)
def test_transitivity(quad_edges_triplet: Tuple[QuadEdge, QuadEdge, QuadEdge]
                      ) -> None:
    left_quad_edge, mid_quad_edge, right_quad_edge = quad_edges_triplet

    assert implication(left_quad_edge == mid_quad_edge == right_quad_edge,
                       left_quad_edge == right_quad_edge)


@given(strategies.quad_edges, strategies.non_quad_edges)
def test_non_quad_edge_argument(quad_edge: QuadEdge,
                                non_quad_edge: Any) -> None:
    assert quad_edge != non_quad_edge
