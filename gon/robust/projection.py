from gon.base import Point
from gon.hints import Scalar
from . import bounds
from .utils import (Expansion,
                    sum_expansions,
                    two_diff_tail,
                    two_product,
                    two_two_sum)


def signed_length(vertex: Point,
                  first_ray_point: Point,
                  second_ray_point: Point) -> Scalar:
    """
    Calculates signed length of projection
    built for segments of rays with common vertex.
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

    return _adjusted_signed_length(vertex, first_ray_point, second_ray_point,
                                   moduli_sum)


def _adjusted_signed_length(vertex: Point,
                            first_ray_point: Point,
                            second_ray_point: Point,
                            moduli_sum: Scalar) -> Scalar:
    left_addend_first_multiplier = first_ray_point.x - vertex.x
    left_addend_second_multiplier = second_ray_point.x - vertex.x
    right_addend_first_multiplier = first_ray_point.y - vertex.y
    right_addend_second_multiplier = second_ray_point.y - vertex.y

    left_addend, left_addend_tail = two_product(left_addend_first_multiplier,
                                                left_addend_second_multiplier)
    right_addend, right_addend_tail = two_product(
            right_addend_first_multiplier, right_addend_second_multiplier)

    result_expansion = two_two_sum(left_addend, left_addend_tail,
                                   right_addend, right_addend_tail)
    result = sum(result_expansion)
    error_bound = bounds.to_counterclockwise_error_b(moduli_sum)
    if (result >= error_bound) or (-result >= error_bound):
        return result

    left_addend_first_multiplier_tail = two_diff_tail(
            first_ray_point.x, vertex.x, left_addend_first_multiplier)
    left_addend_second_multiplier_tail = two_diff_tail(
            second_ray_point.x, vertex.x, left_addend_second_multiplier)
    right_addend_first_multiplier_tail = two_diff_tail(
            first_ray_point.y, vertex.y, right_addend_first_multiplier)
    right_addend_second_multiplier_tail = two_diff_tail(
            second_ray_point.y, vertex.y, right_addend_second_multiplier)
    if (not left_addend_first_multiplier_tail
            and not left_addend_second_multiplier_tail
            and not right_addend_first_multiplier_tail
            and not right_addend_second_multiplier_tail):
        return result

    error_bound = (bounds.to_counterclockwise_error_c(moduli_sum)
                   + bounds.to_determinant_error(result))
    result += ((left_addend_first_multiplier
                * left_addend_second_multiplier_tail
                + left_addend_first_multiplier_tail
                * left_addend_second_multiplier)
               + (right_addend_first_multiplier
                  * right_addend_second_multiplier_tail
                  + right_addend_first_multiplier_tail
                  * right_addend_second_multiplier))
    if (result >= error_bound) or (-result >= error_bound):
        return result

    result_expansion = sum_expansions(
            result_expansion,
            _to_dot_product(left_addend_first_multiplier_tail,
                            left_addend_second_multiplier,
                            right_addend_first_multiplier_tail,
                            right_addend_second_multiplier))
    result_expansion = sum_expansions(
            result_expansion,
            _to_dot_product(left_addend_first_multiplier,
                            left_addend_second_multiplier_tail,
                            right_addend_first_multiplier,
                            right_addend_second_multiplier_tail))
    result_expansion = sum_expansions(
            result_expansion,
            _to_dot_product(left_addend_first_multiplier_tail,
                            left_addend_second_multiplier_tail,
                            right_addend_first_multiplier_tail,
                            right_addend_second_multiplier_tail))
    return result_expansion[-1]


def _to_dot_product(left_addend_first_multiplier: Scalar,
                    left_addend_second_multiplier: Scalar,
                    right_addend_first_multiplier: Scalar,
                    right_addend_second_multiplier: Scalar) -> Expansion:
    left_addend, left_addend_tail = two_product(left_addend_first_multiplier,
                                                left_addend_second_multiplier)
    right_addend, right_addend_tail = two_product(
            right_addend_first_multiplier, right_addend_second_multiplier)
    return two_two_sum(left_addend, left_addend_tail,
                       right_addend, right_addend_tail)
