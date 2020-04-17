from typing import (Callable,
                    Tuple)

from hypothesis import strategies
from lz.functional import identity

from gon.geometry import Geometry
from gon.hints import Coordinate
from tests.strategies import (coordinates_strategies,
                              coordinates_to_contours,
                              coordinates_to_points,
                              coordinates_to_polygons,
                              coordinates_to_segments)
from tests.utils import Strategy

GeometryStrategyFactory = Callable[[Strategy[Coordinate]], Strategy[Geometry]]
geometries_factories = strategies.sampled_from([coordinates_to_points,
                                                coordinates_to_segments,
                                                coordinates_to_contours,
                                                coordinates_to_polygons])


def coordinates_to_geometries(coordinates: Strategy[Coordinate],
                              factory: GeometryStrategyFactory
                              ) -> Strategy[Geometry]:
    return factory(coordinates)


geometries = (strategies.builds(coordinates_to_geometries,
                                coordinates_strategies,
                                geometries_factories)
              .flatmap(identity))


def coordinates_to_geometries_pairs(coordinates: Strategy[Coordinate],
                                    first_factory: GeometryStrategyFactory,
                                    second_factory: GeometryStrategyFactory
                                    ) -> Strategy[Tuple[Geometry, Geometry]]:
    return strategies.tuples(coordinates_to_geometries(coordinates,
                                                       first_factory),
                             coordinates_to_geometries(coordinates,
                                                       second_factory))


geometries_pairs = (strategies.builds(coordinates_to_geometries_pairs,
                                      coordinates_strategies,
                                      geometries_factories,
                                      geometries_factories)
                    .flatmap(identity))
