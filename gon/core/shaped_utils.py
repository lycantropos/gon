from clipping.hints import Multiregion
from ground.hints import (Multipoint,
                          Multipolygon,
                          Multisegment)

from .compound import Compound
from .degenerate import EMPTY
from .linear_utils import (unfold_multipoint,
                           unfold_multisegment)


def mix_from_unfolded_components(multipoint: Multipoint,
                                 multisegment: Multisegment,
                                 multipolygon: Multipolygon) -> Compound:
    # importing here to avoid cyclic imports
    from .mix import from_mix_components
    return from_mix_components(unfold_multipoint(multipoint),
                               unfold_multisegment(multisegment),
                               unfold_multipolygon(multipolygon))


def from_holeless_mix_components(multipoint: Multipoint,
                                 multisegment: Multisegment,
                                 multiregion: Multiregion) -> Compound:
    # importing here to avoid cyclic imports
    from .mix import from_mix_components
    return from_mix_components(unfold_multipoint(multipoint),
                               unfold_multisegment(multisegment),
                               from_raw_multiregion(multiregion))


def unfold_multipolygon(multipolygon: Multipolygon) -> Compound:
    return multipolygon if multipolygon.polygons else EMPTY


def from_raw_multiregion(multiregion: Multiregion) -> Compound:
    # importing here to avoid cyclic imports
    from .polygon import Polygon
    from .multipolygon import Multipolygon
    return (Multipolygon([Polygon(region, []) for region in multiregion])
            if multiregion else EMPTY)
