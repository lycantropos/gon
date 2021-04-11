from typing import (List,
                    Tuple,
                    Union)

from .hints import Coordinate

RAW_EMPTY = None
RawEmpty = type(RAW_EMPTY)
RawPoint = Tuple[Coordinate, Coordinate]
RawContour = List[RawPoint]
RawMultipoint = List[RawPoint]
RawSegment = Tuple[RawPoint, RawPoint]
RawMultisegment = List[RawSegment]
RawRegion = RawContour
RawMultiregion = List[RawRegion]
RawPolygon = Tuple[RawRegion, RawMultiregion]
RawMultipolygon = List[RawPolygon]
RawMix = Tuple[Union[RawEmpty, RawMultipoint],
               Union[RawEmpty, RawMultisegment],
               Union[RawEmpty, RawMultipolygon]]
