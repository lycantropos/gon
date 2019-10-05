from gon.base import Point
from gon.hints import Scalar
from . import parallelogram


def signed_length(first_start: Point,
                  first_end: Point,
                  second_start: Point,
                  second_end: Point) -> Scalar:
    """
    Calculates signed length of projection of one vector onto another.
    """
    return parallelogram.signed_area(first_start, first_end,
                                     Point(-second_start.y, second_start.x),
                                     Point(-second_end.y, second_end.x))
