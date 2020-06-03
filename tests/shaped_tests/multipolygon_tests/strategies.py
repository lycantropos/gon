from functools import partial
from itertools import repeat

from hypothesis import strategies
from hypothesis_geometry import planar
from lz.functional import pack

from gon.shaped import Multipolygon, Polygon
from tests.strategies import (coordinates_strategies,
                              coordinates_to_multipolygons,
                              coordinates_to_points,
                              coordinates_to_polygons, invalid_polygons)
from tests.utils import (cleave_in_tuples,
                         to_pairs,
                         to_triplets)

raw_multipolygons = (coordinates_strategies
                     .flatmap(partial(planar.multipolygons,
                                      min_size=1)))
multipolygons = raw_multipolygons.map(Multipolygon.from_raw)
polygons = (coordinates_strategies.flatmap(coordinates_to_polygons)
            .map(Polygon.from_raw))
repeated_polygons = (strategies.builds(repeat, polygons,
                                       strategies.integers(1, 100))
                     .map(list))
invalid_multipolygons = (strategies.builds(pack(Multipolygon),
                                           strategies.lists(invalid_polygons)
                                           | repeated_polygons))
multipolygons_strategies = (coordinates_strategies
                            .map(coordinates_to_multipolygons))
multipolygons_pairs = multipolygons_strategies.flatmap(to_pairs)
multipolygons_triplets = multipolygons_strategies.flatmap(to_triplets)
multipolygons_with_points = (
    coordinates_strategies.flatmap(
            cleave_in_tuples(coordinates_to_multipolygons,
                             coordinates_to_points)))
