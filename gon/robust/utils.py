from typing import (Sequence,
                    Tuple)

from . import bounds


def fast_two_sum(left: float, right: float) -> Tuple[float, float]:
    result = left + right
    right_virtual = result - left
    tail = right - right_virtual
    return result, tail


def two_sum(left: float, right: float) -> Tuple[float, float]:
    result = left + right
    right_virtual = result - left
    left_virtual = result - right_virtual
    right_roundoff = right - right_virtual
    left_roundoff = left - left_virtual
    tail = left_roundoff + right_roundoff
    return result, tail


def split(value: float,
          *,
          splitter: float = bounds.splitter) -> Tuple[float, float]:
    c = splitter * value
    result_high = c - (c - value)
    result_low = value - result_high
    return result_low, result_high


def two_product_presplit(left: float, right: float, right_low: float,
                         right_high: float) -> Tuple[float, float]:
    result = left * right
    left_low, left_high = split(left)
    first_error = result - left_high * right_high
    second_error = first_error - left_low * right_high
    third_error = second_error - left_high * right_low
    tail = left_low * right_low - third_error
    return result, tail


def two_product(left: float, right: float) -> Tuple[float, float]:
    result = left * right
    left_low, left_high = split(left)
    right_low, right_high = split(right)
    first_error = result - left_high * right_high
    second_error = first_error - left_low * right_high
    third_error = second_error - left_high * right_low
    tail = left_low * right_low - third_error
    return result, tail


def two_two_diff(left: float, left_tail: float,
                 right: float, right_tail: float
                 ) -> Tuple[float, float, float, float]:
    _j, _0, x0 = two_one_diff(left, left_tail, right_tail)
    x3, x2, x1 = two_one_diff(_j, _0, right)
    return x0, x1, x2, x3


def two_two_sum(left: float, left_tail: float,
                right: float, right_tail: float
                ) -> Tuple[float, float, float, float]:
    _j, _0, x0 = two_one_sum(left, left_tail, right_tail)
    x3, x2, x1 = two_one_sum(_j, _0, right)
    return x0, x1, x2, x3


def two_one_sum(left: float, left_tail: float,
                right: float) -> Tuple[float, float, float]:
    _i, x0 = two_sum(left_tail, right)
    x2, x1 = two_sum(left, _i)
    return x2, x1, x0


def two_one_diff(left: float, left_tail: float,
                 right: float) -> Tuple[float, float, float]:
    _i, x0 = two_diff(left_tail, right)
    x2, x1 = two_sum(left, _i)
    return x2, x1, x0


def two_diff(left: float, right: float) -> Tuple[float, float]:
    result = left - right
    return result, two_diff_tail(left, right, result)


def two_diff_tail(left: float, right: float, diff: float) -> float:
    right_virtual = left - diff
    left_virtual = diff + right_virtual
    right_roundoff = right_virtual - right
    left_roundoff = left - left_virtual
    return left_roundoff + right_roundoff


def square(value: float) -> Tuple[float, float]:
    result = value * value
    value_low, value_high = split(value)
    first_error = result - value_high * value_high
    second_error = first_error - (value_high + value_high) * value_low
    tail = value_low * value_low - second_error
    return result, tail


Expansion = Sequence[float]


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
        q = left_element
        left_index += 1
        try:
            left_element = left_expansion[left_index]
        except IndexError:
            pass
    else:
        q = right_element
        right_index += 1
        try:
            right_element = right_expansion[right_index]
        except IndexError:
            pass
    result = []
    if (left_index < left_length) and (right_index < right_length):
        if (right_element > left_element) is (right_element > -left_element):
            q, hh = fast_two_sum(left_element, q)
            left_index += 1
            try:
                left_element = left_expansion[left_index]
            except IndexError:
                pass
        else:
            q, hh = fast_two_sum(right_element, q)
            right_index += 1
            try:
                right_element = right_expansion[right_index]
            except IndexError:
                pass
        if hh:
            result.append(hh)
        while (left_index < left_length) and (right_index < right_length):
            if ((right_element > left_element)
                    is (right_element > -left_element)):
                q, hh = two_sum(q, left_element)
                left_index += 1
                try:
                    left_element = left_expansion[left_index]
                except IndexError:
                    pass
            else:
                q, hh = two_sum(q, right_element)
                right_index += 1
                try:
                    right_element = right_expansion[right_index]
                except IndexError:
                    pass
            if hh:
                result.append(hh)
    while left_index < left_length:
        q, hh = two_sum(q, left_element)
        left_index += 1
        try:
            left_element = left_expansion[left_index]
        except IndexError:
            pass
        if hh:
            result.append(hh)
    while right_index < right_length:
        q, hh = two_sum(q, right_element)
        right_index += 1
        try:
            right_element = right_expansion[right_index]
        except IndexError:
            pass
        if hh:
            result.append(hh)
    if q or not result:
        result.append(q)
    return result


def scale_expansion(expansion: Expansion, scalar: float) -> Expansion:
    """
    Multiplies an expansion by a scalar with zero components elimination.
    """
    expansion = iter(expansion)
    scalar_low, scalar_high = split(scalar)
    q, hh = two_product_presplit(next(expansion), scalar,
                                 scalar_low, scalar_high)
    result = []
    if hh:
        result.append(hh)
    for element in expansion:
        product1, product0 = two_product_presplit(element, scalar,
                                                  scalar_low, scalar_high)
        sum_, hh = two_sum(q, product0)
        if hh:
            result.append(hh)
        q, hh = fast_two_sum(product1, sum_)
        if hh:
            result.append(hh)
    if q or not result:
        result.append(q)
    return result
