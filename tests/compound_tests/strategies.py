from typing import (Callable,
                    Tuple)

from hypothesis import strategies
from lz.functional import identity

from gon.compound import Compound
from gon.hints import Coordinate
from tests.strategies import (coordinates_strategies,
                              coordinates_to_contours,
                              coordinates_to_polygons,
                              coordinates_to_segments)
from tests.utils import Strategy

CompoundStrategyFactory = Callable[[Strategy[Coordinate]], Strategy[Compound]]
compounds_factories = strategies.sampled_from([coordinates_to_segments,
                                               coordinates_to_contours,
                                               coordinates_to_polygons])


def coordinates_to_geometries(coordinates: Strategy[Coordinate],
                              factory: CompoundStrategyFactory
                              ) -> Strategy[Compound]:
    return factory(coordinates)


compounds = (strategies.builds(coordinates_to_geometries,
                               coordinates_strategies,
                               compounds_factories)
             .flatmap(identity))


def coordinates_to_compounds_tuples(coordinates: Strategy[Coordinate],
                                    *factories: CompoundStrategyFactory
                                    ) -> Strategy[Tuple[Compound, ...]]:
    return strategies.tuples(*[coordinates_to_geometries(coordinates, factory)
                               for factory in factories])


compounds_pairs = (strategies.builds(coordinates_to_compounds_tuples,
                                     coordinates_strategies,
                                     compounds_factories,
                                     compounds_factories)
                   .flatmap(identity))
compounds_triplets = (strategies.builds(coordinates_to_compounds_tuples,
                                        coordinates_strategies,
                                        compounds_factories,
                                        compounds_factories,
                                        compounds_factories)
                      .flatmap(identity))
