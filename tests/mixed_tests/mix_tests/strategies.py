from bentley_ottmann.planar import segments_cross_or_overlap
from hypothesis import strategies

from gon.base import (EMPTY,
                      Mix,
                      Multipoint,
                      Multipolygon,
                      Multisegment,
                      Segment)
from tests.strategies import (coordinates_strategies,
                              coordinates_to_mixes,
                              coordinates_to_multipoints,
                              coordinates_to_multipolygons,
                              coordinates_to_multisegments,
                              coordinates_to_points,
                              invalid_multipoints,
                              invalid_multipolygons,
                              invalid_multisegments)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         sub_lists,
                         to_pairs,
                         to_triplets)

mixes = coordinates_strategies.flatmap(coordinates_to_mixes)
empty_geometries = strategies.just(EMPTY)
multipoints = coordinates_strategies.flatmap(coordinates_to_multipoints)
multisegments = coordinates_strategies.flatmap(coordinates_to_multisegments)
multipolygons = coordinates_strategies.flatmap(coordinates_to_multipolygons)


def multipolygon_to_invalid_mix(multipolygon: Multipolygon) -> Strategy[Mix]:
    vertices = sum([sum((hole.vertices for hole in polygon.holes),
                        polygon.border.vertices)
                    for polygon in multipolygon.polygons], [])
    edges = sum([polygon.edges for polygon in multipolygon.polygons], [])
    segments = edges + [Segment(vertices[index - 1], vertices[index])
                        for index in range(len(vertices))]
    return strategies.builds(
            Mix,
            empty_geometries | (sub_lists(vertices).map(Multipoint)),
            sub_lists(segments)
            .filter(lambda candidates: segments_cross_or_overlap(edges
                                                                 + candidates))
            .map(Multisegment),
            strategies.just(multipolygon))


invalid_mixes = (multipolygons.flatmap(multipolygon_to_invalid_mix)
                 | strategies.builds(Mix, empty_geometries | multipoints,
                                     empty_geometries, empty_geometries)
                 | strategies.builds(Mix, empty_geometries,
                                     empty_geometries | multisegments,
                                     empty_geometries)
                 | strategies.builds(Mix, empty_geometries, empty_geometries,
                                     empty_geometries | multipolygons)
                 | strategies.builds(Mix, invalid_multipoints,
                                     empty_geometries | multisegments,
                                     multipolygons)
                 | strategies.builds(Mix, invalid_multipoints, multisegments,
                                     empty_geometries | multipolygons)
                 | strategies.builds(Mix, empty_geometries | multipoints,
                                     invalid_multisegments, multipolygons)
                 | strategies.builds(Mix, multipoints, invalid_multisegments,
                                     empty_geometries | multipolygons)
                 | strategies.builds(Mix, multipoints,
                                     empty_geometries | multisegments,
                                     invalid_multipolygons)
                 | strategies.builds(Mix, empty_geometries | multipoints,
                                     multisegments, invalid_multipolygons))
mixes_with_points = (coordinates_strategies
                     .flatmap(cleave_in_tuples(coordinates_to_mixes,
                                               coordinates_to_points)))
mixes_strategies = coordinates_strategies.map(coordinates_to_mixes)
mixes_pairs = mixes_strategies.flatmap(to_pairs)
mixes_triplets = mixes_strategies.flatmap(to_triplets)
