from functools import partial

from hypothesis import strategies
from hypothesis_geometry import planar
from lz.functional import pack

from gon.linear import Multisegment
from tests.strategies import (coordinates_strategies,
                              coordinates_to_multisegments,
                              coordinates_to_points,
                              invalid_segments)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

raw_multisegments = (coordinates_strategies
                     .flatmap(partial(planar.multisegments,
                                      min_size=1)))
multisegments = raw_multisegments.map(Multisegment.from_raw)
invalid_multisegments = (strategies.lists(invalid_segments)
                         .map(pack(Multisegment)))
multisegments_strategies = coordinates_strategies.map(
        coordinates_to_multisegments)
multisegments_with_points = (coordinates_strategies
    .flatmap(
        cleave_in_tuples(coordinates_to_multisegments,
                         coordinates_to_points)))
multisegments_pairs = multisegments_strategies.flatmap(to_pairs)
multisegments_triplets = multisegments_strategies.flatmap(to_triplets)
