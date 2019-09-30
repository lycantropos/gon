from typing import (Sequence,
                    Tuple)

from gon.hints import Scalar
from . import bounds


def fast_two_sum(left: Scalar, right: Scalar) -> Tuple[Scalar, Scalar]:
    result = left + right
    right_virtual = result - left
    tail = right - right_virtual
    return result, tail


def two_sum(left: Scalar, right: Scalar) -> Tuple[Scalar, Scalar]:
    result = left + right
    right_virtual = result - left
    left_virtual = result - right_virtual
    right_tail = right - right_virtual
    left_tail = left - left_virtual
    tail = left_tail + right_tail
    return result, tail


def split(value: Scalar,
          *,
          splitter: Scalar = bounds.splitter) -> Tuple[Scalar, Scalar]:
    base = splitter * value
    result_high = base - (base - value)
    result_low = value - result_high
    return result_low, result_high


def two_product_presplit(left: Scalar, right: Scalar, right_low: Scalar,
                         right_high: Scalar) -> Tuple[Scalar, Scalar]:
    result = left * right
    left_low, left_high = split(left)
    first_error = result - left_high * right_high
    second_error = first_error - left_low * right_high
    third_error = second_error - left_high * right_low
    tail = left_low * right_low - third_error
    return result, tail


def two_product(left: Scalar, right: Scalar) -> Tuple[Scalar, Scalar]:
    result = left * right
    left_low, left_high = split(left)
    right_low, right_high = split(right)
    first_error = result - left_high * right_high
    second_error = first_error - left_low * right_high
    third_error = second_error - left_high * right_low
    tail = left_low * right_low - third_error
    return result, tail


def two_two_diff(left: Scalar, left_tail: Scalar,
                 right: Scalar, right_tail: Scalar
                 ) -> Tuple[Scalar, Scalar, Scalar, Scalar]:
    _j, _0, x0 = two_one_diff(left, left_tail, right_tail)
    x3, x2, x1 = two_one_diff(_j, _0, right)
    return x0, x1, x2, x3


def two_two_sum(left: Scalar, left_tail: Scalar,
                right: Scalar, right_tail: Scalar
                ) -> Tuple[Scalar, Scalar, Scalar, Scalar]:
    _j, _0, x0 = two_one_sum(left, left_tail, right_tail)
    x3, x2, x1 = two_one_sum(_j, _0, right)
    return x0, x1, x2, x3


def two_one_sum(left: Scalar, left_tail: Scalar,
                right: Scalar) -> Tuple[Scalar, Scalar, Scalar]:
    _i, x0 = two_sum(left_tail, right)
    x2, x1 = two_sum(left, _i)
    return x2, x1, x0


def two_one_diff(left: Scalar, left_tail: Scalar,
                 right: Scalar) -> Tuple[Scalar, Scalar, Scalar]:
    _i, x0 = two_diff(left_tail, right)
    x2, x1 = two_sum(left, _i)
    return x2, x1, x0


def two_diff(left: Scalar, right: Scalar) -> Tuple[Scalar, Scalar]:
    result = left - right
    return result, two_diff_tail(left, right, result)


def two_diff_tail(left: Scalar, right: Scalar, diff: Scalar) -> Scalar:
    right_virtual = left - diff
    left_virtual = diff + right_virtual
    right_error = right_virtual - right
    left_error = left - left_virtual
    return left_error + right_error


def square(value: Scalar) -> Tuple[Scalar, Scalar]:
    result = value * value
    value_low, value_high = split(value)
    first_error = result - value_high * value_high
    second_error = first_error - (value_high + value_high) * value_low
    tail = value_low * value_low - second_error
    return result, tail


Expansion = Sequence[Scalar]


def sum_expansions(left_expansion: Expansion,
                   right_expansion: Expansion) -> Expansion:
    """
    Sums two expansions with zero components elimination.
    """
    left_length = len(left_expansion)
    right_length = len(right_expansion)
    left_element, right_element = left_expansion[0], right_expansion[0]
    left_index = right_index = 0
    if (right_element > left_element) is (right_element > -left_element):
        accumulator = left_element
        left_index += 1
        try:
            left_element = left_expansion[left_index]
        except IndexError:
            pass
    else:
        accumulator = right_element
        right_index += 1
        try:
            right_element = right_expansion[right_index]
        except IndexError:
            pass
    result = []
    if (left_index < left_length) and (right_index < right_length):
        if (right_element > left_element) is (right_element > -left_element):
            accumulator, tail = fast_two_sum(left_element, accumulator)
            left_index += 1
            try:
                left_element = left_expansion[left_index]
            except IndexError:
                pass
        else:
            accumulator, tail = fast_two_sum(right_element, accumulator)
            right_index += 1
            try:
                right_element = right_expansion[right_index]
            except IndexError:
                pass
        if tail:
            result.append(tail)
        while (left_index < left_length) and (right_index < right_length):
            if ((right_element > left_element)
                    is (right_element > -left_element)):
                accumulator, tail = two_sum(accumulator, left_element)
                left_index += 1
                try:
                    left_element = left_expansion[left_index]
                except IndexError:
                    pass
            else:
                accumulator, tail = two_sum(accumulator, right_element)
                right_index += 1
                try:
                    right_element = right_expansion[right_index]
                except IndexError:
                    pass
            if tail:
                result.append(tail)
    while left_index < left_length:
        accumulator, tail = two_sum(accumulator, left_element)
        left_index += 1
        try:
            left_element = left_expansion[left_index]
        except IndexError:
            pass
        if tail:
            result.append(tail)
    while right_index < right_length:
        accumulator, tail = two_sum(accumulator, right_element)
        right_index += 1
        try:
            right_element = right_expansion[right_index]
        except IndexError:
            pass
        if tail:
            result.append(tail)
    if accumulator or not result:
        result.append(accumulator)
    return result


def scale_expansion(expansion: Expansion, scalar: Scalar) -> Expansion:
    """
    Multiplies an expansion by a scalar with zero components elimination.
    """
    expansion = iter(expansion)
    scalar_low, scalar_high = split(scalar)
    accumulator, tail = two_product_presplit(next(expansion), scalar,
                                             scalar_low, scalar_high)
    result = []
    if tail:
        result.append(tail)
    for element in expansion:
        product, product_tail = two_product_presplit(element, scalar,
                                                     scalar_low, scalar_high)
        interim, tail = two_sum(accumulator, product_tail)
        if tail:
            result.append(tail)
        accumulator, tail = fast_two_sum(product, interim)
        if tail:
            result.append(tail)
    if accumulator or not result:
        result.append(accumulator)
    return result
