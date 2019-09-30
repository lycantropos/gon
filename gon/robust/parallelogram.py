from gon.base import Point
from gon.hints import Scalar
from . import bounds
from .utils import (Expansion,
                    sum_expansions,
                    two_diff_tail,
                    two_product,
                    two_two_diff)


def signed_area(vertex: Point,
                first_ray_point: Point,
                second_ray_point: Point) -> Scalar:
    """
    Calculates signed area of parallelogram
    built on segments of rays with common vertex.
    """
    minuend = ((first_ray_point.x - vertex.x)
               * (second_ray_point.y - vertex.y))
    subtrahend = ((first_ray_point.y - vertex.y)
                  * (second_ray_point.x - vertex.x))
    result = minuend - subtrahend

    if minuend > 0:
        if subtrahend <= 0:
            return result
        else:
            moduli_sum = minuend + subtrahend
    elif minuend < 0.0:
        if subtrahend >= 0.0:
            return result
        else:
            moduli_sum = -minuend - subtrahend
    else:
        return result

    error_bound = bounds.to_counterclockwise_error_a(moduli_sum)
    if result >= error_bound or -result >= error_bound:
        return result

    return _adjusted_signed_area(vertex, first_ray_point, second_ray_point,
                                 moduli_sum)


def _adjusted_signed_area(vertex: Point,
                          first_ray_point: Point,
                          second_ray_point: Point,
                          moduli_sum: Scalar) -> Scalar:
    minuend_multiplier_x = first_ray_point.x - vertex.x
    minuend_multiplier_y = second_ray_point.y - vertex.y
    subtrahend_multiplier_x = second_ray_point.x - vertex.x
    subtrahend_multiplier_y = first_ray_point.y - vertex.y

    minuend, minuend_tail = two_product(minuend_multiplier_x,
                                        minuend_multiplier_y)
    subtrahend, subtrahend_tail = two_product(subtrahend_multiplier_y,
                                              subtrahend_multiplier_x)

    result_expansion = two_two_diff(minuend, minuend_tail,
                                    subtrahend, subtrahend_tail)
    result = sum(result_expansion)
    error_bound = bounds.to_counterclockwise_error_b(moduli_sum)
    if (result >= error_bound) or (-result >= error_bound):
        return result

    minuend_multiplier_x_tail = two_diff_tail(first_ray_point.x, vertex.x,
                                              minuend_multiplier_x)
    subtrahend_multiplier_x_tail = two_diff_tail(second_ray_point.x, vertex.x,
                                                 subtrahend_multiplier_x)
    subtrahend_multiplier_y_tail = two_diff_tail(first_ray_point.y, vertex.y,
                                                 subtrahend_multiplier_y)
    minuend_multiplier_y_tail = two_diff_tail(second_ray_point.y, vertex.y,
                                              minuend_multiplier_y)
    if (not minuend_multiplier_x_tail
            and not minuend_multiplier_y_tail
            and not subtrahend_multiplier_x_tail
            and not subtrahend_multiplier_y_tail):
        return result

    error_bound = (bounds.to_counterclockwise_error_c(moduli_sum)
                   + bounds.to_determinant_error(result))
    result += ((minuend_multiplier_x * minuend_multiplier_y_tail
                + minuend_multiplier_y * minuend_multiplier_x_tail)
               - (subtrahend_multiplier_y * subtrahend_multiplier_x_tail
                  + subtrahend_multiplier_x * subtrahend_multiplier_y_tail))
    if (result >= error_bound) or (-result >= error_bound):
        return result

    result_expansion = sum_expansions(
            result_expansion, _to_cross_product(minuend_multiplier_x_tail,
                                                minuend_multiplier_y,
                                                subtrahend_multiplier_x,
                                                subtrahend_multiplier_y_tail))
    result_expansion = sum_expansions(
            result_expansion, _to_cross_product(minuend_multiplier_x,
                                                minuend_multiplier_y_tail,
                                                subtrahend_multiplier_x_tail,
                                                subtrahend_multiplier_y))
    result_expansion = sum_expansions(
            result_expansion, _to_cross_product(minuend_multiplier_x_tail,
                                                minuend_multiplier_y_tail,
                                                subtrahend_multiplier_x_tail,
                                                subtrahend_multiplier_y_tail))
    return result_expansion[-1]


def _to_cross_product(minuend_multiplier_x: Scalar,
                      minuend_multiplier_y: Scalar,
                      subtrahend_multiplier_x: Scalar,
                      subtrahend_multiplier_y: Scalar) -> Expansion:
    minuend, minuend_tail = two_product(minuend_multiplier_x,
                                        minuend_multiplier_y)
    subtrahend, subtrahend_tail = two_product(subtrahend_multiplier_y,
                                              subtrahend_multiplier_x)
    return two_two_diff(minuend, minuend_tail, subtrahend, subtrahend_tail)
