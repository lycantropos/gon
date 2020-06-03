from typing import (List,
                    Tuple)

from gon.linear import RawContour

RawPolygon = Tuple[RawContour, List[RawContour]]
RawMultipolygon = List[RawPolygon]
