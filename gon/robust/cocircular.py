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
    first_vector_x, first_vector_y = (first_point.x - fourth_point.x,
                                      first_point.y - fourth_point.y)
    second_vector_x, second_vector_y = (second_point.x - fourth_point.x,
                                        second_point.y - fourth_point.y)
    third_vector_x, third_vector_y = (third_point.x - fourth_point.x,
                                      third_point.y - fourth_point.y)

    first_point_squared_distance = (first_vector_x * first_vector_x
                                    + first_vector_y * first_vector_y)
    second_point_squared_distance = (second_vector_x * second_vector_x
                                     + second_vector_y * second_vector_y)
    third_point_squared_distance = (third_vector_x * third_vector_x
                                    + third_vector_y * third_vector_y)

    first_vector_x_second_vector_y = first_vector_x * second_vector_y
    first_vector_x_third_vector_y = first_vector_x * third_vector_y
    second_vector_x_first_vector_y = second_vector_x * first_vector_y
    second_vector_x_third_vector_y = second_vector_x * third_vector_y
    third_vector_x_first_vector_y = third_vector_x * first_vector_y
    third_vector_x_second_vector_y = third_vector_x * second_vector_y

    result = (first_point_squared_distance
              * (second_vector_x_third_vector_y
                 - third_vector_x_second_vector_y)
              + second_point_squared_distance
              * (third_vector_x_first_vector_y
                 - first_vector_x_third_vector_y)
              + third_point_squared_distance
              * (first_vector_x_second_vector_y
                 - second_vector_x_first_vector_y))
    upper_bound = (first_point_squared_distance
                   * (abs(second_vector_x_third_vector_y)
                      + abs(third_vector_x_second_vector_y))
                   + second_point_squared_distance
                   * (abs(third_vector_x_first_vector_y)
                      + abs(first_vector_x_third_vector_y))
                   + third_point_squared_distance
                   * (abs(first_vector_x_second_vector_y)
                      + abs(second_vector_x_first_vector_y)))
    error_bound = bounds.to_cocircular_first_error(upper_bound)
    if result > error_bound or -result > error_bound:
        return result
    return _adjusted_determinant(first_point, second_point,
                                 third_point, fourth_point,
                                 upper_bound)


def _adjusted_determinant(first_point: Point,
                          second_point: Point,
                          third_point: Point,
                          fourth_point: Point,
                          upper_bound: Scalar) -> Scalar:
    first_vector_x, first_vector_y = (first_point.x - fourth_point.x,
                                      first_point.y - fourth_point.y)
    second_vector_x, second_vector_y = (second_point.x - fourth_point.x,
                                        second_point.y - fourth_point.y)
    third_vector_x, third_vector_y = (third_point.x - fourth_point.x,
                                      third_point.y - fourth_point.y)

    second_third_vectors_cross_product = to_cross_product(
            second_vector_x, third_vector_y, third_vector_x, second_vector_y)
    first_addend = _to_first_addend(first_vector_x, first_vector_y,
                                    second_third_vectors_cross_product)

    third_first_vectors_cross_product = to_cross_product(
            third_vector_x, first_vector_y, first_vector_x, third_vector_y)
    second_addend = _to_first_addend(second_vector_x, second_vector_y,
                                     third_first_vectors_cross_product)

    first_second_vectors_cross_product = to_cross_product(
            first_vector_x, second_vector_y, second_vector_x, first_vector_y)
    third_addend = _to_first_addend(third_vector_x, third_vector_y,
                                    first_second_vectors_cross_product)

    result_expansion = sum_expansions(sum_expansions(first_addend,
                                                     second_addend),
                                      third_addend)
    result = sum(result_expansion)
    error_bound = bounds.to_cocircular_second_error(upper_bound)
    if result >= error_bound or -result >= error_bound:
        return result

    first_vector_x_tail = two_diff_tail(first_point.x, fourth_point.x,
                                        first_vector_x)
    first_vector_y_tail = two_diff_tail(first_point.y, fourth_point.y,
                                        first_vector_y)
    second_vector_x_tail = two_diff_tail(second_point.x, fourth_point.x,
                                         second_vector_x)
    second_vector_y_tail = two_diff_tail(second_point.y, fourth_point.y,
                                         second_vector_y)
    third_vector_x_tail = two_diff_tail(third_point.x, fourth_point.x,
                                        third_vector_x)
    third_vector_y_tail = two_diff_tail(third_point.y, fourth_point.y,
                                        third_vector_y)

    if (not first_vector_x_tail and not first_vector_y_tail
            and not second_vector_x_tail and not second_vector_y_tail
            and not third_vector_x_tail and not third_vector_y_tail):
        return result

    error_bound = (bounds.to_cocircular_third_error(upper_bound)
                   + bounds.to_determinant_error(result))
    result += (_to_second_addend(first_vector_x, first_vector_x_tail,
                                 first_vector_y, first_vector_y_tail,
                                 second_vector_x, second_vector_x_tail,
                                 second_vector_y, second_vector_y_tail,
                                 third_vector_x, third_vector_x_tail,
                                 third_vector_y, third_vector_y_tail)
               + _to_second_addend(second_vector_x, second_vector_x_tail,
                                   second_vector_y, second_vector_y_tail,
                                   third_vector_x, third_vector_x_tail,
                                   third_vector_y, third_vector_y_tail,
                                   first_vector_x, first_vector_x_tail,
                                   first_vector_y, first_vector_y_tail)
               + _to_second_addend(third_vector_x, third_vector_x_tail,
                                   third_vector_y, third_vector_y_tail,
                                   first_vector_x, first_vector_x_tail,
                                   first_vector_y, first_vector_y_tail,
                                   second_vector_x, second_vector_x_tail,
                                   second_vector_y, second_vector_y_tail))
    if result >= error_bound or -result >= error_bound:
        return result

    if (second_vector_x_tail or second_vector_y_tail
            or third_vector_x_tail or third_vector_y_tail):
        first_vector_squared_length = _to_squared_length(first_vector_x,
                                                         first_vector_y)
    else:
        first_vector_squared_length = (0,) * 4

    if (first_vector_x_tail or first_vector_y_tail
            or third_vector_x_tail or third_vector_y_tail):
        second_vector_squared_length = _to_squared_length(second_vector_x,
                                                          second_vector_y)
    else:
        second_vector_squared_length = (0,) * 4

    if (first_vector_x_tail or first_vector_y_tail
            or second_vector_x_tail or second_vector_y_tail):
        third_vector_squared_length = _to_squared_length(third_vector_x,
                                                         third_vector_y)
    else:
        third_vector_squared_length = (0,) * 4

    if first_vector_x_tail:
        axtbc = scale_expansion(second_third_vectors_cross_product,
                                first_vector_x_tail)
        temp16a = scale_expansion(axtbc, 2 * first_vector_x)
        axtcc = scale_expansion(third_vector_squared_length,
                                first_vector_x_tail)
        temp16b = scale_expansion(axtcc, second_vector_y)
        axtbb = scale_expansion(second_vector_squared_length,
                                first_vector_x_tail)
        temp16c = scale_expansion(axtbb, -third_vector_y)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if first_vector_y_tail:
        aytbc = scale_expansion(second_third_vectors_cross_product,
                                first_vector_y_tail)
        temp16a = scale_expansion(aytbc, 2 * first_vector_y)
        aytbb = scale_expansion(second_vector_squared_length,
                                first_vector_y_tail)
        temp16b = scale_expansion(aytbb, third_vector_x)
        aytcc = scale_expansion(third_vector_squared_length,
                                first_vector_y_tail)
        temp16c = scale_expansion(aytcc, -second_vector_x)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if second_vector_x_tail:
        bxtca = scale_expansion(third_first_vectors_cross_product,
                                second_vector_x_tail)
        temp16a = scale_expansion(bxtca, 2 * second_vector_x)
        bxtaa = scale_expansion(first_vector_squared_length,
                                second_vector_x_tail)
        temp16b = scale_expansion(bxtaa, third_vector_y)
        bxtcc = scale_expansion(third_vector_squared_length,
                                second_vector_x_tail)
        temp16c = scale_expansion(bxtcc, -first_vector_y)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if second_vector_y_tail:
        bytca = scale_expansion(third_first_vectors_cross_product,
                                second_vector_y_tail)
        temp16a = scale_expansion(bytca, 2 * second_vector_y)
        bytcc = scale_expansion(third_vector_squared_length,
                                second_vector_y_tail)
        temp16b = scale_expansion(bytcc, first_vector_x)
        bytaa = scale_expansion(first_vector_squared_length,
                                second_vector_y_tail)
        temp16c = scale_expansion(bytaa, -third_vector_x)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if third_vector_x_tail:
        cxtab = scale_expansion(first_second_vectors_cross_product,
                                third_vector_x_tail)
        temp16a = scale_expansion(cxtab, 2 * third_vector_x)
        cxtbb = scale_expansion(second_vector_squared_length,
                                third_vector_x_tail)
        temp16b = scale_expansion(cxtbb, first_vector_y)
        cxtaa = scale_expansion(first_vector_squared_length,
                                third_vector_x_tail)
        temp16c = scale_expansion(cxtaa, -second_vector_y)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if third_vector_y_tail:
        cytab = scale_expansion(first_second_vectors_cross_product,
                                third_vector_y_tail)
        temp16a = scale_expansion(cytab, 2 * third_vector_y)
        cytaa = scale_expansion(first_vector_squared_length,
                                third_vector_y_tail)
        temp16b = scale_expansion(cytaa, second_vector_x)
        cytbb = scale_expansion(second_vector_squared_length,
                                third_vector_y_tail)
        temp16c = scale_expansion(cytbb, -first_vector_x)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if first_vector_x_tail or first_vector_y_tail:
        if (second_vector_x_tail or second_vector_y_tail
                or third_vector_x_tail or third_vector_y_tail):
            ti, ti_tail = two_product(second_vector_x_tail, third_vector_y)
            tj, tj_tail = two_product(second_vector_x, third_vector_y_tail)
            u = two_two_sum(ti, ti_tail, tj, tj_tail)

            negate = -second_vector_y
            ti, ti_tail = two_product(third_vector_x_tail, negate)
            negate = -second_vector_y_tail
            tj, tj_tail = two_product(third_vector_x, negate)
            v = two_two_sum(ti, ti_tail, tj, tj_tail)

            bct = sum_expansions(u, v)

            ti, ti_tail = two_product(second_vector_x_tail,
                                      third_vector_y_tail)
            tj, tj_tail = two_product(third_vector_x_tail,
                                      second_vector_y_tail)
            bctt = two_two_diff(ti, ti_tail, tj, tj_tail)
        else:
            bct = bctt = (0,)

        if first_vector_x_tail:
            temp16a = scale_expansion(axtbc, first_vector_x_tail)
            axtbct = scale_expansion(bct, first_vector_x_tail)
            temp32a = scale_expansion(axtbct, 2 * first_vector_x)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            if second_vector_y_tail:
                temp8 = scale_expansion(third_vector_squared_length,
                                        first_vector_x_tail)
                temp16a = scale_expansion(temp8, second_vector_y_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            if third_vector_y_tail:
                temp8 = scale_expansion(second_vector_squared_length,
                                        -first_vector_x_tail)
                temp16a = scale_expansion(temp8, third_vector_y_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            temp32a = scale_expansion(axtbct, first_vector_x_tail)
            axtbctt = scale_expansion(bctt, first_vector_x_tail)
            temp16a = scale_expansion(axtbctt, 2 * first_vector_x)
            temp16b = scale_expansion(axtbctt, first_vector_x_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

        if first_vector_y_tail:
            temp16a = scale_expansion(aytbc, first_vector_y_tail)
            aytbct = scale_expansion(bct, first_vector_y_tail)
            temp32a = scale_expansion(aytbct, 2 * first_vector_y)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            temp32a = scale_expansion(aytbct, first_vector_y_tail)
            aytbctt = scale_expansion(bctt, first_vector_y_tail)
            temp16a = scale_expansion(aytbctt, 2 * first_vector_y)
            temp16b = scale_expansion(aytbctt, first_vector_y_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

    if second_vector_x_tail or second_vector_y_tail:
        if (first_vector_x_tail or first_vector_y_tail
                or third_vector_x_tail or third_vector_y_tail):
            ti, ti_tail = two_product(third_vector_x_tail, first_vector_y)
            tj, tj_tail = two_product(third_vector_x, first_vector_y_tail)
            u = two_two_sum(ti, ti_tail, tj, tj_tail)
            negate = -third_vector_y
            ti, ti_tail = two_product(first_vector_x_tail, negate)
            negate = -third_vector_y_tail
            tj, tj_tail = two_product(first_vector_x, negate)
            v = two_two_sum(ti, ti_tail, tj, tj_tail)
            cat = sum_expansions(u, v)

            ti, ti_tail = two_product(third_vector_x_tail, first_vector_y_tail)
            tj, tj_tail = two_product(first_vector_x_tail, third_vector_y_tail)
            catt = two_two_diff(ti, ti_tail, tj, tj_tail)
        else:
            cat = catt = (0,)

        if second_vector_x_tail:
            temp16a = scale_expansion(bxtca, second_vector_x_tail)
            bxtcat = scale_expansion(cat, second_vector_x_tail)
            temp32a = scale_expansion(bxtcat, 2 * second_vector_x)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            if third_vector_y_tail:
                temp8 = scale_expansion(first_vector_squared_length,
                                        second_vector_x_tail)
                temp16a = scale_expansion(temp8, third_vector_y_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            if first_vector_y_tail:
                temp8 = scale_expansion(third_vector_squared_length,
                                        -second_vector_x_tail)
                temp16a = scale_expansion(temp8, first_vector_y_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            temp32a = scale_expansion(bxtcat, second_vector_x_tail)
            bxtcatt = scale_expansion(catt, second_vector_x_tail)
            temp16a = scale_expansion(bxtcatt, 2 * second_vector_x)
            temp16b = scale_expansion(bxtcatt, second_vector_x_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

        if second_vector_y_tail:
            temp16a = scale_expansion(bytca, second_vector_y_tail)
            bytcat = scale_expansion(cat, second_vector_y_tail)
            temp32a = scale_expansion(bytcat, 2 * second_vector_y)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)
            temp32a = scale_expansion(bytcat, second_vector_y_tail)
            bytcatt = scale_expansion(catt, second_vector_y_tail)
            temp16a = scale_expansion(bytcatt, 2 * second_vector_y)
            temp16b = scale_expansion(bytcatt, second_vector_y_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

    if third_vector_x_tail or third_vector_y_tail:
        if (first_vector_x_tail or first_vector_y_tail
                or second_vector_x_tail or second_vector_y_tail):
            ti, ti_tail = two_product(first_vector_x_tail, second_vector_y)
            tj, tj_tail = two_product(first_vector_x, second_vector_y_tail)
            u = two_two_sum(ti, ti_tail, tj, tj_tail)
            negate = -first_vector_y
            ti, ti_tail = two_product(second_vector_x_tail, negate)
            negate = -first_vector_y_tail
            tj, tj_tail = two_product(second_vector_x, negate)
            v = two_two_sum(ti, ti_tail, tj, tj_tail)

            abt = sum_expansions(u, v)

            ti, ti_tail = two_product(first_vector_x_tail,
                                      second_vector_y_tail)
            tj, tj_tail = two_product(second_vector_x_tail,
                                      first_vector_y_tail)
            abtt = two_two_diff(ti, ti_tail, tj, tj_tail)
        else:
            abt = abtt = (0,)

        if third_vector_x_tail:
            temp16a = scale_expansion(cxtab, third_vector_x_tail)
            cxtabt = scale_expansion(abt, third_vector_x_tail)
            temp32a = scale_expansion(cxtabt, 2 * third_vector_x)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            if first_vector_y_tail:
                temp8 = scale_expansion(second_vector_squared_length,
                                        third_vector_x_tail)
                temp16a = scale_expansion(temp8, first_vector_y_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            if second_vector_y_tail:
                temp8 = scale_expansion(first_vector_squared_length,
                                        -third_vector_x_tail)
                temp16a = scale_expansion(temp8, second_vector_y_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            temp32a = scale_expansion(cxtabt, third_vector_x_tail)
            cxtabtt = scale_expansion(abtt, third_vector_x_tail)
            temp16a = scale_expansion(cxtabtt, 2 * third_vector_x)
            temp16b = scale_expansion(cxtabtt, third_vector_x_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

        if third_vector_y_tail:
            temp16a = scale_expansion(cytab, third_vector_y_tail)
            cytabt = scale_expansion(abt, third_vector_y_tail)
            temp32a = scale_expansion(cytabt, 2 * third_vector_y)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)
            temp32a = scale_expansion(cytabt, third_vector_y_tail)
            cytabtt = scale_expansion(abtt, third_vector_y_tail)
            temp16a = scale_expansion(cytabtt, 2 * third_vector_y)
            temp16b = scale_expansion(cytabtt, third_vector_y_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)
    return result_expansion[-1]


def _to_first_addend(vector_x: Scalar, vector_y: Scalar,
                     other_vectors_cross_product: Expansion) -> Expansion:
    vector_x_other_vectors_cross_product = scale_expansion(
            other_vectors_cross_product, vector_x)
    vector_y_other_vectors_cross_product = scale_expansion(
            other_vectors_cross_product, vector_y)
    return sum_expansions(scale_expansion(vector_x_other_vectors_cross_product,
                                          vector_x),
                          scale_expansion(vector_y_other_vectors_cross_product,
                                          vector_y))


def _to_second_addend(left_vector_x: Scalar, left_vector_x_tail: Scalar,
                      left_vector_y: Scalar, left_vector_y_tail: Scalar,
                      mid_vector_x: Scalar, mid_vector_x_tail: Scalar,
                      mid_vector_y: Scalar, mid_vector_y_tail: Scalar,
                      right_vector_x: Scalar, right_vector_x_tail: Scalar,
                      right_vector_y: Scalar, right_vector_y_tail: Scalar
                      ) -> Scalar:
    return ((left_vector_x * left_vector_x + left_vector_y * left_vector_y)
            * ((mid_vector_x * right_vector_y_tail
                + right_vector_y * mid_vector_x_tail)
               - (mid_vector_y * right_vector_x_tail
                  + right_vector_x * mid_vector_y_tail))
            + 2 * (left_vector_x * left_vector_x_tail
                   + left_vector_y * left_vector_y_tail)
            * (mid_vector_x * right_vector_y - mid_vector_y * right_vector_x))


def _to_squared_length(vector_x: Scalar, vector_y: Scalar) -> Expansion:
    vector_x_squared, vector_x_squared_tail = square(vector_x)
    vector_y_squared, vector_y_squared_tail = square(vector_y)
    return two_two_sum(vector_x_squared, vector_x_squared_tail,
                       vector_y_squared, vector_y_squared_tail)
