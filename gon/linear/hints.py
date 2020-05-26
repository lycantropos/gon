from typing import (List,
                    Sequence,
                    Tuple)

from gon.primitive import (Point,
                           RawPoint)

RawSegment = Tuple[RawPoint, RawPoint]
RawMultisegment = List[RawSegment]
RawContour = List[RawPoint]
Vertices = Sequence[Point]
