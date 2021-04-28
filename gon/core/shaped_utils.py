from clipping.hints import Multiregion
from ground.hints import (Multipoint,
                          Multipolygon,
                          Multisegment)

from .compound import Compound
from .empty import EMPTY
from .linear_utils import (unpack_multipoint,
                           unpack_multisegment)


def mix_from_packed_components(multipoint: Multipoint,
                               multisegment: Multisegment,
                               multipolygon: Multipolygon) -> Compound:
    # importing here to avoid cyclic imports
    from .mix import from_mix_components
    return from_mix_components(unpack_multipoint(multipoint),
                               unpack_multisegment(multisegment),
                               unpack_multipolygon(multipolygon))


def from_holeless_mix_components(multipoint: Multipoint,
                                 multisegment: Multisegment,
                                 multiregion: Multiregion) -> Compound:
    # importing here to avoid cyclic imports
    from .mix import from_mix_components
    return from_mix_components(unpack_multipoint(multipoint),
                               unpack_multisegment(multisegment),
                               unpack_multiregion(multiregion))


def unpack_multipolygon(multipolygon: Multipolygon) -> Compound:
    return ((multipolygon
             if len(multipolygon.polygons) > 1
             else multipolygon.polygons[0])
            if multipolygon.polygons
            else EMPTY)


def unpack_multiregion(multiregion: Multiregion) -> Compound:
    # importing here to avoid cyclic imports
    from .polygon import Polygon
    from .multipolygon import Multipolygon
    return ((Multipolygon([Polygon(region) for region in multiregion])
             if len(multiregion) > 1
             else Polygon(multiregion[0]))
            if multiregion
            else EMPTY)
