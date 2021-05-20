from itertools import chain

from hypothesis import strategies

from gon.base import (EMPTY,
                      Mix,
                      Multipoint,
                      Multisegment,
                      Segment,
                      Shaped)
from gon.hints import Scalar
from tests.strategies import (coordinates_strategies,
                              coordinates_to_linear_geometries,
                              coordinates_to_mixes,
                              coordinates_to_multipoints,
                              coordinates_to_points,
                              coordinates_to_shaped_geometries,
                              invalid_linear_geometries,
                              invalid_multipoints,
                              invalid_shaped_geometries)
from tests.utils import (Strategy,
                         cleave_in_tuples,
                         flatten,
                         shaped_to_polygons,
                         sub_lists,
                         to_pairs,
                         to_polygon_diagonals,
                         to_rational_segment,
                         to_triplets)

mixes = coordinates_strategies.flatmap(coordinates_to_mixes)
empty_geometries = strategies.just(EMPTY)
multipoints = coordinates_strategies.flatmap(coordinates_to_multipoints)
linear_geometries = (coordinates_strategies
                     .flatmap(coordinates_to_linear_geometries))
shaped_geometries = (coordinates_strategies
                     .flatmap(coordinates_to_shaped_geometries))


def shaped_to_invalid_mix(shaped: Shaped) -> Strategy[Mix]:
    polygons = shaped_to_polygons(shaped)
    vertices = list(flatten(chain(polygon.border.vertices,
                                  flatten(hole.vertices
                                          for hole in polygon.holes))
                            for polygon in polygons))
    edges = list(flatten(polygon.edges for polygon in polygons))
    scales = strategies.integers(2, 100)
    rational_edges = strategies.sampled_from(edges).map(to_rational_segment)
    return (strategies.builds(Mix,
                              sub_lists(vertices,
                                        min_size=2)
                              .map(Multipoint),
                              empty_geometries,
                              strategies.just(shaped))
            | strategies.builds(
                    Mix,
                    empty_geometries,
                    strategies.builds(stretch_segment_end, rational_edges,
                                      scales),
                    strategies.just(shaped))
            | strategies.builds(
                    Mix,
                    empty_geometries,
                    strategies.builds(stretch_segment_start, rational_edges,
                                      scales),
                    strategies.just(shaped))
            | strategies.builds(Mix,
                                empty_geometries,
                                strategies.sampled_from(polygons)
                                .map(to_polygon_diagonals),
                                strategies.just(shaped))
            | strategies.builds(Mix,
                                empty_geometries,
                                sub_lists(edges,
                                          min_size=2)
                                .map(Multisegment),
                                strategies.just(shaped)))


def stretch_segment_end(segment: Segment, scale: Scalar) -> Segment:
    assert scale > 1
    return Segment(segment.start,
                   segment.end
                   .translate(scale * (segment.end.x - segment.start.x),
                              scale * (segment.end.y - segment.start.y)))


def stretch_segment_start(segment: Segment, scale: Scalar) -> Segment:
    assert scale > 1
    return Segment(segment.start
                   .translate(scale * (segment.start.x - segment.end.x),
                              scale * (segment.start.y - segment.end.y)),
                   segment.end)


invalid_mixes = (shaped_geometries.flatmap(shaped_to_invalid_mix)
                 | strategies.builds(Mix, empty_geometries | multipoints,
                                     empty_geometries, empty_geometries)
                 | strategies.builds(Mix, empty_geometries,
                                     empty_geometries | linear_geometries,
                                     empty_geometries)
                 | strategies.builds(Mix, empty_geometries, empty_geometries,
                                     empty_geometries | shaped_geometries)
                 | strategies.builds(Mix, invalid_multipoints,
                                     empty_geometries | linear_geometries,
                                     shaped_geometries)
                 | strategies.builds(Mix, invalid_multipoints,
                                     linear_geometries,
                                     empty_geometries | shaped_geometries)
                 | strategies.builds(Mix, empty_geometries | multipoints,
                                     invalid_linear_geometries,
                                     shaped_geometries)
                 | strategies.builds(Mix, multipoints,
                                     invalid_linear_geometries,
                                     empty_geometries | shaped_geometries)
                 | strategies.builds(Mix, multipoints,
                                     empty_geometries | linear_geometries,
                                     invalid_shaped_geometries)
                 | strategies.builds(Mix, empty_geometries | multipoints,
                                     linear_geometries,
                                     invalid_shaped_geometries))
mixes_with_points = (coordinates_strategies
                     .flatmap(cleave_in_tuples(coordinates_to_mixes,
                                               coordinates_to_points)))
mixes_strategies = coordinates_strategies.map(coordinates_to_mixes)
mixes_pairs = mixes_strategies.flatmap(to_pairs)
mixes_triplets = mixes_strategies.flatmap(to_triplets)
