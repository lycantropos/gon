from typing import Callable

from hypothesis import strategies

from gon.compound import Shaped
from gon.hints import Coordinate
from tests.strategies import (coordinates_strategies,
                              coordinates_to_multipolygons,
                              coordinates_to_polygons)
from tests.utils import (Strategy,
                         identity)

ShapedGeometriesFactory = Callable[[Strategy[Coordinate]], Strategy[Shaped]]
shaped_geometries_factories = strategies.sampled_from(
        [coordinates_to_polygons, coordinates_to_multipolygons])


def coordinates_to_shaped_geometries(coordinates: Strategy[Coordinate],
                                     factory: ShapedGeometriesFactory
                                     ) -> Strategy[Shaped]:
    return factory(coordinates)


shaped_geometries = (strategies.builds(coordinates_to_shaped_geometries,
                                       coordinates_strategies,
                                       shaped_geometries_factories)
                     .flatmap(identity))
