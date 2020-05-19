from collections import OrderedDict
from itertools import chain
from typing import (Callable,
                    Tuple)

from hypothesis import strategies
from lz.functional import identity

from gon.compound import Compound
from gon.discrete import Multipoint
from gon.hints import Coordinate
from gon.linear import (Contour,
                        Segment)
from gon.shaped import Polygon
from tests.strategies import (coordinates_strategies,
                              coordinates_to_contours,
                              coordinates_to_multipoints,
                              coordinates_to_polygons,
                              coordinates_to_segments)
from tests.utils import Strategy

CompoundsFactory = Callable[[Strategy[Coordinate]], Strategy[Compound]]
indexables_factories = strategies.sampled_from([coordinates_to_contours,
                                                coordinates_to_polygons])
compounds_factories = (strategies.sampled_from([coordinates_to_multipoints,
                                                coordinates_to_segments])
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


def compound_to_compound_with_multipoint(compound: Compound
                                         ) -> Tuple[Compound, Multipoint]:
    if isinstance(compound, Multipoint):
        return compound, compound
    elif isinstance(compound, Segment):
        return compound, Multipoint(compound.start, compound.end)
    elif isinstance(compound, Contour):
        return compound, Multipoint(*compound.vertices)
    elif isinstance(compound, Polygon):
        unique_vertices = OrderedDict.fromkeys(
                chain(compound.border.vertices,
                      chain.from_iterable(hole.vertices
                                          for hole in compound.holes)))
        return compound, Multipoint(*unique_vertices)
    else:
        raise TypeError('Unsupported geometry type: {type}.'
                        .format(type=type(compound)))


compounds_pairs = (compounds.map(compound_to_compound_with_multipoint)
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
