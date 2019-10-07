from functools import reduce
from typing import (Iterable,
                    Tuple)

from gon.base import Point
from gon.hints import Scalar
from . import bounds
from .utils import (Expansion,
                    scale_expansion,
                    square,
                    sum_expansions,
                    to_cross_product,
                    two_diff_tail,
                    two_product,
                    two_two_diff,
                    two_two_sum)


def determinant(first_point: Point, second_point: Point,
                third_point: Point, fourth_point: Point) -> Scalar:
    """
    Calculates determinant of linear equations' system
    for checking if four points lie on the same circle.
    """
    first_dx, first_dy = (first_point.x - fourth_point.x,
                          first_point.y - fourth_point.y)
    second_dx, second_dy = (second_point.x - fourth_point.x,
                            second_point.y - fourth_point.y)
    third_dx, third_dy = (third_point.x - fourth_point.x,
                          third_point.y - fourth_point.y)

    first_squared_distance = first_dx * first_dx + first_dy * first_dy
    second_squared_distance = second_dx * second_dx + second_dy * second_dy
    third_squared_distance = third_dx * third_dx + third_dy * third_dy

    first_dx_second_dy = first_dx * second_dy
    first_dx_third_dy = first_dx * third_dy
    second_dx_first_dy = second_dx * first_dy
    second_dx_third_dy = second_dx * third_dy
    third_dx_first_dy = third_dx * first_dy
    third_dx_second_dy = third_dx * second_dy

    result = (first_squared_distance
              * (second_dx_third_dy - third_dx_second_dy)
              + second_squared_distance
              * (third_dx_first_dy - first_dx_third_dy)
              + third_squared_distance
              * (first_dx_second_dy - second_dx_first_dy))
    upper_bound = (first_squared_distance
                   * (abs(second_dx_third_dy) + abs(third_dx_second_dy))
                   + second_squared_distance
                   * (abs(third_dx_first_dy) + abs(first_dx_third_dy))
                   + third_squared_distance
                   * (abs(first_dx_second_dy) + abs(second_dx_first_dy)))
    error_bound = bounds.to_cocircular_first_error(upper_bound)
    if result > error_bound or -result > error_bound:
        return result
    return _adjusted_determinant(first_point, second_point,
                                 third_point, fourth_point,
                                 upper_bound)


def _adjusted_determinant(first_point: Point, second_point: Point,
                          third_point: Point, fourth_point: Point,
                          upper_bound: Scalar) -> Scalar:
    first_dx, first_dy = (first_point.x - fourth_point.x,
                          first_point.y - fourth_point.y)
    second_dx, second_dy = (second_point.x - fourth_point.x,
                            second_point.y - fourth_point.y)
    third_dx, third_dy = (third_point.x - fourth_point.x,
                          third_point.y - fourth_point.y)

    second_third_cross_product = to_cross_product(second_dx, third_dy,
                                                  third_dx, second_dy)
    third_first_cross_product = to_cross_product(third_dx, first_dy,
                                                 first_dx, third_dy)
    first_second_cross_product = to_cross_product(first_dx, second_dy,
                                                  second_dx, first_dy)
    result_expansion = sum_expansions(
            sum_expansions(
                    _multiply_by_squared_length(second_third_cross_product,
                                                first_dx, first_dy),
                    _multiply_by_squared_length(third_first_cross_product,
                                                second_dx, second_dy)),
            _multiply_by_squared_length(first_second_cross_product,
                                        third_dx, third_dy))
    result = sum(result_expansion)
    error_bound = bounds.to_cocircular_second_error(upper_bound)
    if result >= error_bound or -result >= error_bound:
        return result

    first_dx_tail = two_diff_tail(first_point.x, fourth_point.x, first_dx)
    first_dy_tail = two_diff_tail(first_point.y, fourth_point.y, first_dy)
    second_dx_tail = two_diff_tail(second_point.x, fourth_point.x, second_dx)
    second_dy_tail = two_diff_tail(second_point.y, fourth_point.y, second_dy)
    third_dx_tail = two_diff_tail(third_point.x, fourth_point.x, third_dx)
    third_dy_tail = two_diff_tail(third_point.y, fourth_point.y, third_dy)

    if (not first_dx_tail and not first_dy_tail
            and not second_dx_tail and not second_dy_tail
            and not third_dx_tail and not third_dy_tail):
        return result

    error_bound = (bounds.to_cocircular_third_error(upper_bound)
                   + bounds.to_determinant_error(result))
    result += (
            _to_addend(first_dx, first_dx_tail, first_dy, first_dy_tail,
                       second_dx, second_dx_tail, second_dy, second_dy_tail,
                       third_dx, third_dx_tail, third_dy, third_dy_tail)
            + _to_addend(second_dx, second_dx_tail, second_dy, second_dy_tail,
                         third_dx, third_dx_tail, third_dy, third_dy_tail,
                         first_dx, first_dx_tail, first_dy, first_dy_tail)
            + _to_addend(third_dx, third_dx_tail, third_dy, third_dy_tail,
                         first_dx, first_dx_tail, first_dy, first_dy_tail,
                         second_dx, second_dx_tail, second_dy, second_dy_tail))
    if result >= error_bound or -result >= error_bound:
        return result

    first_squared_length = (_to_squared_length(first_dx, first_dy)
                            if (second_dx_tail or second_dy_tail
                                or third_dx_tail or third_dy_tail)
                            else (0,) * 4)
    second_squared_length = (_to_squared_length(second_dx, second_dy)
                             if (first_dx_tail or first_dy_tail
                                 or third_dx_tail or third_dy_tail)
                             else (0,) * 4)
    third_squared_length = (_to_squared_length(third_dx, third_dy)
                            if (first_dx_tail or first_dy_tail
                                or second_dx_tail or second_dy_tail)
                            else (0,) * 4)

    if first_dx_tail:
        first_dx_tail_second_third_cross_product = scale_expansion(
                second_third_cross_product, first_dx_tail)
        result_expansion = sum_expansions(
                result_expansion,
                _to_extra(first_dx_tail_second_third_cross_product,
                          first_dx, first_dx_tail,
                          second_dy, second_squared_length,
                          third_dy, third_squared_length))

    if first_dy_tail:
        first_dy_tail_second_third_cross_product = scale_expansion(
                second_third_cross_product, first_dy_tail)
        result_expansion = sum_expansions(
                result_expansion,
                _to_extra(first_dy_tail_second_third_cross_product,
                          first_dy, first_dy_tail,
                          third_dx, third_squared_length,
                          second_dx, second_squared_length))

    if second_dx_tail:
        second_dx_tail_third_first_cross_product = scale_expansion(
                third_first_cross_product, second_dx_tail)
        result_expansion = sum_expansions(
                result_expansion,
                _to_extra(second_dx_tail_third_first_cross_product,
                          second_dx, second_dx_tail,
                          third_dy, third_squared_length,
                          first_dy, first_squared_length))

    if second_dy_tail:
        second_dy_tail_third_first_cross_product = scale_expansion(
                third_first_cross_product, second_dy_tail)
        result_expansion = sum_expansions(
                result_expansion,
                _to_extra(second_dy_tail_third_first_cross_product,
                          second_dy, second_dy_tail,
                          first_dx, first_squared_length,
                          third_dx, third_squared_length))

    if third_dx_tail:
        third_dx_tail_first_second_cross_product = scale_expansion(
                first_second_cross_product, third_dx_tail)
        result_expansion = sum_expansions(
                result_expansion,
                _to_extra(third_dx_tail_first_second_cross_product,
                          third_dx, third_dx_tail,
                          first_dy, first_squared_length,
                          second_dy, second_squared_length))

    if third_dy_tail:
        third_dy_tail_first_second_cross_product = scale_expansion(
                first_second_cross_product, third_dy_tail)
        result_expansion = sum_expansions(
                result_expansion,
                _to_extra(third_dy_tail_first_second_cross_product,
                          third_dy, third_dy_tail,
                          second_dx, second_squared_length,
                          first_dx, first_squared_length))

    if first_dx_tail or first_dy_tail:
        if second_dx_tail or second_dy_tail or third_dx_tail or third_dy_tail:
            second_third_crossed_tails, second_third_crossed_tails_tail = (
                _to_crossed_tails(second_dx, second_dx_tail,
                                  second_dy, second_dy_tail,
                                  third_dx, third_dx_tail,
                                  third_dy, third_dy_tail))
        else:
            second_third_crossed_tails = second_third_crossed_tails_tail = (0,)

        if first_dx_tail:
            result_expansion = reduce(
                    sum_expansions,
                    _to_dx_extras(first_dx_tail_second_third_cross_product,
                                  first_dx, first_dx_tail,
                                  second_dy_tail, second_squared_length,
                                  third_dy_tail, third_squared_length,
                                  second_third_crossed_tails,
                                  second_third_crossed_tails_tail),
                    result_expansion)

        if first_dy_tail:
            result_expansion = reduce(
                    sum_expansions,
                    _to_dy_extras(first_dy_tail_second_third_cross_product,
                                  first_dy, first_dy_tail,
                                  second_third_crossed_tails,
                                  second_third_crossed_tails_tail),
                    result_expansion)

    if second_dx_tail or second_dy_tail:
        if first_dx_tail or first_dy_tail or third_dx_tail or third_dy_tail:
            third_first_crossed_tails, third_first_crossed_tails_tail = (
                _to_crossed_tails(third_dx, third_dx_tail,
                                  third_dy, third_dy_tail,
                                  first_dx, first_dx_tail,
                                  first_dy, first_dy_tail))
        else:
            third_first_crossed_tails = third_first_crossed_tails_tail = (0,)

        if second_dx_tail:
            result_expansion = reduce(
                    sum_expansions,
                    _to_dx_extras(second_dx_tail_third_first_cross_product,
                                  second_dx, second_dx_tail,
                                  third_dy_tail, third_squared_length,
                                  first_dy_tail, first_squared_length,
                                  third_first_crossed_tails,
                                  third_first_crossed_tails_tail),
                    result_expansion)

        if second_dy_tail:
            result_expansion = reduce(
                    sum_expansions,
                    _to_dy_extras(second_dy_tail_third_first_cross_product,
                                  second_dy, second_dy_tail,
                                  third_first_crossed_tails,
                                  third_first_crossed_tails_tail),
                    result_expansion)

    if third_dx_tail or third_dy_tail:
        if first_dx_tail or first_dy_tail or second_dx_tail or second_dy_tail:
            first_second_crossed_tails, first_second_crossed_tails_tail = (
                _to_crossed_tails(first_dx, first_dx_tail,
                                  first_dy, first_dy_tail,
                                  second_dx, second_dx_tail,
                                  second_dy, second_dy_tail))
        else:
            first_second_crossed_tails = first_second_crossed_tails_tail = (0,)

        if third_dx_tail:
            result_expansion = reduce(
                    sum_expansions,
                    _to_dx_extras(third_dx_tail_first_second_cross_product,
                                  third_dx, third_dx_tail,
                                  first_dy_tail, first_squared_length,
                                  second_dy_tail, second_squared_length,
                                  first_second_crossed_tails,
                                  first_second_crossed_tails_tail),
                    result_expansion)

        if third_dy_tail:
            result_expansion = reduce(
                    sum_expansions,
                    _to_dy_extras(third_dy_tail_first_second_cross_product,
                                  third_dy, third_dy_tail,
                                  first_second_crossed_tails,
                                  first_second_crossed_tails_tail),
                    result_expansion)
    return result_expansion[-1]


def _to_dx_extras(expansion: Expansion,
                  dx: Scalar, dx_tail: Scalar,
                  left_dy_tail: Scalar, left_squared_length: Expansion,
                  right_dy_tail: Scalar, right_squared_length: Expansion,
                  left_right_crossed_tails: Expansion,
                  left_right_crossed_tails_tail: Expansion
                  ) -> Iterable[Expansion]:
    dx_tail_left_right_crossed_tails = scale_expansion(
            left_right_crossed_tails, dx_tail)
    yield sum_expansions(scale_expansion(expansion, dx_tail),
                         scale_expansion(dx_tail_left_right_crossed_tails,
                                         2 * dx))
    if left_dy_tail:
        yield scale_expansion(scale_expansion(right_squared_length, dx_tail),
                              left_dy_tail)
    if right_dy_tail:
        yield scale_expansion(scale_expansion(left_squared_length, -dx_tail),
                              right_dy_tail)
    first_addend = scale_expansion(dx_tail_left_right_crossed_tails, dx_tail)
    dx_tail_left_right_crossed_tails_tail = scale_expansion(
            left_right_crossed_tails_tail, dx_tail)
    second_addend = sum_expansions(
            scale_expansion(dx_tail_left_right_crossed_tails_tail, 2 * dx),
            scale_expansion(dx_tail_left_right_crossed_tails_tail, dx_tail))
    yield sum_expansions(first_addend, second_addend)


def _to_dy_extras(expansion: Expansion,
                  dy: Scalar, dy_tail: Scalar,
                  rest_crossed_tails: Expansion,
                  rest_crossed_tails_tail: Expansion) -> Iterable[Expansion]:
    dy_tail_rest_crossed_tails = scale_expansion(rest_crossed_tails, dy_tail)
    yield sum_expansions(scale_expansion(expansion, dy_tail),
                         scale_expansion(dy_tail_rest_crossed_tails, 2 * dy))
    first_addend = scale_expansion(dy_tail_rest_crossed_tails, dy_tail)
    dy_tail_rest_crossed_tails_tail = scale_expansion(rest_crossed_tails_tail,
                                                      dy_tail)
    second_addend = sum_expansions(
            scale_expansion(dy_tail_rest_crossed_tails_tail, 2 * dy),
            scale_expansion(dy_tail_rest_crossed_tails_tail, dy_tail))
    yield sum_expansions(first_addend, second_addend)


def _to_extra(expansion: Expansion,
              coordinate: Scalar, coordinate_tail: Scalar,
              left_coordinate: Scalar, left_squared_length: Expansion,
              right_coordinate: Scalar, right_squared_length: Expansion
              ) -> Expansion:
    second_addend = scale_expansion(scale_expansion(right_squared_length,
                                                    coordinate_tail),
                                    left_coordinate)
    first_addend = scale_expansion(expansion, 2 * coordinate)
    minuend = sum_expansions(first_addend, second_addend)
    subtrahend = scale_expansion(scale_expansion(left_squared_length,
                                                 coordinate_tail),
                                 -right_coordinate)
    return sum_expansions(subtrahend, minuend)


def _to_crossed_tails(left_dx: Scalar, left_dx_tail: Scalar,
                      left_dy: Scalar, left_dy_tail: Scalar,
                      right_dx: Scalar, right_dx_tail: Scalar,
                      right_dy: Scalar, right_dy_tail: Scalar
                      ) -> Tuple[Expansion, Expansion]:
    left_dx_tail_right_dy, left_dx_tail_right_dy_tail = two_product(
            left_dx_tail, right_dy)
    left_dx_right_dy_tail, left_dx_right_dy_tail_tail = two_product(
            left_dx, right_dy_tail)
    minus_right_dx_tail_left_dy, minus_right_dx_tail_left_dy_tail = (
        two_product(right_dx_tail, -left_dy))
    minus_right_dx_left_dy_tail, minus_right_dx_left_dy_tail_tail = (
        two_product(right_dx, -left_dy_tail))
    result = sum_expansions(two_two_sum(left_dx_tail_right_dy,
                                        left_dx_tail_right_dy_tail,
                                        left_dx_right_dy_tail,
                                        left_dx_right_dy_tail_tail),
                            two_two_sum(minus_right_dx_tail_left_dy,
                                        minus_right_dx_tail_left_dy_tail,
                                        minus_right_dx_left_dy_tail,
                                        minus_right_dx_left_dy_tail_tail))
    left_dx_tail_right_dy_tail, left_dx_tail_right_dy_tail_tail = two_product(
            left_dx_tail, right_dy_tail)
    right_dx_tail_left_dy_tail, right_dx_tail_left_dy_tail_tail = two_product(
            right_dx_tail, left_dy_tail)
    tail = two_two_diff(left_dx_tail_right_dy_tail,
                        left_dx_tail_right_dy_tail_tail,
                        right_dx_tail_left_dy_tail,
                        right_dx_tail_left_dy_tail_tail)
    return result, tail


def _multiply_by_squared_length(expansion: Expansion,
                                dx: Scalar, dy: Scalar) -> Expansion:
    return sum_expansions(scale_expansion(scale_expansion(expansion, dx), dx),
                          scale_expansion(scale_expansion(expansion, dy), dy))


def _to_addend(left_dx: Scalar, left_dx_tail: Scalar,
               left_dy: Scalar, left_dy_tail: Scalar,
               mid_dx: Scalar, mid_dx_tail: Scalar,
               mid_dy: Scalar, mid_dy_tail: Scalar,
               right_dx: Scalar, right_dx_tail: Scalar,
               right_dy: Scalar, right_dy_tail: Scalar) -> Scalar:
    return ((left_dx * left_dx + left_dy * left_dy)
            * ((mid_dx * right_dy_tail + right_dy * mid_dx_tail)
               - (mid_dy * right_dx_tail + right_dx * mid_dy_tail))
            + 2 * (left_dx * left_dx_tail + left_dy * left_dy_tail)
            * (mid_dx * right_dy - mid_dy * right_dx))


def _to_squared_length(dx: Scalar, dy: Scalar) -> Expansion:
    dx_squared, dx_squared_tail = square(dx)
    dy_squared, dy_squared_tail = square(dy)
    return two_two_sum(dx_squared, dx_squared_tail,
                       dy_squared, dy_squared_tail)
