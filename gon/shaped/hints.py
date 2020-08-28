from typing import (List,
                    Tuple)

from gon.linear import RawContour

RawRegion = RawContour
RawMultiregion = List[RawRegion]
RawPolygon = Tuple[RawRegion, RawMultiregion]
RawMultipolygon = List[RawPolygon]
