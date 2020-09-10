from gon.compound import (Compound,
                          Relation)
from gon.degenerate import EMPTY
from gon.discrete import (Multipoint,
                          RawMultipoint)
from .hints import RawMultisegment


def relate_multipoint_to_linear_compound(multipoint: Multipoint,
                                         compound: Compound) -> Relation:
    disjoint = is_subset = True
    for point in multipoint.points:
        if point in compound:
            if disjoint:
                disjoint = False
        elif is_subset:
            is_subset = False
    return (Relation.DISJOINT
            if disjoint
            else (Relation.COMPONENT
                  if is_subset
                  else Relation.TOUCH))


def from_raw_mix_components(raw_multipoint: RawMultipoint,
                            raw_multisegment: RawMultisegment) -> Compound:
    # importing here to avoid cyclic imports
    from gon.mixed.mix import from_mix_components
    return from_mix_components(from_raw_multipoint(raw_multipoint),
                               from_raw_multisegment(raw_multisegment),
                               EMPTY)


def from_raw_multipoint(raw_multipoint: RawMultipoint) -> Multipoint:
    return (Multipoint.from_raw(raw_multipoint)
            if raw_multipoint
            else EMPTY)


def from_raw_multisegment(raw: RawMultisegment) -> Compound:
    # importing here to avoid cyclic imports
    from .segment import Segment
    from .multisegment import Multisegment
    return ((Segment.from_raw(raw[0])
             if len(raw) == 1
             else Multisegment.from_raw(raw))
            if raw
            else EMPTY)
