from typing import Callable

from hypothesis import strategies
from lz.functional import identity

from gon.compound import Linear
from gon.hints import Coordinate
from tests.strategies import (coordinates_strategies,
                              coordinates_to_contours,
                              coordinates_to_multisegments,
                              coordinates_to_segments)
from tests.utils import Strategy

LinearGeometriesFactory = Callable[[Strategy[Coordinate]], Strategy[Linear]]
linear_geometries_factories = strategies.sampled_from(
        [coordinates_to_segments, coordinates_to_multisegments,
         coordinates_to_contours])


def coordinates_to_linear_geometries(coordinates: Strategy[Coordinate],
                                     factory: LinearGeometriesFactory
                                     ) -> Strategy[Linear]:
    return factory(coordinates)


linear_geometries = (strategies.builds(coordinates_to_linear_geometries,
                                       coordinates_strategies,
                                       linear_geometries_factories)
                     .flatmap(identity))
