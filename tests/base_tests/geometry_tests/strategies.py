from itertools import repeat

from hypothesis import strategies

from gon.base import EMPTY
from tests.strategies import (angles,
                              coordinates_strategies,
                              coordinates_to_contours,
                              coordinates_to_mixes,
                              coordinates_to_multipoints,
                              coordinates_to_multipolygons,
                              coordinates_to_multisegments,
                              coordinates_to_points,
                              coordinates_to_polygons,
                              coordinates_to_segments,
                              to_non_zero_coordinates,
                              to_zero_coordinates)
from tests.utils import (cleave_in_tuples,
                         combine_factories,
                         factories_to_values,
                         identity,
                         to_constant)

empty_compounds = strategies.just(EMPTY)
empty_compounds_factory = to_constant(empty_compounds)
non_empty_compounds_factories = (
    strategies.sampled_from([coordinates_to_multipoints,
                             coordinates_to_segments,
                             coordinates_to_multisegments,
                             coordinates_to_contours,
                             coordinates_to_polygons,
                             coordinates_to_multipolygons,
                             coordinates_to_mixes])
)
non_empty_geometries_factories = (strategies.just(coordinates_to_points)
                                  | non_empty_compounds_factories)
geometries_factories = (strategies.just(empty_compounds_factory)
                        | non_empty_geometries_factories)
geometries = factories_to_values(geometries_factories, coordinates_strategies)
geometries_with_non_zero_coordinates_pairs = factories_to_values(
        combine_factories(geometries_factories,
                          *repeat(strategies.just(to_non_zero_coordinates),
                                  times=2)),
        coordinates_strategies
)
empty_compounds_with_coordinates_pairs = (
    coordinates_strategies.flatmap(cleave_in_tuples(empty_compounds_factory,
                                                    identity, identity))
)
geometries_with_coordinates_pairs = factories_to_values(
        combine_factories(geometries_factories,
                          *repeat(strategies.sampled_from([to_zero_coordinates,
                                                           identity]),
                                  times=2)),
        coordinates_strategies
)
geometries_with_points = factories_to_values(
        combine_factories(geometries_factories,
                          strategies.just(coordinates_to_points)),
        coordinates_strategies
)
geometries_points_with_angles = strategies.tuples(geometries_with_points,
                                                  angles)
geometries_points_with_angles_pairs = strategies.tuples(geometries_with_points,
                                                        angles, angles)
non_empty_geometries_pairs = factories_to_values(
        combine_factories(*repeat(non_empty_geometries_factories,
                                  times=2)),
        coordinates_strategies
)
