from typing import (Iterable,
                    Type,
                    Union)

from ground.hints import (Contour,
                          Empty,
                          Mix,
                          Multipoint,
                          Multisegment,
                          Point,
                          Polygon,
                          Scalar,
                          Segment)

from .contracts import (is_segment_horizontal,
                        is_segment_vertical)
from .iterable import unique_ever_seen
from .packing import (pack_mix,
                      pack_points,
                      pack_segments)


def scale_contour(contour: Contour,
                  factor_x: Scalar,
                  factor_y: Scalar,
                  contour_cls: Type[Contour],
                  point_cls: Type[Point]) -> Contour:
    return contour_cls([scale_point(vertex, factor_x, factor_y, point_cls)
                        for vertex in contour.vertices])


def scale_contour_degenerate(contour: Contour,
                             factor_x: Scalar,
                             factor_y: Scalar,
                             multipoint_cls: Type[Multipoint],
                             point_cls: Type[Point],
                             segment_cls: Type[Segment]
                             ) -> Union[Segment, Multipoint]:
    return scale_vertices_degenerate(contour.vertices, factor_x, factor_y,
                                     multipoint_cls, point_cls, segment_cls)


def scale_point(point: Point,
                factor_x: Scalar,
                factor_y: Scalar,
                point_cls: Type[Point]) -> Point:
    return point_cls(point.x * factor_x, point.y * factor_y)


def scale_polygon(polygon: Polygon,
                  factor_x: Scalar,
                  factor_y: Scalar,
                  contour_cls: Type[Contour],
                  point_cls: Type[Point],
                  polygon_cls: Type[Polygon]) -> Polygon:
    return polygon_cls(scale_contour(polygon.border, factor_x, factor_y,
                                     contour_cls, point_cls),
                       [scale_contour(hole, factor_x, factor_y, contour_cls,
                                      point_cls)
                        for hole in polygon.holes])


def scale_segment(segment: Segment,
                  factor_x: Scalar,
                  factor_y: Scalar,
                  multipoint_cls: Type[Multipoint],
                  point_cls: Type[Point],
                  segment_cls: Type[Segment]) -> Union[Multipoint, Segment]:
    return (scale_segment_non_degenerate(segment, factor_x, factor_y,
                                         point_cls, segment_cls)
            if ((factor_x or not is_segment_horizontal(segment)) and factor_y
                or factor_x and not is_segment_vertical(segment))
            else multipoint_cls([scale_point(segment.start, factor_x, factor_y,
                                             point_cls)]))


def scale_segment_non_degenerate(segment: Segment,
                                 factor_x: Scalar,
                                 factor_y: Scalar,
                                 point_cls: Type[Point],
                                 segment_cls: Type[Segment]) -> Segment:
    return segment_cls(scale_point(segment.start, factor_x, factor_y,
                                   point_cls),
                       scale_point(segment.end, factor_x, factor_y,
                                   point_cls))


def scale_vertices_degenerate(vertices: Iterable[Point],
                              factor_x: Scalar,
                              factor_y: Scalar,
                              multipoint_cls: Type[Multipoint],
                              point_cls: Type[Point],
                              segment_cls: Type[Segment]
                              ) -> Union[Segment, Multipoint]:
    return (scale_vertices_projecting_on_ox(vertices, factor_x, factor_y,
                                            point_cls, segment_cls)
            if factor_x
            else (scale_vertices_projecting_on_oy(vertices, factor_x, factor_y,
                                                  point_cls, segment_cls)
                  if factor_y
                  else multipoint_cls([point_cls(factor_x, factor_y)])))


def scale_vertices_projecting_on_ox(vertices: Iterable[Point],
                                    factor_x: Scalar,
                                    factor_y: Scalar,
                                    point_cls: Type[Point],
                                    segment_cls: Type[Segment]) -> Segment:
    vertices = iter(vertices)
    min_x = max_x = next(vertices).x
    for vertex in vertices:
        if min_x > vertex.x:
            min_x = vertex.x
        elif max_x < vertex.x:
            max_x = vertex.x
    return segment_cls(point_cls(min_x * factor_x, factor_y),
                       point_cls(max_x * factor_x, factor_y))


def scale_vertices_projecting_on_oy(vertices: Iterable[Point],
                                    factor_x: Scalar,
                                    factor_y: Scalar,
                                    point_cls: Type[Point],
                                    segment_cls: Type[Segment]) -> Segment:
    vertices = iter(vertices)
    min_y = max_y = next(vertices).y
    for vertex in vertices:
        if min_y > vertex.y:
            min_y = vertex.y
        elif max_y < vertex.y:
            max_y = vertex.y
    return segment_cls(point_cls(factor_x, min_y * factor_y),
                       point_cls(factor_x, max_y * factor_y))


def scale_segments(segments: Iterable[Segment],
                   factor_x: Scalar,
                   factor_y: Scalar,
                   empty: Empty,
                   mix_cls: Type[Mix],
                   multipoint_cls: Type[Multipoint],
                   multisegment_cls: Type[Multisegment],
                   point_cls: Type[Point],
                   segment_cls: Type[Segment]
                   ) -> Union[Mix, Multipoint, Multisegment, Segment]:
    scaled_points, scaled_segments = [], []
    for segment in segments:
        if ((factor_x or not is_segment_horizontal(segment)) and factor_y
                or factor_x and not is_segment_vertical(segment)):
            scaled_segments.append(scale_segment_non_degenerate(
                    segment, factor_x, factor_y, point_cls, segment_cls))
        else:
            scaled_points.append(scale_point(segment.start, factor_x, factor_y,
                                             point_cls))
    return pack_mix(pack_points(unique_ever_seen(scaled_points), empty,
                                multipoint_cls),
                    pack_segments(scaled_segments, empty, multisegment_cls),
                    empty, empty, mix_cls)
