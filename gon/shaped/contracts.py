from bentley_ottmann.base import edges_intersect
from robust import cocircular

from gon.angular import Orientation
from gon.base import (Point,
                      _point_to_real_tuple)
from .hints import Vertices
from .utils import to_angles


def vertices_forms_convex_polygon(vertices: Vertices) -> bool:
    if len(vertices) == 3:
        return True
    orientations = (angle.orientation for angle in to_angles(vertices))
    base_orientation = next(orientations)
    # orientation change means
    # that internal angle is greater than 180 degrees
    return all(orientation == base_orientation for orientation in orientations)


def vertices_forms_strict_polygon(vertices: Vertices) -> bool:
    return all(angle.orientation is not Orientation.COLLINEAR
               for angle in to_angles(vertices))


def self_intersects(vertices: Vertices) -> bool:
    return edges_intersect([vertex.as_tuple() for vertex in vertices])


def is_point_inside_circumcircle(first_vertex: Point,
                                 second_vertex: Point,
                                 third_vertex: Point,
                                 point: Point) -> bool:
    return cocircular.determinant(_point_to_real_tuple(first_vertex),
                                  _point_to_real_tuple(second_vertex),
                                  _point_to_real_tuple(third_vertex),
                                  _point_to_real_tuple(point)) > 0
