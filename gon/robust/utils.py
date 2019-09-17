from typing import (Sequence,
                    Tuple)

from .bounds import splitter


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


def split(value: float) -> Tuple[float, float]:
    c = splitter * value
    result_hi = c - (c - value)
    result_lo = value - result_hi
    return result_hi, result_lo


def two_product_presplit(a: float, b: float,
                         bhi: float, blo: float) -> Tuple[float, float]:
    result = a * b
    ahi, alo = split(a)
    err1 = result - ahi * bhi
    err2 = err1 - alo * bhi
    err3 = err2 - ahi * blo
    tail = alo * blo - err3
    return result, tail


def two_product(left: float, right: float) -> Tuple[float, float]:
    result = left * right
    left_hi, left_lo = split(left)
    right_hi, right_lo = split(right)
    first_error = result - left_hi * right_hi
    second_error = first_error - left_lo * right_hi
    third_error = second_error - left_hi * right_lo
    tail = left_lo * right_lo - third_error
    return result, tail


def two_two_diff(left: float, left_tail: float,
                 right: float, right_tail: float
                 ) -> Tuple[float, float, float, float]:
    _j, _0, x0 = two_one_diff(left, left_tail, right_tail)
    x3, x2, x1 = two_one_diff(_j, _0, right)
    return x3, x2, x1, x0


def two_two_sum(left: float, left_tail: float,
                right: float, right_tail: float
                ) -> Tuple[float, float, float, float]:
    _j, _0, x0 = two_one_sum(left, left_tail, right_tail)
    x3, x2, x1 = two_one_sum(_j, _0, right)
    return x3, x2, x1, x0


def two_one_sum(left: float, left_tail: float,
                right: float) -> Tuple[float, float, float]:
    _i, x0 = two_sum(left_tail, right)
    x2, x1 = two_sum(left, _i)
    return x2, x1, x0


def two_one_diff(a1: float, a0: float, b: float) -> Tuple[float, float, float]:
    _i, x0 = two_diff(a0, b)
    x2, x1 = two_sum(a1, _i)
    return x2, x1, x0


def two_diff(a: float, b: float):
    x = a - b
    b_virtual = a - x
    a_virtual = x + b_virtual
    b_roundoff = b_virtual - b
    a_roundoff = a - a_virtual
    y = a_roundoff + b_roundoff
    return x, y


def two_diff_tail(a: float, b: float, x: float) -> float:
    b_virtual = a - x
    a_virtual = x + b_virtual
    b_roundoff = b_virtual - b
    a_roundoff = a - a_virtual
    y = a_roundoff + b_roundoff
    return y


def square(a: float) -> Tuple[float, float]:
    x = a * a
    ahi, alo = split(a)
    err1 = x - ahi * ahi
    err3 = err1 - (ahi + ahi) * alo
    y = alo * alo - err3
    return x, y


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
    scalar_hi, scalar_lo = split(scalar)
    q, hh = two_product_presplit(next(expansion), scalar,
                                 scalar_hi, scalar_lo)
    result = []
    if hh:
        result.append(hh)
    for element in expansion:
        product1, product0 = two_product_presplit(element, scalar,
                                                  scalar_hi, scalar_lo)
        sum_, hh = two_sum(q, product0)
        if hh:
            result.append(hh)
        q, hh = fast_two_sum(product1, sum_)
        if hh:
            result.append(hh)
    if q or not result:
        result.append(q)
    return result
