from typing import Callable

from hypothesis import strategies

from gon.compound import Compound
from gon.degenerate import EMPTY
from gon.hints import Coordinate
from tests.strategies import (coordinates_strategies,
                              coordinates_to_contours,
                              coordinates_to_mixes,
                              coordinates_to_multipoints,
                              coordinates_to_multipolygons,
                              coordinates_to_multisegments,
                              coordinates_to_points,
                              coordinates_to_polygons,
                              coordinates_to_segments,
                              rational_coordinates_strategies,
                              rational_cosines_sines)
from tests.utils import (Strategy,
                         call,
                         cleave_in_tuples,
                         identity,
                         to_constant)

CompoundsFactory = Callable[[Strategy[Coordinate]], Strategy[Compound]]

empty_compounds = strategies.just(EMPTY)
empty_compounds_factory = to_constant(empty_compounds)
non_empty_compounds_factories = (
    strategies.sampled_from([coordinates_to_multipoints,
                             coordinates_to_segments,
                             coordinates_to_multisegments,
                             coordinates_to_contours,
                             coordinates_to_polygons,
                             coordinates_to_multipolygons,
                             coordinates_to_mixes]))
geometries_factories = (strategies.sampled_from([empty_compounds_factory,
                                                 coordinates_to_points])
                        | non_empty_compounds_factories)
geometries = (strategies.builds(call, geometries_factories,
                                coordinates_strategies)
              .flatmap(identity))
empty_compounds_with_coordinates_pairs = (
    coordinates_strategies.flatmap(cleave_in_tuples(empty_compounds_factory,
                                                    identity, identity)))
geometries_with_coordinates_pairs = (
    (strategies.builds(call,
                       geometries_factories
                       .map(lambda factory: cleave_in_tuples(factory, identity,
                                                             identity)),
                       coordinates_strategies)
     .flatmap(identity)))
rational_geometries_with_points = (
    (strategies.builds(call,
                       geometries_factories
                       .map(lambda factory
                            : cleave_in_tuples(factory,
                                               coordinates_to_points)),
                       rational_coordinates_strategies)
     .flatmap(identity)))
rational_geometries_points_with_cosines_sines = strategies.tuples(
        rational_geometries_with_points, rational_cosines_sines)
rational_geometries_points_with_cosines_sines_pairs = strategies.tuples(
        rational_geometries_with_points, rational_cosines_sines,
        rational_cosines_sines)
