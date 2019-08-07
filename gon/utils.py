from operator import itemgetter
from typing import (Any,
                    Iterable)

import math
from lz.functional import compose
from lz.hints import Domain
from lz.iterating import slider
from lz.sorting import Key

from .hints import (Permutation,
                    Scalar)

_sentinel = object()


def to_index_min(values: Iterable[Domain],
                 *,
                 key: Key = None,
                 default: Any = _sentinel) -> int:
    kwargs = {}
    if key is not None:
        kwargs['key'] = compose(key, itemgetter(0))
    if default is not _sentinel:
        kwargs['default'] = default
    return min(((value, index)
                for index, value in enumerate(values)),
               **kwargs)[1]


triplewise = slider(3)


def inverse_permutation(permutation: Permutation) -> Permutation:
    """
    Based on:
        permutation of indices with values.

    Reference:
        http://mathworld.wolfram.com/InversePermutation.html

    Time complexity:
        O(n)
    """
    result = [None] * len(permutation)
    for index, element in enumerate(permutation):
        result[element] = index
    return type(permutation)(result)


def to_sign(value: Scalar) -> int:
    validate_value(value)
    if value > 0:
        return 1
    elif value < 0:
        return -1
    else:
        return 0


def validate_value(value: Scalar) -> None:
    if not math.isfinite(value):
        raise ValueError('NaN/infinity are not supported.')
