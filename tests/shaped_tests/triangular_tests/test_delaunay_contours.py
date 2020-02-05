from collections import abc
from typing import Sequence

from hypothesis import given

from gon.base import Point
from gon.shaped.contracts import is_point_inside_circumcircle
from gon.shaped.hints import Contour
from gon.shaped.triangular import delaunay_contours
from gon.shaped.utils import (to_convex_hull,
                              to_edges)
from tests.utils import to_boundary
from . import strategies


@given(strategies.points_lists)
def test_basic(points: Sequence[Point]) -> None:
    result = delaunay_contours(points)

    assert isinstance(result, abc.Sequence)
    assert all(isinstance(element, abc.Sequence)
               for element in result)


@given(strategies.points_lists)
def test_sizes(points: Sequence[Point]) -> None:
    result = delaunay_contours(points)

    assert 0 < len(result) <= (2 * (len(points) - 1)
                               - len(to_convex_hull(points)))
    assert all(len(element) == 3
               for element in result)


@given(strategies.points_lists)
def test_delaunay_criterion(points: Sequence[Point]) -> None:
    result = delaunay_contours(points)

    assert all(not any(is_point_inside_circumcircle(*triangle_contour, point)
                       for triangle_contour in result)
               for point in points)


@given(strategies.points_lists)
def test_boundary(points: Sequence[Point]) -> None:
    result = delaunay_contours(points)

    assert to_boundary(result) == set(to_edges(to_convex_hull(points)))


@given(strategies.triangular_contours)
def test_base_case(contour: Contour) -> None:
    result = delaunay_contours(contour)

    assert len(result) == 1
    assert is_contour_in_triangulation(contour, result)


@given(strategies.non_triangle_points_lists)
def test_step(next_points: Sequence[Point]) -> None:
    points = next_points[:-1]
    next_point = next_points[-1]

    result = delaunay_contours(points)
    next_result = delaunay_contours(next_points)

    assert len(result) <= len(next_result) + 2
    assert all(not is_contour_in_triangulation(contour, next_result)
               for contour in result
               if is_point_inside_circumcircle(*contour, next_point))


def is_contour_in_triangulation(contour: Contour,
                                triangulation: Sequence[Contour]) -> bool:
    return frozenset(contour) in map(frozenset, triangulation)
