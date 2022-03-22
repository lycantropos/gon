from ground.base import (Context as _Context,
                         get_context as _get_context,
                         set_context as _set_context)
from ground.hints import Scalar as _Scalar

from .core.angle import (Angle as _Angle,
                         Kind,
                         Orientation)
from .core.compound import (Compound,
                            Indexable,
                            Linear,
                            Location,
                            Relation,
                            Shaped)
from .core.contour import Contour as _Contour
from .core.empty import Empty as _Empty
from .core.geometry import Geometry
from .core.mix import Mix as _Mix
from .core.multipoint import Multipoint as _Multipoint
from .core.multipolygon import Multipolygon as _Multipolygon
from .core.multisegment import Multisegment as _Multisegment
from .core.point import Point as _Point
from .core.polygon import (Polygon as _Polygon,
                           Triangulation)
from .core.segment import Segment as _Segment
from .core.vector import Vector as _Vector

Compound = Compound
Geometry = Geometry
Indexable = Indexable
Linear = Linear
Shaped = Shaped
Compound.__module__ = __name__
Geometry.__module__ = __name__
Indexable.__module__ = __name__
Linear.__module__ = __name__
Shaped.__module__ = __name__

Kind = Kind
Location = Location
Orientation = Orientation
Relation = Relation

Triangulation = Triangulation


class _ContextMixin:
    _context = ...  # type: _Context
    __slots__ = ()


class Empty(_ContextMixin, _Empty):
    __slots__ = ()


#: Empty geometry instance, equivalent of empty set.
EMPTY = Empty()


class Point(_ContextMixin, _Point[_Scalar]):
    __slots__ = ()


class Contour(_ContextMixin, _Contour[_Scalar]):
    __slots__ = ()


class Mix(_ContextMixin, _Mix[_Scalar]):
    __slots__ = ()


class Multipoint(_ContextMixin, _Multipoint[_Scalar]):
    __slots__ = ()


class Segment(_ContextMixin, _Segment[_Scalar]):
    __slots__ = ()


class Multisegment(_ContextMixin, _Multisegment[_Scalar]):
    __slots__ = ()


class Polygon(_ContextMixin, _Polygon[_Scalar]):
    __slots__ = ()


class Multipolygon(_ContextMixin, _Multipolygon[_Scalar]):
    __slots__ = ()


class Angle(_ContextMixin, _Angle[_Scalar]):
    __slots__ = ()


class Vector(_ContextMixin, _Vector[_Scalar]):
    __slots__ = ()


_context = _get_context().replace(contour_cls=Contour,
                                  empty_cls=Empty,
                                  mix_cls=Mix,
                                  multipoint_cls=Multipoint,
                                  multipolygon_cls=Multipolygon,
                                  multisegment_cls=Multisegment,
                                  point_cls=Point,
                                  polygon_cls=Polygon,
                                  segment_cls=Segment)
_ContextMixin._context = _context
_set_context(_context)
