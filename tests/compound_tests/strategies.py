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

CompoundsFactory = Callable[[Strategy[Coordinate]], Strategy[Compound]]
indexables_factories = strategies.sampled_from([coordinates_to_contours,
                                                coordinates_to_polygons])
compounds_factories = (strategies.just(coordinates_to_segments)
                       | indexables_factories)


def coordinates_to_compounds(coordinates: Strategy[Coordinate],
                             factory: CompoundsFactory) -> Strategy[Compound]:
    return factory(coordinates)


indexables = (strategies.builds(coordinates_to_compounds,
                                coordinates_strategies,
                                indexables_factories)
              .flatmap(identity))
compounds = (strategies.builds(coordinates_to_compounds,
                               coordinates_strategies,
                               compounds_factories)
             .flatmap(identity))


def coordinates_to_compounds_tuples(coordinates: Strategy[Coordinate],
                                    *factories: CompoundsFactory
                                    ) -> Strategy[Tuple[Compound, ...]]:
    return strategies.tuples(*[coordinates_to_compounds(coordinates, factory)
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
