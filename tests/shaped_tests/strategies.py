from typing import Callable

from hypothesis import strategies
from lz.functional import identity

from gon.compound import Shaped
from gon.hints import Coordinate
from tests.strategies import (coordinates_strategies,
                              coordinates_to_polygons)
from tests.utils import Strategy

ShapedGeometriesFactory = Callable[[Strategy[Coordinate]], Strategy[Shaped]]
shaped_geometries_factories = strategies.just(coordinates_to_polygons)


def coordinates_to_shaped_geometries(coordinates: Strategy[Coordinate],
                                     factory: ShapedGeometriesFactory
                                     ) -> Strategy[Shaped]:
    return factory(coordinates)


shaped_geometries = (strategies.builds(coordinates_to_shaped_geometries,
                                       coordinates_strategies,
                                       shaped_geometries_factories)
                     .flatmap(identity))
