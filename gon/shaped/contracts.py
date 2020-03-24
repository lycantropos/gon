from bentley_ottmann.planar import edges_intersect
from robust import cocircular

from gon.angular import Orientation
from gon.base import Point
from .hints import Contour
from .utils import to_orientations


def contour_forms_convex_polygon(contour: Contour) -> bool:
    if len(contour) == 3:
        return True
    orientations = iter(to_orientations(contour))
    base_orientation = next(orientations)
    # orientation change means
    # that internal angle is greater than 180 degrees
    return all(orientation is base_orientation for orientation in orientations)


def contour_forms_strict_polygon(contour: Contour) -> bool:
    return all(orientation is not Orientation.COLLINEAR
               for orientation in to_orientations(contour))


def self_intersects(contour: Contour) -> bool:
    return edges_intersect([vertex.as_tuple() for vertex in contour])


def is_point_inside_circumcircle(first_vertex: Point,
                                 second_vertex: Point,
                                 third_vertex: Point,
                                 point: Point) -> bool:
    return cocircular.determinant(first_vertex.as_tuple(),
                                  second_vertex.as_tuple(),
                                  third_vertex.as_tuple(),
                                  point.as_tuple()) > 0
