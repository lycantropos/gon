from itertools import chain
from typing import (Iterable,
                    Tuple)

from hypothesis import strategies

from gon.base import (EMPTY,
                      Compound,
                      Contour,
                      Mix,
                      Multipoint,
                      Multipolygon,
                      Multisegment,
                      Point,
                      Polygon,
                      Segment)
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
                              rational_coordinates_strategies,
                              rational_cosines_sines)
from tests.utils import (call,
                         cleave_in_tuples,
                         flatten,
                         identity,
                         pack,
                         to_constant,
                         to_pairs,
                         to_triplets,
                         to_unique_ever_seen)

empty_compounds = strategies.just(EMPTY)
rational_equidimensional_compounds_strategies = (
        rational_coordinates_strategies.map(coordinates_to_maybe_multipoints)
        | (rational_coordinates_strategies
           .map(coordinates_to_maybe_linear_geometries))
        | (rational_coordinates_strategies
           .map(coordinates_to_maybe_shaped_geometries)))
rational_equidimensional_compounds_triplets = (
    rational_equidimensional_compounds_strategies.flatmap(to_triplets))
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
rational_compounds = (strategies.builds(call, compounds_factories,
                                        rational_coordinates_strategies)
                      .flatmap(identity))
rational_non_empty_compounds_with_coordinates_pairs = (
    (strategies.builds(call,
                       non_empty_compounds_factories
                       .map(lambda factory: cleave_in_tuples(factory, identity,
                                                             identity)),
                       rational_coordinates_strategies)
     .flatmap(identity)))
rational_non_empty_compounds = (
    strategies.builds(call, non_empty_compounds_factories,
                      rational_coordinates_strategies).flatmap(identity))
rational_non_empty_compounds_with_cosines_sines = strategies.tuples(
        rational_non_empty_compounds, rational_cosines_sines)
rational_non_empty_compounds_with_points = (
    (strategies.builds(call,
                       non_empty_compounds_factories
                       .map(lambda factory
                            : cleave_in_tuples(factory,
                                               coordinates_to_points)),
                       rational_coordinates_strategies)
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


def compound_to_compound_with_multipoint(compound: Compound
                                         ) -> Tuple[Compound, Multipoint]:
    return (compound, Multipoint(list(to_unique_ever_seen(compound_to_points(
            compound)))))


def compound_to_points(compound: Compound) -> Iterable[Point]:
    if isinstance(compound, Multipoint):
        return compound.points
    elif isinstance(compound, Segment):
        return [compound.start, compound.end]
    elif isinstance(compound, Multisegment):
        return flatten((segment.start, segment.end)
                       for segment in compound.segments)
    elif isinstance(compound, Contour):
        return compound.vertices
    elif isinstance(compound, Polygon):
        return chain(compound.border.vertices,
                     flatten(hole.vertices for hole in compound.holes))
    elif isinstance(compound, Multipolygon):
        return flatten(compound_to_points(polygon)
                       for polygon in compound.polygons)
    elif isinstance(compound, Mix):
        return chain([]
                     if compound.multipoint is EMPTY
                     else compound_to_points(compound.multipoint),
                     []
                     if compound.multisegment is EMPTY
                     else compound_to_points(compound.multisegment),
                     []
                     if compound.multipolygon is EMPTY
                     else compound_to_points(compound.multipolygon))
    else:
        raise TypeError('Unsupported geometry type: {type}.'
                        .format(type=type(compound)))


rational_compounds_pairs = (strategies.builds(call,
                                              to_pairs(compounds_factories)
                                              .map(pack(cleave_in_tuples)),
                                              rational_coordinates_strategies)
                            .flatmap(identity))
rational_compounds_triplets = (
    strategies.builds(call,
                      to_triplets(compounds_factories)
                      .map(pack(cleave_in_tuples)),
                      rational_coordinates_strategies).flatmap(identity))
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
