from bentley_ottmann.base import edges_intersect
from robust import cocircular

from gon.angular import Orientation
from gon.base import (Point,
                      _point_to_real_tuple)
from .hints import Contour
from .utils import to_angles


def contour_forms_convex_polygon(contour: Contour) -> bool:
    if len(contour) == 3:
        return True
    orientations = (angle.orientation for angle in to_angles(contour))
    base_orientation = next(orientations)
    # orientation change means
    # that internal angle is greater than 180 degrees
    return all(orientation is base_orientation for orientation in orientations)


def contour_forms_strict_polygon(contour: Contour) -> bool:
    return all(angle.orientation is not Orientation.COLLINEAR
               for angle in to_angles(contour))


def self_intersects(contour: Contour) -> bool:
    return edges_intersect([vertex.as_tuple() for vertex in contour])


def is_point_inside_circumcircle(first_vertex: Point,
                                 second_vertex: Point,
                                 third_vertex: Point,
                                 point: Point) -> bool:
    return cocircular.determinant(_point_to_real_tuple(first_vertex),
                                  _point_to_real_tuple(second_vertex),
                                  _point_to_real_tuple(third_vertex),
                                  _point_to_real_tuple(point)) > 0
