from reprit.base import generate_repr

from gon.compound import (Compound,
                          Indexable,
                          Linear,
                          Location,
                          Relation,
                          Shaped)
from gon.degenerate import (EMPTY,
                            RAW_EMPTY,
                            Maybe)
from gon.discrete import Multipoint
from gon.geometry import Geometry
from gon.hints import Domain
from gon.linear import Multisegment
from gon.mixed import RawMix
from gon.primitive import Point
from gon.shaped import Multipolygon

MIN_MIX_NON_EMPTY_COMPONENTS = 2


class Mix(Indexable):
    __slots__ = '_multipoint', '_multisegment', '_multipolygon', '_components'

    def __init__(self, multipoint: Maybe[Multipoint],
                 multisegment: Maybe[Multisegment],
                 multipolygon: Maybe[Multipolygon]) -> None:
        """
        Initializes mix.

        Time complexity:
            ``O(1)``
        Memory complexity:
            ``O(1)``
        """
        self._multipoint = multipoint
        self._multisegment = multisegment
        self._multipolygon = multipolygon
        self._components = (self._multipoint, self._multisegment,
                            self._multipolygon)

    __repr__ = generate_repr(__init__)

    def __and__(self, other: Compound) -> Compound:
        multipoint_part = self._multipoint & other
        multisegment_part = self._multisegment & other
        if isinstance(multisegment_part, Multipoint):
            multipoint_part |= multisegment_part
            multisegment_part = EMPTY
        multipolygon_part = self._multipolygon & other
        if isinstance(multipolygon_part, Multipoint):
            multipoint_part |= multipolygon_part
            multipolygon_part = EMPTY
        elif isinstance(multipolygon_part, Linear):
            multisegment_part |= multipolygon_part
            multipolygon_part = EMPTY
        return _from_mix_components(multipoint_part, multisegment_part,
                                    multipolygon_part)

    __rand__ = __and__

    def __contains__(self, other: Geometry) -> bool:
        return isinstance(other, Point) and bool(self.locate(other))

    def __eq__(self, other: Geometry) -> bool:
        return (self._components == other._components
                if isinstance(other, Mix)
                else (False
                      if isinstance(other, Geometry)
                      else NotImplemented))

    def __ge__(self, other: Compound) -> bool:
        return (other is EMPTY
                or self == other
                or (self.relate(other) in (Relation.EQUAL, Relation.COMPONENT,
                                           Relation.ENCLOSED, Relation.WITHIN)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __gt__(self, other: Compound) -> bool:
        return (other is EMPTY
                or self != other
                and (self.relate(other) in (Relation.COMPONENT,
                                            Relation.ENCLOSED, Relation.WITHIN)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __hash__(self) -> int:
        return hash(self._components)

    def __le__(self, other: Compound) -> bool:
        return (self == other
                or (not isinstance(other, Multipoint)
                    and (self._multipolygon is EMPTY
                         or not isinstance(other, Linear)
                         and (not isinstance(other, Mix)
                              or other._multipolygon is not EMPTY))
                    and self.relate(other) in (Relation.COVER,
                                               Relation.ENCLOSES,
                                               Relation.COMPOSITE,
                                               Relation.EQUAL)
                    if isinstance(other, Compound)
                    else NotImplemented))

    def __lt__(self, other: Compound) -> bool:
        return (self != other
                and (not isinstance(other, Multipoint)
                     and (self._multipolygon is EMPTY
                          or not isinstance(other, (Multipoint, Linear))
                          and (not isinstance(other, Mix)
                               or other._multipolygon is not EMPTY))
                     and self.relate(other) in (Relation.COVER,
                                                Relation.ENCLOSES,
                                                Relation.COMPOSITE)
                     if isinstance(other, Compound)
                     else NotImplemented))

    def __rsub__(self, other: Compound) -> Compound:
        return ((other - self._multipoint) & (other - self._multisegment)
                & other - self._multipolygon)

    def __sub__(self, other: Compound) -> Compound:
        return _from_mix_components(self._multipoint - other,
                                    self._multisegment - other,
                                    self._multipolygon - other)

    @classmethod
    def from_raw(cls, raw: RawMix) -> Domain:
        raw_multipoint, raw_multisegment, raw_multipolygon = raw
        return cls(EMPTY
                   if raw_multipoint is RAW_EMPTY
                   else Multipoint.from_raw(raw_multipoint),
                   EMPTY
                   if raw_multisegment is RAW_EMPTY
                   else Multisegment.from_raw(raw_multisegment),
                   EMPTY
                   if raw_multipolygon is RAW_EMPTY
                   else Multipolygon.from_raw(raw_multipolygon))

    @property
    def multipoint(self) -> Maybe[Multipoint]:
        return self._multipoint

    @property
    def multipolygon(self) -> Maybe[Multipolygon]:
        return self._multipolygon

    @property
    def multisegment(self) -> Maybe[Multisegment]:
        return self._multisegment

    def index(self) -> None:
        if self._multisegment is not EMPTY:
            self._multisegment.index()
        if self._multipolygon is not EMPTY:
            self._multipolygon.index()

    def locate(self, point: Point) -> Location:
        for candidate in self._components:
            location = candidate.locate(point)
            if location is not Location.EXTERIOR:
                return location
        return Location.EXTERIOR

    def raw(self) -> RawMix:
        return (self._multipoint.raw(), self._multisegment.raw(),
                self._multipolygon.raw())

    def relate(self, other: Compound) -> Relation:
        return (self._relate_multipoint(other)
                if isinstance(other, Multipoint)
                else (self._relate_linear(other)
                      if isinstance(other, Linear)
                      else (self._relate_shaped(other)
                            if isinstance(other, Shaped)
                            else (self._relate_mix(other)
                                  if isinstance(other, Mix)
                                  else other.relate(self).complement))))

    def validate(self) -> None:
        if (sum(component is not EMPTY for component in self._components)
                < MIN_MIX_NON_EMPTY_COMPONENTS):
            raise ValueError('At least {count} components should not be empty.'
                             .format(count=MIN_MIX_NON_EMPTY_COMPONENTS))
        for component in self._components:
            component.validate()
        if (not self._multipoint.disjoint(self._multisegment)
                or not self._multipoint.disjoint(self._multipolygon)):
            raise ValueError('Multipoint should be disjoint '
                             'with other components.')
        multipolygon_multisegment_relation = self._multipolygon.relate(
                self._multisegment)
        if multipolygon_multisegment_relation in (Relation.CROSS,
                                                  Relation.COMPONENT,
                                                  Relation.ENCLOSED,
                                                  Relation.WITHIN):
            raise ValueError('Multisegment should not {} multipolygon.'
                             .format('cross'
                                     if (multipolygon_multisegment_relation
                                         is Relation.CROSS)
                                     else 'be subset of'))
        elif (multipolygon_multisegment_relation is Relation.TOUCH
              and any(polygon.border.relate(self._multisegment)
                      is Relation.OVERLAP
                      or any(hole.border.relate(self._multisegment)
                             is Relation.OVERLAP
                             for hole in polygon.holes)
                      for polygon in self._multipolygon.polygons)):
            raise ValueError('Multisegment should not overlap '
                             'multipolygon borders.')

    def _relate_linear(self, other: Linear) -> Relation:
        if self._multipolygon is EMPTY:
            multisegment_relation = self._multisegment.relate(other)
            if multisegment_relation is Relation.DISJOINT:
                multipoint_relation = self._multipoint.relate(other)
                return (Relation.TOUCH
                        if multipoint_relation is Relation.COMPOSITE
                        else multipoint_relation)
            elif multisegment_relation is Relation.EQUAL:
                return Relation.COMPONENT
            elif multisegment_relation is Relation.COMPOSITE:
                multipoint_relation = self._multipoint.relate(other)
                return (multisegment_relation
                        if multipoint_relation is multisegment_relation
                        else Relation.OVERLAP)
            else:
                return multisegment_relation
        else:
            multipolygon_relation = self._multipolygon.relate(other)
            if multipolygon_relation is Relation.DISJOINT:
                multisegment_relation = self._multisegment.relate(other)
                if multisegment_relation is Relation.DISJOINT:
                    multipoint_relation = self._multipoint.relate(other)
                    return (multipolygon_relation
                            if multipoint_relation is Relation.DISJOINT
                            else Relation.TOUCH)
                elif (multisegment_relation is Relation.TOUCH
                      or multisegment_relation is Relation.CROSS):
                    return multisegment_relation
                elif (multisegment_relation is Relation.EQUAL
                      or multisegment_relation is Relation.COMPONENT):
                    return Relation.COMPONENT
                else:
                    return Relation.TOUCH
            elif (multipolygon_relation is Relation.TOUCH
                  or multipolygon_relation is Relation.CROSS):
                rest_other = other - self._multipolygon
                multisegment_relation = self._multisegment.relate(rest_other)
                return (Relation.COMPONENT
                        if (multisegment_relation is Relation.EQUAL
                            or multisegment_relation is Relation.COMPONENT)
                        else multipolygon_relation)
            else:
                return multipolygon_relation

    def _relate_mix(self, other: 'Mix') -> Relation:
        if self._multipolygon is other._multipolygon is EMPTY:
            multisegments_relation = self._multisegment.relate(
                    other._multisegment)
            if multisegments_relation is Relation.DISJOINT:
                return (multisegments_relation
                        if (self._relate_multipoint(other._multipoint)
                            is other._relate_multipoint(self._multipoint)
                            is multisegments_relation)
                        else Relation.TOUCH)
            elif multisegments_relation in (Relation.TOUCH,
                                            Relation.CROSS,
                                            Relation.OVERLAP):
                return multisegments_relation
            elif multisegments_relation is Relation.COMPONENT:
                other_multipoint_relation = self._relate_multipoint(
                        other._multipoint)
                return (multisegments_relation
                        if other_multipoint_relation is Relation.COMPONENT
                        else Relation.OVERLAP)
            elif multisegments_relation is Relation.COMPOSITE:
                multipoint_relation = other._relate_multipoint(
                        self._multipoint)
                return (multisegments_relation
                        if multipoint_relation is Relation.COMPONENT
                        else Relation.OVERLAP)
            else:
                assert multisegments_relation is Relation.EQUAL
                multipoints_relation = self._multipoint.relate(
                        other._multipoint)
                return (multisegments_relation
                        if multipoints_relation is Relation.EQUAL
                        else Relation.OVERLAP)
        elif self._multipolygon is EMPTY:
            multisegment_relation = other._relate_linear(
                    self._multisegment)
            if multisegment_relation is Relation.DISJOINT:
                multipoint_relation = other._relate_multipoint(
                        self._multipoint)
                return (multipoint_relation
                        if multipoint_relation in (Relation.DISJOINT,
                                                   Relation.TOUCH,
                                                   Relation.CROSS)
                        else (Relation.TOUCH
                              if multipoint_relation is Relation.COMPONENT
                              else Relation.CROSS))
            elif multisegment_relation is Relation.TOUCH:
                multipoint_relation = other._relate_multipoint(
                        self._multipoint)
                return (Relation.CROSS
                        if multipoint_relation in (Relation.CROSS,
                                                   Relation.ENCLOSED,
                                                   Relation.WITHIN)
                        else multisegment_relation)
            elif multisegment_relation is Relation.COMPONENT:
                multipoint_relation = other._relate_multipoint(
                        self._multipoint)
                return (Relation.TOUCH
                        if (multipoint_relation is Relation.DISJOINT
                            or multipoint_relation is Relation.TOUCH)
                        else (multipoint_relation
                              if multipoint_relation is Relation.CROSS
                              else
                              (Relation.COMPOSITE
                               if multipoint_relation is Relation.COMPONENT
                               else Relation.ENCLOSES)))
            elif multisegment_relation is Relation.ENCLOSED:
                multipoint_relation = other._relate_multipoint(
                        self._multipoint)
                return (Relation.CROSS
                        if multipoint_relation in (Relation.DISJOINT,
                                                   Relation.TOUCH,
                                                   Relation.CROSS)
                        else Relation.ENCLOSES)
            elif multisegment_relation is Relation.WITHIN:
                multipoint_relation = other._relate_multipoint(
                        self._multipoint)
                return (Relation.CROSS
                        if multipoint_relation in (Relation.DISJOINT,
                                                   Relation.TOUCH,
                                                   Relation.CROSS)
                        else (Relation.COVER
                              if multipoint_relation is multisegment_relation
                              else Relation.ENCLOSES))
            else:
                assert multisegment_relation is Relation.CROSS
                return multisegment_relation
        elif other._multipolygon is EMPTY:
            multisegment_relation = self._relate_linear(
                    other._multisegment)
            if multisegment_relation is Relation.DISJOINT:
                multipoint_relation = self._relate_multipoint(
                        other._multipoint)
                return (multipoint_relation
                        if multipoint_relation in (Relation.DISJOINT,
                                                   Relation.TOUCH,
                                                   Relation.CROSS)
                        else (Relation.TOUCH
                              if multipoint_relation is Relation.COMPONENT
                              else Relation.CROSS))
            elif multisegment_relation is Relation.TOUCH:
                multipoint_relation = self._relate_multipoint(
                        other._multipoint)
                return (Relation.CROSS
                        if multipoint_relation in (Relation.CROSS,
                                                   Relation.ENCLOSED,
                                                   Relation.WITHIN)
                        else multisegment_relation)
            elif multisegment_relation is Relation.COMPONENT:
                multipoint_relation = self._relate_multipoint(
                        other._multipoint)
                return (Relation.TOUCH
                        if (multipoint_relation is Relation.DISJOINT
                            or multipoint_relation is Relation.TOUCH)
                        else (multipoint_relation
                              if (multipoint_relation is Relation.CROSS
                                  or multipoint_relation is Relation.COMPONENT)
                              else Relation.ENCLOSED))
            elif multisegment_relation is Relation.ENCLOSED:
                multipoint_relation = self._relate_multipoint(
                        other._multipoint)
                return (Relation.CROSS
                        if multipoint_relation in (Relation.DISJOINT,
                                                   Relation.TOUCH,
                                                   Relation.CROSS)
                        else multisegment_relation)
            elif multisegment_relation is Relation.WITHIN:
                multipoint_relation = other._relate_multipoint(
                        self._multipoint)
                return (Relation.CROSS
                        if multipoint_relation in (Relation.DISJOINT,
                                                   Relation.TOUCH,
                                                   Relation.CROSS)
                        else (multisegment_relation
                              if multipoint_relation is multisegment_relation
                              else Relation.ENCLOSED))
            else:
                assert multisegment_relation is Relation.CROSS
                return multisegment_relation
        multipolygons_relation = self._multipolygon.relate(
                other._multipolygon)
        if multipolygons_relation is Relation.OVERLAP:
            return multipolygons_relation
        elif multipolygons_relation is Relation.EQUAL:
            multisegments_relation = self._multisegment.relate(
                    other._multisegment)
            if (self._multisegment is other._multisegment is EMPTY
                    or multisegments_relation is Relation.EQUAL):
                multipoints_relation = self._multipoint.relate(
                        other._multipoint)
                if (self._multipoint is other._multipoint is EMPTY
                        or multipoints_relation is Relation.EQUAL):
                    return Relation.EQUAL
                elif self._multipoint is EMPTY:
                    return Relation.COMPONENT
                elif other._multipoint is EMPTY:
                    return Relation.COMPOSITE
                elif (multipoints_relation is Relation.COMPONENT
                      or multipoints_relation is Relation.COMPOSITE):
                    return multipoints_relation
                else:
                    return Relation.OVERLAP
            elif (self._multisegment is EMPTY
                  or multisegments_relation is Relation.COMPOSITE):
                multipoints_relation = self._multipoint.relate(
                        other._multipoint)
                return (Relation.COMPOSITE
                        if (multipoints_relation is Relation.EQUAL
                            or multipoints_relation is Relation.COMPOSITE)
                        else Relation.OVERLAP)
            elif (other._multisegment is EMPTY
                  or multisegments_relation is Relation.COMPONENT):
                multipoints_relation = self._multipoint.relate(
                        other._multipoint)
                return (Relation.COMPONENT
                        if (multipoints_relation is Relation.EQUAL
                            or multipoints_relation is Relation.COMPONENT)
                        else Relation.OVERLAP)
            else:
                return Relation.OVERLAP
        elif multipolygons_relation in (Relation.COVER,
                                        Relation.ENCLOSES,
                                        Relation.COMPOSITE):
            if self._multisegment is EMPTY:
                multipoint_relation = other._relate_multipoint(
                        self._multipoint).complement
                return (multipolygons_relation
                        if multipoint_relation is multipolygons_relation
                        else (Relation.ENCLOSES
                              if multipoint_relation in (Relation.COVER,
                                                         Relation.ENCLOSES,
                                                         Relation.COMPOSITE)
                              else Relation.OVERLAP))
            else:
                multisegment_relation = other._relate_linear(
                        self._multisegment).complement
                if multisegment_relation is multipolygons_relation:
                    if self._multipoint is EMPTY:
                        return multipolygons_relation
                    else:
                        multipoint_relation = other._relate_multipoint(
                                self._multipoint).complement
                        return (multipolygons_relation
                                if (multipoint_relation
                                    is multipolygons_relation)
                                else
                                (Relation.ENCLOSES
                                 if multipoint_relation in (Relation.COVER,
                                                            Relation.ENCLOSES,
                                                            Relation.COMPOSITE)
                                 else Relation.OVERLAP))
                elif multisegment_relation in (Relation.COVER,
                                               Relation.ENCLOSES,
                                               Relation.COMPOSITE):
                    if self._multipoint is EMPTY:
                        return Relation.ENCLOSES
                    else:
                        multipoint_relation = other._relate_multipoint(
                                self._multipoint).complement
                        return (Relation.ENCLOSES
                                if multipoint_relation in (Relation.COVER,
                                                           Relation.ENCLOSES,
                                                           Relation.COMPOSITE)
                                else Relation.OVERLAP)
                else:
                    return Relation.OVERLAP
        elif multipolygons_relation in (Relation.COMPONENT,
                                        Relation.ENCLOSED,
                                        Relation.WITHIN):
            if other._multisegment is EMPTY:
                multipoint_relation = self._relate_multipoint(
                        other._multipoint)
                return (multipolygons_relation
                        if multipoint_relation is multipolygons_relation
                        else (Relation.ENCLOSED
                              if multipoint_relation in (Relation.COMPONENT,
                                                         Relation.ENCLOSED,
                                                         Relation.WITHIN)
                              else Relation.OVERLAP))
            else:
                multisegment_relation = self._relate_linear(
                        other._multisegment)
                if multisegment_relation is multipolygons_relation:
                    if other._multipoint is EMPTY:
                        return multipolygons_relation
                    else:
                        multipoint_relation = self._relate_multipoint(
                                other._multipoint)
                        return (multipolygons_relation
                                if (multipoint_relation
                                    is multipolygons_relation)
                                else
                                (Relation.ENCLOSED
                                 if multipoint_relation in (Relation.COMPONENT,
                                                            Relation.ENCLOSED,
                                                            Relation.WITHIN)
                                 else Relation.OVERLAP))
                elif multisegment_relation in (Relation.COMPONENT,
                                               Relation.ENCLOSED,
                                               Relation.WITHIN):
                    if other._multipoint is EMPTY:
                        return Relation.ENCLOSED
                    else:
                        multipoint_relation = self._relate_multipoint(
                                other._multipoint)
                        return (Relation.ENCLOSED
                                if multipoint_relation in (Relation.COMPONENT,
                                                           Relation.ENCLOSED,
                                                           Relation.WITHIN)
                                else Relation.OVERLAP)
                else:
                    return Relation.OVERLAP
        else:
            assert (multipolygons_relation is Relation.DISJOINT
                    or multipolygons_relation is Relation.TOUCH)
            if self._multisegment is other._multisegment is EMPTY:
                other_multipoint_relation = self._relate_multipoint(
                        other._multipoint)
                if other_multipoint_relation is Relation.CROSS:
                    return other_multipoint_relation
                elif (other_multipoint_relation is Relation.ENCLOSED
                      or other_multipoint_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    multipoint_relation = other._relate_multipoint(
                            self._multipoint)
                    if (multipoint_relation
                            is other_multipoint_relation
                            is Relation.DISJOINT):
                        return multipolygons_relation
                    elif multipoint_relation is Relation.CROSS:
                        return multipoint_relation
                    elif (multipoint_relation is Relation.ENCLOSED
                          or multipoint_relation is Relation.WITHIN):
                        return Relation.CROSS
                    else:
                        return Relation.TOUCH
            elif self._multisegment is EMPTY:
                other_multisegment_relation = self._relate_linear(
                        other._multisegment)
                if other_multisegment_relation is Relation.CROSS:
                    return other_multisegment_relation
                elif (other_multisegment_relation is Relation.ENCLOSED
                      or other_multisegment_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    multipoint_relation = other._relate_multipoint(
                            self._multipoint)
                    if multipoint_relation is Relation.CROSS:
                        return multipoint_relation
                    elif (multipoint_relation is Relation.ENCLOSED
                          or multipoint_relation is Relation.WITHIN):
                        return Relation.CROSS
                    elif other._multipoint is EMPTY:
                        return (multipolygons_relation
                                if (multipoint_relation
                                    is other_multisegment_relation
                                    is Relation.DISJOINT)
                                else Relation.TOUCH)
                    else:
                        other_multipoint_relation = self._relate_multipoint(
                                other._multipoint)
                        if other_multipoint_relation is Relation.CROSS:
                            return other_multipoint_relation
                        elif (other_multipoint_relation is Relation.ENCLOSED
                              or other_multipoint_relation is Relation.WITHIN):
                            return Relation.CROSS
                        elif (multipoint_relation
                              is other_multipoint_relation
                              is other_multisegment_relation
                              is Relation.DISJOINT):
                            return multipolygons_relation
                        else:
                            return Relation.TOUCH
            elif other._multisegment is EMPTY:
                multisegment_relation = other._relate_linear(
                        self._multisegment)
                if multisegment_relation is Relation.CROSS:
                    return multisegment_relation
                elif (multisegment_relation is Relation.ENCLOSED
                      or multisegment_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    other_multipoint_relation = self._relate_multipoint(
                            other._multipoint)
                    if other_multipoint_relation is Relation.CROSS:
                        return other_multipoint_relation
                    elif (other_multipoint_relation is Relation.ENCLOSED
                          or other_multipoint_relation is Relation.WITHIN):
                        return Relation.CROSS
                    elif self._multipoint is EMPTY:
                        return (multipolygons_relation
                                if (multisegment_relation
                                    is other_multipoint_relation
                                    is Relation.DISJOINT)
                                else Relation.TOUCH)
                    else:
                        multipoint_relation = other._relate_multipoint(
                                self._multipoint)
                        if multipoint_relation is Relation.CROSS:
                            return multipoint_relation
                        elif (multipoint_relation is Relation.ENCLOSED
                              or multipoint_relation is Relation.WITHIN):
                            return Relation.CROSS
                        elif (multipoint_relation
                              is multisegment_relation
                              is other_multipoint_relation
                              is Relation.DISJOINT):
                            return multipolygons_relation
                        else:
                            return Relation.TOUCH
            else:
                other_multisegment_relation = self._relate_linear(
                        other._multisegment)
                if other_multisegment_relation is Relation.CROSS:
                    return other_multisegment_relation
                elif (other_multisegment_relation is Relation.ENCLOSED
                      or other_multisegment_relation is Relation.WITHIN):
                    return Relation.CROSS
                else:
                    multisegment_relation = other._relate_linear(
                            self._multisegment)
                    if multisegment_relation is Relation.CROSS:
                        return multisegment_relation
                    elif (multisegment_relation is Relation.ENCLOSED
                          or multisegment_relation is Relation.WITHIN):
                        return Relation.CROSS
                    elif self._multipoint is EMPTY:
                        other_multipoint_relation = self._relate_multipoint(
                                other._multipoint)
                        return (other_multipoint_relation
                                if other_multipoint_relation is Relation.CROSS
                                else
                                (Relation.CROSS
                                 if (other_multipoint_relation
                                     is Relation.ENCLOSED
                                     or other_multipoint_relation
                                     is Relation.WITHIN)
                                 else (multipolygons_relation
                                       if (other_multipoint_relation
                                           is multisegment_relation
                                           is other_multisegment_relation
                                           is Relation.DISJOINT)
                                       else Relation.TOUCH)))
                    elif other._multipoint is EMPTY:
                        multipoint_relation = other._relate_multipoint(
                                self._multipoint)
                        return (multipoint_relation
                                if multipoint_relation is Relation.CROSS
                                else
                                (Relation.CROSS
                                 if (multipoint_relation is Relation.ENCLOSED
                                     or multipoint_relation is Relation.WITHIN)
                                 else (multipolygons_relation
                                       if (multipoint_relation
                                           is multisegment_relation
                                           is other_multisegment_relation
                                           is Relation.DISJOINT)
                                       else Relation.TOUCH)))
                    else:
                        other_multipoint_relation = self._relate_multipoint(
                                other._multipoint)
                        if other_multipoint_relation is Relation.CROSS:
                            return other_multipoint_relation
                        elif (other_multipoint_relation is Relation.ENCLOSED
                              or other_multipoint_relation is Relation.WITHIN):
                            return Relation.CROSS
                        else:
                            multipoint_relation = other._relate_multipoint(
                                    self._multipoint)
                            return (multipoint_relation
                                    if multipoint_relation is Relation.CROSS
                                    else (Relation.CROSS
                                          if (multipoint_relation
                                              is Relation.ENCLOSED
                                              or multipoint_relation
                                              is Relation.WITHIN)
                                          else
                                          (multipolygons_relation
                                           if (multipoint_relation
                                               is multisegment_relation
                                               is other_multipoint_relation
                                               is other_multisegment_relation
                                               is Relation.DISJOINT)
                                           else Relation.TOUCH)))

    def _relate_multipoint(self, other: Multipoint) -> Relation:
        if self._multipolygon is EMPTY:
            multisegment_relation = self._multisegment.relate(other)
            if multisegment_relation is Relation.DISJOINT:
                multipoint_relation = self._multipoint.relate(other)
                return (multipoint_relation
                        if multipoint_relation is Relation.DISJOINT
                        else (Relation.COMPONENT
                              if (multipoint_relation is Relation.COMPONENT
                                  or multipoint_relation is Relation.EQUAL)
                              else Relation.TOUCH))
            elif multisegment_relation is Relation.TOUCH:
                rest_other = other - self._multisegment
                multipoint_relation = self._multipoint.relate(rest_other)
                return (Relation.COMPONENT
                        if (multipoint_relation is Relation.EQUAL
                            or multipoint_relation is Relation.COMPOSITE)
                        else multisegment_relation)
            else:
                return multisegment_relation
        else:
            multipolygon_relation = self._multipolygon.relate(other)
            if multipolygon_relation in (Relation.COMPONENT,
                                         Relation.ENCLOSED,
                                         Relation.WITHIN):
                return multipolygon_relation
            elif (multipolygon_relation is Relation.TOUCH
                  or multipolygon_relation is Relation.CROSS):
                rest_other = other - self._multipolygon
                if self._multisegment is EMPTY:
                    multipoint_relation = self._multipoint.relate(rest_other)
                    return (Relation.COMPONENT
                            if (multipoint_relation is Relation.EQUAL
                                or multipoint_relation is Relation.COMPONENT)
                            else multipolygon_relation)
                else:
                    multisegment_relation = self._multisegment.relate(
                            rest_other)
                    if multisegment_relation is Relation.DISJOINT:
                        multipoint_relation = self._multipoint.relate(
                                rest_other)
                        return ((Relation.COMPONENT
                                 if multipolygon_relation is Relation.TOUCH
                                 else Relation.ENCLOSED)
                                if (multipoint_relation is Relation.COMPONENT
                                    or multipoint_relation is Relation.EQUAL)
                                else multipolygon_relation)
                    elif multisegment_relation is Relation.TOUCH:
                        rest_other -= self._multisegment
                        multipoint_relation = self._multipoint.relate(
                                rest_other)
                        return (Relation.COMPONENT
                                if (multipoint_relation is Relation.COMPONENT
                                    or multipoint_relation is Relation.EQUAL)
                                else multipolygon_relation)
                    else:
                        return (Relation.COMPONENT
                                if multipolygon_relation is Relation.TOUCH
                                else Relation.ENCLOSED)
            elif self._multipoint is EMPTY:
                return self._multisegment.relate(other)
            elif self._multisegment is EMPTY:
                multipoint_relation = self._multipoint.relate(other)
                return (multipolygon_relation
                        if multipoint_relation is Relation.DISJOINT
                        else (Relation.COMPONENT
                              if (multipoint_relation is Relation.EQUAL
                                  or multipoint_relation is Relation.COMPONENT)
                              else Relation.TOUCH))
            else:
                multisegment_relation = self._multisegment.relate(other)
                if multisegment_relation is Relation.DISJOINT:
                    multipoint_relation = self._multipoint.relate(other)
                    return (multipolygon_relation
                            if multipoint_relation is Relation.DISJOINT
                            else (Relation.COMPONENT
                                  if (multipoint_relation is Relation.COMPONENT
                                      or multipoint_relation is Relation.EQUAL)
                                  else Relation.TOUCH))
                elif multisegment_relation is Relation.TOUCH:
                    rest_other = other - self._multisegment
                    multipoint_relation = self._multipoint.relate(rest_other)
                    return (multipolygon_relation
                            if multipoint_relation is Relation.DISJOINT
                            else (Relation.COMPONENT
                                  if (multipoint_relation is Relation.COMPONENT
                                      or multipoint_relation is Relation.EQUAL)
                                  else Relation.TOUCH))
                else:
                    return multisegment_relation

    def _relate_shaped(self, other: Shaped) -> Relation:
        multipolygon_relation = self._multipolygon.relate(other)
        if multipolygon_relation in (Relation.OVERLAP,
                                     Relation.COMPONENT,
                                     Relation.ENCLOSED,
                                     Relation.WITHIN):
            return multipolygon_relation
        elif multipolygon_relation is Relation.EQUAL:
            return Relation.COMPONENT
        elif self._multisegment is EMPTY:
            multipoint_relation = self._multipoint.relate(other)
            return (multipolygon_relation
                    if multipoint_relation is multipolygon_relation
                    else (Relation.ENCLOSES
                          if multipoint_relation in (Relation.COVER,
                                                     Relation.ENCLOSES,
                                                     Relation.COMPOSITE)
                          else Relation.OVERLAP))
        else:
            multisegment_relation = self._multisegment.relate(other)
            if multisegment_relation in (Relation.DISJOINT,
                                         Relation.TOUCH,
                                         Relation.CROSS):
                return Relation.OVERLAP
            elif multisegment_relation is multipolygon_relation:
                if self._multipoint is EMPTY:
                    return multipolygon_relation
                else:
                    multipoint_relation = self._multipoint.relate(other)
                    return (multipolygon_relation
                            if multipoint_relation is multipolygon_relation
                            else
                            (Relation.ENCLOSES
                             if multipoint_relation in (Relation.COVER,
                                                        Relation.ENCLOSES,
                                                        Relation.COMPOSITE)
                             else Relation.OVERLAP))
            elif self._multipoint is EMPTY:
                return Relation.ENCLOSES
            else:
                multipoint_relation = self._multipoint.relate(other)
                return (Relation.ENCLOSES
                        if multipoint_relation in (Relation.COVER,
                                                   Relation.ENCLOSES,
                                                   Relation.COMPOSITE)
                        else Relation.OVERLAP)


def _from_mix_components(multipoint: Maybe[Multipoint],
                         multisegment: Maybe[Multisegment],
                         multipolygon: Maybe[Multipolygon]) -> Compound:
    return (Mix(multipoint, multisegment, multipolygon)
            if (((multipoint is not EMPTY)
                 + (multisegment is not EMPTY)
                 + (multipolygon is not EMPTY))
                >= MIN_MIX_NON_EMPTY_COMPONENTS)
            else (multipoint
                  if multipoint is not EMPTY
                  else (multisegment
                        if multisegment is not EMPTY
                        else multipolygon)))
