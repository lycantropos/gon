from typing import Tuple

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

    second_third_vectors_cross_product = to_cross_product(second_dx, third_dy,
                                                          third_dx, second_dy)
    third_first_vectors_cross_product = to_cross_product(third_dx, first_dy,
                                                         first_dx, third_dy)
    first_second_vectors_cross_product = to_cross_product(first_dx, second_dy,
                                                          second_dx, first_dy)
    result_expansion = sum_expansions(sum_expansions(
            _multiply_by_squared_length(
                    second_third_vectors_cross_product,
                    first_dx, first_dy),
            _multiply_by_squared_length(
                    third_first_vectors_cross_product,
                    second_dx, second_dy)),
            _multiply_by_squared_length(
                    first_second_vectors_cross_product,
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
    result += (_to_second_addend(first_dx, first_dx_tail,
                                 first_dy, first_dy_tail,
                                 second_dx, second_dx_tail,
                                 second_dy, second_dy_tail,
                                 third_dx, third_dx_tail,
                                 third_dy, third_dy_tail)
               + _to_second_addend(second_dx, second_dx_tail,
                                   second_dy, second_dy_tail,
                                   third_dx, third_dx_tail,
                                   third_dy, third_dy_tail,
                                   first_dx, first_dx_tail,
                                   first_dy, first_dy_tail)
               + _to_second_addend(third_dx, third_dx_tail,
                                   third_dy, third_dy_tail,
                                   first_dx, first_dx_tail,
                                   first_dy, first_dy_tail,
                                   second_dx, second_dx_tail,
                                   second_dy, second_dy_tail))
    if result >= error_bound or -result >= error_bound:
        return result

    if (second_dx_tail or second_dy_tail
            or third_dx_tail or third_dy_tail):
        first_squared_length = _to_squared_length(first_dx, first_dy)
    else:
        first_squared_length = (0,) * 4

    if (first_dx_tail or first_dy_tail
            or third_dx_tail or third_dy_tail):
        second_squared_length = _to_squared_length(second_dx, second_dy)
    else:
        second_squared_length = (0,) * 4

    if (first_dx_tail or first_dy_tail
            or second_dx_tail or second_dy_tail):
        third_squared_length = _to_squared_length(third_dx, third_dy)
    else:
        third_squared_length = (0,) * 4

    if first_dx_tail:
        axtbc = scale_expansion(second_third_vectors_cross_product,
                                first_dx_tail)
        temp16a = scale_expansion(axtbc, 2 * first_dx)
        axtcc = scale_expansion(third_squared_length, first_dx_tail)
        temp16b = scale_expansion(axtcc, second_dy)
        axtbb = scale_expansion(second_squared_length, first_dx_tail)
        temp16c = scale_expansion(axtbb, -third_dy)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if first_dy_tail:
        aytbc = scale_expansion(second_third_vectors_cross_product,
                                first_dy_tail)
        temp16a = scale_expansion(aytbc, 2 * first_dy)
        aytbb = scale_expansion(second_squared_length, first_dy_tail)
        temp16b = scale_expansion(aytbb, third_dx)
        aytcc = scale_expansion(third_squared_length, first_dy_tail)
        temp16c = scale_expansion(aytcc, -second_dx)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if second_dx_tail:
        bxtca = scale_expansion(third_first_vectors_cross_product,
                                second_dx_tail)
        temp16a = scale_expansion(bxtca, 2 * second_dx)
        bxtaa = scale_expansion(first_squared_length, second_dx_tail)
        temp16b = scale_expansion(bxtaa, third_dy)
        bxtcc = scale_expansion(third_squared_length, second_dx_tail)
        temp16c = scale_expansion(bxtcc, -first_dy)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if second_dy_tail:
        bytca = scale_expansion(third_first_vectors_cross_product,
                                second_dy_tail)
        temp16a = scale_expansion(bytca, 2 * second_dy)
        bytcc = scale_expansion(third_squared_length, second_dy_tail)
        temp16b = scale_expansion(bytcc, first_dx)
        bytaa = scale_expansion(first_squared_length, second_dy_tail)
        temp16c = scale_expansion(bytaa, -third_dx)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if third_dx_tail:
        cxtab = scale_expansion(first_second_vectors_cross_product,
                                third_dx_tail)
        temp16a = scale_expansion(cxtab, 2 * third_dx)
        cxtbb = scale_expansion(second_squared_length, third_dx_tail)
        temp16b = scale_expansion(cxtbb, first_dy)
        cxtaa = scale_expansion(first_squared_length, third_dx_tail)
        temp16c = scale_expansion(cxtaa, -second_dy)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if third_dy_tail:
        cytab = scale_expansion(first_second_vectors_cross_product,
                                third_dy_tail)
        temp16a = scale_expansion(cytab, 2 * third_dy)
        cytaa = scale_expansion(first_squared_length, third_dy_tail)
        temp16b = scale_expansion(cytaa, second_dx)
        cytbb = scale_expansion(second_squared_length, third_dy_tail)
        temp16c = scale_expansion(cytbb, -first_dx)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if first_dx_tail or first_dy_tail:
        if second_dx_tail or second_dy_tail or third_dx_tail or third_dy_tail:
            bct, bctt = _to_crossed_tails(second_dx, second_dx_tail,
                                          second_dy, second_dy_tail,
                                          third_dx, third_dx_tail,
                                          third_dy, third_dy_tail)
        else:
            bct = bctt = (0,)

        if first_dx_tail:
            temp16a = scale_expansion(axtbc, first_dx_tail)
            axtbct = scale_expansion(bct, first_dx_tail)
            temp32a = scale_expansion(axtbct, 2 * first_dx)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            if second_dy_tail:
                temp8 = scale_expansion(third_squared_length,
                                        first_dx_tail)
                temp16a = scale_expansion(temp8, second_dy_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            if third_dy_tail:
                temp8 = scale_expansion(second_squared_length, -first_dx_tail)
                temp16a = scale_expansion(temp8, third_dy_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            temp32a = scale_expansion(axtbct, first_dx_tail)
            axtbctt = scale_expansion(bctt, first_dx_tail)
            temp16a = scale_expansion(axtbctt, 2 * first_dx)
            temp16b = scale_expansion(axtbctt, first_dx_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

        if first_dy_tail:
            temp16a = scale_expansion(aytbc, first_dy_tail)
            aytbct = scale_expansion(bct, first_dy_tail)
            temp32a = scale_expansion(aytbct, 2 * first_dy)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            temp32a = scale_expansion(aytbct, first_dy_tail)
            aytbctt = scale_expansion(bctt, first_dy_tail)
            temp16a = scale_expansion(aytbctt, 2 * first_dy)
            temp16b = scale_expansion(aytbctt, first_dy_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

    if second_dx_tail or second_dy_tail:
        if first_dx_tail or first_dy_tail or third_dx_tail or third_dy_tail:
            cat, catt = _to_crossed_tails(third_dx, third_dx_tail,
                                          third_dy, third_dy_tail,
                                          first_dx, first_dx_tail,
                                          first_dy, first_dy_tail)
        else:
            cat = catt = (0,)

        if second_dx_tail:
            temp16a = scale_expansion(bxtca, second_dx_tail)
            bxtcat = scale_expansion(cat, second_dx_tail)
            temp32a = scale_expansion(bxtcat, 2 * second_dx)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            if third_dy_tail:
                temp8 = scale_expansion(first_squared_length, second_dx_tail)
                temp16a = scale_expansion(temp8, third_dy_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            if first_dy_tail:
                temp8 = scale_expansion(third_squared_length, -second_dx_tail)
                temp16a = scale_expansion(temp8, first_dy_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            temp32a = scale_expansion(bxtcat, second_dx_tail)
            bxtcatt = scale_expansion(catt, second_dx_tail)
            temp16a = scale_expansion(bxtcatt, 2 * second_dx)
            temp16b = scale_expansion(bxtcatt, second_dx_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

        if second_dy_tail:
            temp16a = scale_expansion(bytca, second_dy_tail)
            bytcat = scale_expansion(cat, second_dy_tail)
            temp32a = scale_expansion(bytcat, 2 * second_dy)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)
            temp32a = scale_expansion(bytcat, second_dy_tail)
            bytcatt = scale_expansion(catt, second_dy_tail)
            temp16a = scale_expansion(bytcatt, 2 * second_dy)
            temp16b = scale_expansion(bytcatt, second_dy_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

    if third_dx_tail or third_dy_tail:
        if first_dx_tail or first_dy_tail or second_dx_tail or second_dy_tail:
            abt, abtt = _to_crossed_tails(first_dx, first_dx_tail,
                                          first_dy, first_dy_tail,
                                          second_dx, second_dx_tail,
                                          second_dy, second_dy_tail)
        else:
            abt = abtt = (0,)

        if third_dx_tail:
            temp16a = scale_expansion(cxtab, third_dx_tail)
            cxtabt = scale_expansion(abt, third_dx_tail)
            temp32a = scale_expansion(cxtabt, 2 * third_dx)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            if first_dy_tail:
                temp8 = scale_expansion(second_squared_length, third_dx_tail)
                temp16a = scale_expansion(temp8, first_dy_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            if second_dy_tail:
                temp8 = scale_expansion(first_squared_length, -third_dx_tail)
                temp16a = scale_expansion(temp8, second_dy_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            temp32a = scale_expansion(cxtabt, third_dx_tail)
            cxtabtt = scale_expansion(abtt, third_dx_tail)
            temp16a = scale_expansion(cxtabtt, 2 * third_dx)
            temp16b = scale_expansion(cxtabtt, third_dx_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

        if third_dy_tail:
            temp16a = scale_expansion(cytab, third_dy_tail)
            cytabt = scale_expansion(abt, third_dy_tail)
            temp32a = scale_expansion(cytabt, 2 * third_dy)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)
            temp32a = scale_expansion(cytabt, third_dy_tail)
            cytabtt = scale_expansion(abtt, third_dy_tail)
            temp16a = scale_expansion(cytabtt, 2 * third_dy)
            temp16b = scale_expansion(cytabtt, third_dy_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)
    return result_expansion[-1]


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


def _to_second_addend(left_dx: Scalar, left_dx_tail: Scalar,
                      left_dy: Scalar, left_dy_tail: Scalar,
                      mid_dx: Scalar, mid_dx_tail: Scalar,
                      mid_dy: Scalar, mid_dy_tail: Scalar,
                      right_dx: Scalar, right_dx_tail: Scalar,
                      right_dy: Scalar, right_dy_tail: Scalar
                      ) -> Scalar:
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
