from .compound import Compound
from .degenerate import EMPTY
from .linear_utils import (from_raw_multipoint,
                           from_raw_multisegment)
from .raw import (RawMultipoint,
                  RawMultipolygon,
                  RawMultiregion,
                  RawMultisegment)


def from_raw_mix_components(raw_multipoint: RawMultipoint,
                            raw_multisegment: RawMultisegment,
                            raw_multipolygon: RawMultipolygon) -> Compound:
    # importing here to avoid cyclic imports
    from .mix import from_mix_components
    return from_mix_components(from_raw_multipoint(raw_multipoint),
                               from_raw_multisegment(raw_multisegment),
                               from_raw_multipolygon(raw_multipolygon))


def from_raw_holeless_mix_components(raw_multipoint: RawMultipoint,
                                     raw_multisegment: RawMultisegment,
                                     raw_multiregion: RawMultiregion
                                     ) -> Compound:
    # importing here to avoid cyclic imports
    from .mix import from_mix_components
    return from_mix_components(from_raw_multipoint(raw_multipoint),
                               from_raw_multisegment(raw_multisegment),
                               from_raw_multiregion(raw_multiregion))


def from_raw_multipolygon(raw: RawMultipolygon) -> Compound:
    # importing here to avoid cyclic imports
    from .polygon import Polygon
    from .multipolygon import Multipolygon
    return ((Polygon.from_raw(raw[0])
             if len(raw) == 1
             else Multipolygon.from_raw(raw))
            if raw else EMPTY)


def from_raw_multiregion(raw: RawMultiregion) -> Compound:
    # importing here to avoid cyclic imports
    from .polygon import Polygon
    from .multipolygon import Multipolygon
    return ((Polygon.from_raw((raw[0], []))
             if len(raw) == 1
             else Multipolygon.from_raw([(raw_region, [])
                                         for raw_region in raw]))
            if raw else EMPTY)
