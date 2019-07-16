from decimal import Decimal
from numbers import Real
from typing import (Sequence,
                    TypeVar)

Scalar = TypeVar('Scalar', Real, Decimal)
Permutation = Sequence[int]
