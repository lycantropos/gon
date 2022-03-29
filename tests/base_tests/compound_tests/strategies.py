from itertools import repeat

from hypothesis import strategies

from gon.base import EMPTY
from tests.strategies import (angles,
                              coordinates_strategies,
                              coordinates_to_contours,
                              coordinates_to_maybe_linear_geometries,
                              coordinates_to_maybe_multipoints,
                              coordinates_to_maybe_shaped_geometries,
                              coordinates_to_mixes,
                              coordinates_to_multipoints,
                              coordinates_to_multipolygons,
                              coordinates_to_multisegments,
                              coordinates_to_points,
                              coordinates_to_polygons,
                              coordinates_to_segments)
from tests.utils import (combine_factories,
                         compound_to_compound_with_multipoint,
                         factories_to_values,
                         identity,
                         to_constant,
                         to_triplets)

empty_compounds = strategies.just(EMPTY)
equidimensional_compounds_strategies = (
        coordinates_strategies.map(coordinates_to_maybe_multipoints)
        | coordinates_strategies.map(coordinates_to_maybe_linear_geometries)
        | coordinates_strategies.map(coordinates_to_maybe_shaped_geometries)
)
equidimensional_compounds_triplets = (equidimensional_compounds_strategies
                                      .flatmap(to_triplets))
indexables_factories = strategies.sampled_from([coordinates_to_multisegments,
                                                coordinates_to_contours,
                                                coordinates_to_polygons,
                                                coordinates_to_multipolygons,
                                                coordinates_to_mixes])
non_empty_compounds_factories = (
        strategies.sampled_from([coordinates_to_multipoints,
                                 coordinates_to_segments])
        | indexables_factories
)
non_empty_geometries_factories = (strategies.just(coordinates_to_points)
                                  | non_empty_compounds_factories)
compounds_factories = (strategies.just(to_constant(empty_compounds))
                       | non_empty_compounds_factories)
indexables = factories_to_values(indexables_factories, coordinates_strategies)
indexables_with_non_empty_geometries = (
    factories_to_values(combine_factories(indexables_factories,
                                          non_empty_geometries_factories),
                        coordinates_strategies)
)
non_empty_compounds = factories_to_values(non_empty_compounds_factories,
                                          coordinates_strategies)
non_empty_compounds_pairs = factories_to_values(
        combine_factories(*repeat(non_empty_compounds_factories,
                                  times=2)),
        coordinates_strategies
)
compounds = factories_to_values(compounds_factories, coordinates_strategies)
non_empty_compounds_with_coordinates_pairs = (
    factories_to_values(combine_factories(non_empty_compounds_factories,
                                          *repeat(strategies.just(identity),
                                                  times=2)),
                        coordinates_strategies)
)
non_empty_compounds_with_angles = strategies.tuples(non_empty_compounds,
                                                    angles)
non_empty_compounds_with_points = factories_to_values(
        combine_factories(non_empty_compounds_factories,
                          strategies.just(coordinates_to_points)),
        coordinates_strategies
)
compounds_with_points = factories_to_values(
        combine_factories(compounds_factories,
                          strategies.just(coordinates_to_points)),
        coordinates_strategies
)
empty_compounds_with_compounds = strategies.tuples(empty_compounds, compounds)
compounds_pairs = (
        (non_empty_compounds
         .map(compound_to_compound_with_multipoint))
        | factories_to_values(combine_factories(*repeat(compounds_factories,
                                                        times=2)),
                              coordinates_strategies)
)
compounds_triplets = factories_to_values(
        combine_factories(*repeat(compounds_factories,
                                  times=3)),
        coordinates_strategies
)
