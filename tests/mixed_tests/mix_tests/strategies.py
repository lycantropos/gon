from hypothesis import strategies

from gon.degenerate import Empty
from gon.mixed import Mix
from tests.strategies import (coordinates_strategies,
                              coordinates_to_mixes,
                              coordinates_to_multipoints,
                              coordinates_to_multipolygons,
                              coordinates_to_multisegments,
                              coordinates_to_points,
                              coordinates_to_raw_mixes,
                              invalid_multipoints,
                              invalid_multipolygons,
                              invalid_multisegments)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

raw_mixes = coordinates_strategies.flatmap(coordinates_to_raw_mixes)
mixes = coordinates_strategies.flatmap(coordinates_to_mixes)
empty_geometries = strategies.builds(Empty)
multipoints = coordinates_strategies.flatmap(coordinates_to_multipoints)
multisegments = coordinates_strategies.flatmap(coordinates_to_multisegments)
multipolygons = coordinates_strategies.map(coordinates_to_multipolygons)
invalid_mixes = (strategies.builds(Mix, empty_geometries | multipoints,
                                   empty_geometries, empty_geometries)
                 | strategies.builds(Mix, empty_geometries,
                                     empty_geometries | multisegments,
                                     empty_geometries)
                 | strategies.builds(Mix, empty_geometries, empty_geometries,
                                     empty_geometries | multipolygons)
                 | strategies.builds(Mix, invalid_multipoints,
                                     empty_geometries | multisegments,
                                     multipolygons)
                 | strategies.builds(Mix, invalid_multipoints, multisegments,
                                     empty_geometries | multipolygons)
                 | strategies.builds(Mix, empty_geometries | multipoints,
                                     invalid_multisegments, multipolygons)
                 | strategies.builds(Mix, multipoints, invalid_multisegments,
                                     empty_geometries | multipolygons)
                 | strategies.builds(Mix, multipoints,
                                     empty_geometries | multisegments,
                                     invalid_multipolygons)
                 | strategies.builds(Mix, empty_geometries | multipoints,
                                     multisegments, invalid_multipolygons))
mixes_with_points = (coordinates_strategies
                     .flatmap(cleave_in_tuples(coordinates_to_mixes,
                                               coordinates_to_points)))
mixes_strategies = coordinates_strategies.map(coordinates_to_mixes)
mixes_pairs = mixes_strategies.flatmap(to_pairs)
mixes_triplets = mixes_strategies.flatmap(to_triplets)
