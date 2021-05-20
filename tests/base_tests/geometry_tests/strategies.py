from hypothesis import strategies

from gon.base import EMPTY
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
                              rational_cosines_sines,
                              to_non_zero_coordinates,
                              to_zero_coordinates)
from tests.utils import (call,
                         cleave_in_tuples,
                         identity,
                         to_constant,
                         to_pairs)

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
non_empty_geometries_factories = (strategies.just(coordinates_to_points)
                                  | non_empty_compounds_factories)
geometries_factories = (strategies.just(empty_compounds_factory)
                        | non_empty_geometries_factories)
geometries_strategies = strategies.builds(call, geometries_factories,
                                          coordinates_strategies)
geometries = geometries_strategies.flatmap(identity)
rational_geometries_with_non_zero_coordinates_pairs = strategies.builds(
        call,
        geometries_factories.map(lambda factory
                                 : cleave_in_tuples(factory,
                                                    to_non_zero_coordinates,
                                                    to_non_zero_coordinates)),
        rational_coordinates_strategies).flatmap(identity)
empty_compounds_with_coordinates_pairs = (
    coordinates_strategies.flatmap(cleave_in_tuples(empty_compounds_factory,
                                                    identity, identity)))
geometries_with_coordinates_pairs = strategies.builds(
        call,
        geometries_factories.map(lambda factory
                                 : cleave_in_tuples(factory,
                                                    to_zero_coordinates,
                                                    identity))
        | geometries_factories.map(lambda factory
                                   : cleave_in_tuples(factory, identity,
                                                      to_zero_coordinates))
        | geometries_factories.map(lambda factory
                                   : cleave_in_tuples(factory, identity,
                                                      identity)),
        coordinates_strategies).flatmap(identity)
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
non_empty_geometries_pairs = (strategies.builds(call,
                                                non_empty_geometries_factories,
                                                coordinates_strategies)
                              .flatmap(to_pairs))
