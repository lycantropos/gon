from collections import OrderedDict
from itertools import chain
from typing import (Callable,
                    Iterable,
                    Tuple)

from hypothesis import strategies

from gon.compound import Compound
from gon.degenerate import EMPTY
from gon.discrete import Multipoint
from gon.hints import Coordinate
from gon.linear import (Contour,
                        Multisegment,
                        Segment)
from gon.mixed import Mix
from gon.primitive import Point
from gon.shaped import (Multipolygon,
                        Polygon)
from tests.strategies import (coordinates_strategies,
                              coordinates_to_contours,
                              coordinates_to_mixes,
                              coordinates_to_multipoints,
                              coordinates_to_multipolygons,
                              coordinates_to_multisegments,
                              coordinates_to_points,
                              coordinates_to_polygons,
                              coordinates_to_segments,
                              rational_coordinates_strategies)
from tests.utils import (Strategy,
                         flatten,
                         identity,
                         to_constant)

CompoundsFactory = Callable[[Strategy[Coordinate]], Strategy[Compound]]

empty_compounds = strategies.just(EMPTY)
indexables_factories = strategies.sampled_from([coordinates_to_multisegments,
                                                coordinates_to_contours,
                                                coordinates_to_polygons,
                                                coordinates_to_multipolygons,
                                                coordinates_to_mixes])
non_empty_compounds_factories = (
        strategies.sampled_from([coordinates_to_multipoints,
                                 coordinates_to_segments])
        | indexables_factories)
compounds_factories = (strategies.just(to_constant(empty_compounds))
                       | non_empty_compounds_factories)


def coordinates_to_compounds(coordinates: Strategy[Coordinate],
                             factory: CompoundsFactory) -> Strategy[Compound]:
    return factory(coordinates)


indexables = (strategies.builds(coordinates_to_compounds,
                                coordinates_strategies,
                                indexables_factories)
              .flatmap(identity))
non_empty_compounds = (strategies.builds(coordinates_to_compounds,
                                         coordinates_strategies,
                                         non_empty_compounds_factories)
                       .flatmap(identity))
compounds = (strategies.builds(coordinates_to_compounds,
                               coordinates_strategies, compounds_factories)
             .flatmap(identity))
rational_compounds = (strategies.builds(coordinates_to_compounds,
                                        rational_coordinates_strategies,
                                        compounds_factories)
                      .flatmap(identity))
empty_compounds_with_compounds = strategies.tuples(empty_compounds, compounds)


def coordinates_to_compounds_with_points(coordinates: Strategy[Coordinate],
                                         factory: CompoundsFactory
                                         ) -> Strategy[Tuple[Compound, Point]]:
    return strategies.tuples(factory(coordinates),
                             coordinates_to_points(coordinates))


compounds_with_points = (
    (strategies.builds(coordinates_to_compounds_with_points,
                       coordinates_strategies,
                       compounds_factories)
     .flatmap(identity)))


def coordinates_to_compounds_tuples(coordinates: Strategy[Coordinate],
                                    *factories: CompoundsFactory
                                    ) -> Strategy[Tuple[Compound, ...]]:
    return strategies.tuples(*[coordinates_to_compounds(coordinates, factory)
                               for factory in factories])


def compound_to_compound_with_multipoint(compound: Compound
                                         ) -> Tuple[Compound, Multipoint]:
    return compound, Multipoint(*compound_to_points(compound))


def compound_to_points(compound: Compound) -> Iterable[Point]:
    if isinstance(compound, Multipoint):
        return compound.points
    elif isinstance(compound, Segment):
        return [compound.start, compound.end]
    elif isinstance(compound, Multisegment):
        return list(flatten((segment.start, segment.end)
                            for segment in compound.segments))
    elif isinstance(compound, Contour):
        return compound.vertices
    elif isinstance(compound, Polygon):
        return OrderedDict.fromkeys(chain(compound.border.vertices,
                                          flatten(hole.vertices
                                                  for hole in compound.holes)))
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


rational_compounds_pairs = (strategies.builds(coordinates_to_compounds_tuples,
                                              rational_coordinates_strategies,
                                              compounds_factories,
                                              compounds_factories)
                            .flatmap(identity))
rational_compounds_triplets = (
    strategies.builds(coordinates_to_compounds_tuples,
                      rational_coordinates_strategies,
                      compounds_factories,
                      compounds_factories,
                      compounds_factories).flatmap(identity))
compounds_pairs = ((non_empty_compounds
                    .map(compound_to_compound_with_multipoint))
                   | (strategies.builds(coordinates_to_compounds_tuples,
                                        coordinates_strategies,
                                        compounds_factories,
                                        compounds_factories)
                      .flatmap(identity)))
compounds_triplets = (strategies.builds(coordinates_to_compounds_tuples,
                                        coordinates_strategies,
                                        compounds_factories,
                                        compounds_factories,
                                        compounds_factories)
                      .flatmap(identity))
