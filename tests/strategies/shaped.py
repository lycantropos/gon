from hypothesis import strategies
from hypothesis_geometry import planar

from gon.linear import Contour
from gon.shaped import Polygon
from gon.shaped.utils import to_convex_hull
from .base import coordinates_strategies
from .factories import coordinates_to_contours
from .linear import (contours_with_repeated_points,
                     invalid_vertices_contours)


def to_invalid_polygon_with_hole(concave_contour: Contour) -> Polygon:
    return Polygon(concave_contour,
                   [Contour(to_convex_hull(concave_contour.vertices))])


invalid_contours = invalid_vertices_contours | contours_with_repeated_points
invalid_polygons = (
        strategies.builds(Polygon, invalid_contours)
        | strategies.builds(Polygon,
                            coordinates_strategies
                            .flatmap(coordinates_to_contours),
                            strategies.lists(invalid_contours,
                                             min_size=1))
        | (coordinates_strategies.flatmap(planar.concave_contours)
           .map(Contour.from_raw)
           .map(to_invalid_polygon_with_hole)))
