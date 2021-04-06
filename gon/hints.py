from numbers import Real as _Real
from typing import TypeVar as _TypeVar

from symba.base import Expression as _Expression

Domain = _TypeVar('Domain')
Coordinate = _TypeVar('Coordinate', _Expression, _Real)
