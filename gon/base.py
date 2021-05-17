from ground.base import (Context as _Context,
                         get_context as _get_context,
                         set_context as _set_context)

from .core.angular import Orientation
from .core.compound import (Compound,
                            Indexable,
                            Linear,
                            Location,
                            Relation,
                            Shaped)
from .core.contour import Contour
from .core.empty import (EMPTY,
                         Empty)
from .core.geometry import Geometry
from .core.mix import Mix
from .core.multipoint import Multipoint
from .core.multipolygon import Multipolygon
from .core.multisegment import Multisegment
from .core.point import Point
from .core.polygon import (Polygon,
                           Triangulation)
from .core.segment import Segment

EMPTY = EMPTY
Compound = Compound
Contour = Contour
Empty = Empty
Geometry = Geometry
Indexable = Indexable
Linear = Linear
Location = Location
Mix = Mix
Multipoint = Multipoint
Multisegment = Multisegment
Multipolygon = Multipolygon
Orientation = Orientation
Point = Point
Polygon = Polygon
Relation = Relation
Segment = Segment
Shaped = Shaped
Triangulation = Triangulation
_initial_context = _get_context()
_set_context(_Context(box_cls=_initial_context.box_cls,
                      contour_cls=Contour,
                      empty_cls=Empty,
                      mix_cls=Mix,
                      multipoint_cls=Multipoint,
                      multipolygon_cls=Multipolygon,
                      multisegment_cls=Multisegment,
                      point_cls=Point,
                      polygon_cls=Polygon,
                      segment_cls=Segment,
                      mode=_initial_context.mode,
                      sqrt=_initial_context.sqrt))
