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
from .core.contour import Contour as _Contour
from .core.empty import Empty as _Empty
from .core.geometry import (Coordinate as _Coordinate,
                            Geometry)
from .core.mix import Mix as _Mix
from .core.multipoint import Multipoint as _Multipoint
from .core.multipolygon import Multipolygon as _Multipolygon
from .core.multisegment import Multisegment as _Multisegment
from .core.point import Point as _Point
from .core.polygon import (Polygon as _Polygon,
                           Triangulation)
from .core.segment import Segment as _Segment

Compound = Compound
Geometry = Geometry
Indexable = Indexable
Linear = Linear
Shaped = Shaped

Location = Location
Orientation = Orientation
Relation = Relation

Triangulation = Triangulation


class _ContextMixin:
    __slots__ = ()

    @property
    def _context(self) -> _Context:
        return _context


class Empty(_ContextMixin, _Empty):
    __slots__ = ()


#: Empty geometry instance, equivalent of empty set.
EMPTY = Empty()


class Point(_ContextMixin, _Point[_Coordinate]):
    __slots__ = ()


class Contour(_ContextMixin, _Contour[_Coordinate]):
    __slots__ = ()


class Mix(_ContextMixin, _Mix[_Coordinate]):
    __slots__ = ()


class Multipoint(_ContextMixin, _Multipoint[_Coordinate]):
    __slots__ = ()


class Segment(_ContextMixin, _Segment[_Coordinate]):
    __slots__ = ()


class Multisegment(_ContextMixin, _Multisegment[_Coordinate]):
    __slots__ = ()


class Polygon(_ContextMixin, _Polygon[_Coordinate]):
    __slots__ = ()


class Multipolygon(_ContextMixin, _Multipolygon[_Coordinate]):
    __slots__ = ()


_initial_context = _get_context()
_context = _Context(box_cls=_initial_context.box_cls,
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
                    sqrt=_initial_context.sqrt)
_set_context(_context)
