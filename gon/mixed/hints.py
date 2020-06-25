from typing import (Tuple,
                    Union)

from gon.degenerate import RawEmpty
from gon.discrete import RawMultipoint
from gon.linear import RawMultisegment
from gon.shaped import RawMultipolygon

RawMix = Tuple[Union[RawEmpty, RawMultipoint],
               Union[RawEmpty, RawMultisegment],
               Union[RawEmpty, RawMultipolygon]]
