from hypothesis import strategies

from gon.base import EMPTY
from tests.strategies import (coordinates_strategies,
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
                              coordinates_to_segments,
                              rational_cosines_sines)
from tests.utils import (call,
                         cleave_in_tuples,
                         compound_to_compound_with_multipoint,
                         identity,
                         pack,
                         to_constant,
                         to_pairs,
                         to_triplets)

empty_compounds = strategies.just(EMPTY)
equidimensional_compounds_strategies = (
        coordinates_strategies.map(coordinates_to_maybe_multipoints)
        | coordinates_strategies.map(coordinates_to_maybe_linear_geometries)
        | coordinates_strategies.map(coordinates_to_maybe_shaped_geometries))
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
        | indexables_factories)
non_empty_geometries_factories = (strategies.just(coordinates_to_points)
                                  | non_empty_compounds_factories)
compounds_factories = (strategies.just(to_constant(empty_compounds))
                       | non_empty_compounds_factories)
indexables = (strategies.builds(call, indexables_factories,
                                coordinates_strategies)
              .flatmap(identity))
indexables_with_non_empty_geometries = strategies.builds(
        call,
        (strategies.tuples(indexables_factories,
                           non_empty_geometries_factories)
         .map(pack(cleave_in_tuples))),
        coordinates_strategies).flatmap(identity)
non_empty_compounds_strategies = strategies.builds(
        call, non_empty_compounds_factories, coordinates_strategies)
non_empty_compounds = non_empty_compounds_strategies.flatmap(identity)
non_empty_compounds_pairs = non_empty_compounds_strategies.flatmap(to_pairs)
compounds = (strategies.builds(call, compounds_factories,
                               coordinates_strategies)
             .flatmap(identity))
non_empty_compounds_with_coordinates_pairs = (
    (strategies.builds(call,
                       non_empty_compounds_factories
                       .map(lambda factory: cleave_in_tuples(factory, identity,
                                                             identity)),
                       coordinates_strategies)
     .flatmap(identity)))
non_empty_compounds_with_cosines_sines = strategies.tuples(
        non_empty_compounds, rational_cosines_sines)
non_empty_compounds_with_points = (
    (strategies.builds(call,
                       non_empty_compounds_factories
                       .map(lambda factory
                            : cleave_in_tuples(factory,
                                               coordinates_to_points)),
                       coordinates_strategies)
     .flatmap(identity)))
compounds_with_points = (
    (strategies.builds(call,
                       compounds_factories
                       .map(lambda factory
                            : cleave_in_tuples(factory,
                                               coordinates_to_points)),
                       coordinates_strategies)
     .flatmap(identity)))
empty_compounds_with_compounds = strategies.tuples(empty_compounds, compounds)
compounds_pairs = ((non_empty_compounds
                    .map(compound_to_compound_with_multipoint))
                   | (strategies.builds(call,
                                        to_pairs(compounds_factories)
                                        .map(pack(cleave_in_tuples)),
                                        coordinates_strategies)
                      .flatmap(identity)))
compounds_triplets = (strategies.builds(call,
                                        to_triplets(compounds_factories)
                                        .map(pack(cleave_in_tuples)),
                                        coordinates_strategies)
                      .flatmap(identity))
