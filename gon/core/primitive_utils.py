import math
from numbers import Real

from symba.base import Expression

from .hints import Coordinate


def is_finite(value: Coordinate) -> bool:
    return (math.isfinite(value)
            if isinstance(value, Real)
            else isinstance(value, Expression) and value.is_finite)
