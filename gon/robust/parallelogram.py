from gon.base import Point
from gon.hints import Scalar
from . import bounds
from .utils import (sum_expansions,
                    to_cross_product,
                    two_diff_tail,
                    two_product,
                    two_two_diff)


def signed_area(first_start: Point,
                first_end: Point,
                second_start: Point,
                second_end: Point) -> Scalar:
    """
    Calculates signed area of parallelogram built on segments' vectors.
    """
    minuend = ((first_end.x - first_start.x)
               * (second_end.y - second_start.y))
    subtrahend = ((first_end.y - first_start.y)
                  * (second_end.x - second_start.x))
    result = minuend - subtrahend

    if minuend > 0:
        if subtrahend <= 0:
            return result
        else:
            upper_bound = minuend + subtrahend
    elif minuend < 0.0:
        if subtrahend >= 0.0:
            return result
        else:
            upper_bound = -minuend - subtrahend
    else:
        return result

    error_bound = bounds.to_signed_measure_first_error(upper_bound)
    if result >= error_bound or -result >= error_bound:
        return result

    return _adjusted_signed_area(first_start, first_end,
                                 second_start, second_end,
                                 upper_bound)


def _adjusted_signed_area(first_start: Point,
                          first_end: Point,
                          second_start: Point,
                          second_end: Point,
                          upper_bound: Scalar) -> Scalar:
    minuend_multiplier_x = first_end.x - first_start.x
    minuend_multiplier_y = second_end.y - second_start.y
    subtrahend_multiplier_x = second_end.x - second_start.x
    subtrahend_multiplier_y = first_end.y - first_start.y

    minuend, minuend_tail = two_product(minuend_multiplier_x,
                                        minuend_multiplier_y)
    subtrahend, subtrahend_tail = two_product(subtrahend_multiplier_y,
                                              subtrahend_multiplier_x)

    result_expansion = two_two_diff(minuend, minuend_tail,
                                    subtrahend, subtrahend_tail)
    result = sum(result_expansion)
    error_bound = bounds.to_signed_measure_second_error(upper_bound)
    if result >= error_bound or -result >= error_bound:
        return result

    minuend_multiplier_x_tail = two_diff_tail(first_end.x, first_start.x,
                                              minuend_multiplier_x)
    subtrahend_multiplier_x_tail = two_diff_tail(second_end.x, second_start.x,
                                                 subtrahend_multiplier_x)
    subtrahend_multiplier_y_tail = two_diff_tail(first_end.y, first_start.y,
                                                 subtrahend_multiplier_y)
    minuend_multiplier_y_tail = two_diff_tail(second_end.y, second_start.y,
                                              minuend_multiplier_y)
    if (not minuend_multiplier_x_tail
            and not minuend_multiplier_y_tail
            and not subtrahend_multiplier_x_tail
            and not subtrahend_multiplier_y_tail):
        return result

    error_bound = (bounds.to_signed_measure_third_error(upper_bound)
                   + bounds.to_determinant_error(result))
    result += ((minuend_multiplier_x * minuend_multiplier_y_tail
                + minuend_multiplier_y * minuend_multiplier_x_tail)
               - (subtrahend_multiplier_y * subtrahend_multiplier_x_tail
                  + subtrahend_multiplier_x * subtrahend_multiplier_y_tail))
    if result >= error_bound or -result >= error_bound:
        return result

    result_expansion = sum_expansions(
            result_expansion, to_cross_product(minuend_multiplier_x_tail,
                                               minuend_multiplier_y,
                                               subtrahend_multiplier_x,
                                               subtrahend_multiplier_y_tail))
    result_expansion = sum_expansions(
            result_expansion, to_cross_product(minuend_multiplier_x,
                                               minuend_multiplier_y_tail,
                                               subtrahend_multiplier_x_tail,
                                               subtrahend_multiplier_y))
    result_expansion = sum_expansions(
            result_expansion, to_cross_product(minuend_multiplier_x_tail,
                                               minuend_multiplier_y_tail,
                                               subtrahend_multiplier_x_tail,
                                               subtrahend_multiplier_y_tail))
    return result_expansion[-1]
