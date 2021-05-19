from typing import (Iterable,
                    List,
                    Tuple,
                    Type)

from ground.hints import (Contour,
                          Multipolygon,
                          Point,
                          Polygon,
                          Scalar,
                          Segment)


def point_to_step(point: Point,
                  cosine: Scalar,
                  sine: Scalar) -> Tuple[Scalar, Scalar]:
    rotated_x, rotated_y = rotated_around_origin_point_coordinates(
            point, cosine, sine)
    return point.x - rotated_x, point.y - rotated_y


def rotated_around_origin_point_coordinates(point: Point,
                                            cosine: Scalar,
                                            sine: Scalar
                                            ) -> Tuple[Scalar, Scalar]:
    return (cosine * point.x - sine * point.y,
            sine * point.x + cosine * point.y)


def rotate_contour_around_origin(contour: Contour,
                                 cosine: Scalar,
                                 sine: Scalar,
                                 contour_cls: Type[Contour],
                                 point_cls: Type[Point]) -> Contour:
    return contour_cls(rotate_points_around_origin(contour.vertices, cosine,
                                                   sine, point_cls))


def rotate_multipolygon_around_origin(multipolygon: Multipolygon,
                                      cosine: Scalar,
                                      sine: Scalar,
                                      contour_cls: Type[Contour],
                                      multipolygon_cls: Type[Multipolygon],
                                      point_cls: Type[Point],
                                      polygon_cls: Type[Polygon]
                                      ) -> Multipolygon:
    return multipolygon_cls(
            [rotate_polygon_around_origin(polygon, cosine, sine, contour_cls,
                                          point_cls, polygon_cls)
             for polygon in multipolygon.polygons])


def rotate_point_around_origin(point: Point,
                               cosine: Scalar,
                               sine: Scalar,
                               point_cls: Type[Point]) -> Point:
    return point_cls(cosine * point.x - sine * point.y,
                     sine * point.x + cosine * point.y)


def rotate_points_around_origin(points: Iterable[Point],
                                cosine: Scalar,
                                sine: Scalar,
                                point_cls: Type[Point]) -> List[Point]:
    return [rotate_point_around_origin(point, cosine, sine, point_cls)
            for point in points]


def rotate_polygon_around_origin(polygon: Polygon,
                                 cosine: Scalar,
                                 sine: Scalar,
                                 contour_cls: Type[Contour],
                                 point_cls: Type[Point],
                                 polygon_cls: Type[Polygon]) -> Polygon:
    return polygon_cls(
            rotate_contour_around_origin(polygon.border, cosine, sine,
                                         contour_cls, point_cls),
            [rotate_contour_around_origin(hole, cosine, sine, contour_cls,
                                          point_cls)
             for hole in polygon.holes])


def rotate_segment_around_origin(segment: Segment,
                                 cosine: Scalar,
                                 sine: Scalar,
                                 point_cls: Type[Point],
                                 segment_cls: Type[Segment]) -> Segment:
    return segment_cls(rotate_point_around_origin(segment.start, cosine, sine,
                                                  point_cls),
                       rotate_point_around_origin(segment.end, cosine, sine,
                                                  point_cls))


def rotate_translate_contour(contour: Contour,
                             cosine: Scalar,
                             sine: Scalar,
                             step_x: Scalar,
                             step_y: Scalar,
                             contour_cls: Type[Contour],
                             point_cls: Type[Point]) -> Contour:
    return contour_cls(rotate_translate_points(contour.vertices, cosine, sine,
                                               step_x, step_y, point_cls))


def rotate_translate_multipolygon(multipolygon: Multipolygon,
                                  cosine: Scalar,
                                  sine: Scalar,
                                  step_x: Scalar,
                                  step_y: Scalar,
                                  contour_cls: Type[Contour],
                                  multipolygon_cls: Type[Multipolygon],
                                  point_cls: Type[Point],
                                  polygon_cls: Type[Polygon]) -> Multipolygon:
    return multipolygon_cls(
            [rotate_translate_polygon(polygon, cosine, sine, step_x, step_y,
                                      contour_cls, point_cls, polygon_cls)
             for polygon in multipolygon.polygons])


def rotate_translate_point(point: Point,
                           cosine: Scalar,
                           sine: Scalar,
                           step_x: Scalar,
                           step_y: Scalar,
                           point_cls: Type[Point]) -> Point:
    return point_cls(cosine * point.x - sine * point.y + step_x,
                     sine * point.x + cosine * point.y + step_y)


def rotate_translate_points(points: Iterable[Point],
                            cosine: Scalar,
                            sine: Scalar,
                            step_x: Scalar,
                            step_y: Scalar,
                            point_cls: Type[Point]) -> List[Point]:
    return [rotate_translate_point(point, cosine, sine, step_x, step_y,
                                   point_cls)
            for point in points]


def rotate_translate_polygon(polygon: Polygon,
                             cosine: Scalar,
                             sine: Scalar,
                             step_x: Scalar,
                             step_y: Scalar,
                             contour_cls: Type[Contour],
                             point_cls: Type[Point],
                             polygon_cls: Type[Polygon]) -> Polygon:
    return polygon_cls(rotate_translate_contour(polygon.border, cosine, sine,
                                                step_x, step_y, contour_cls,
                                                point_cls),
                       [rotate_translate_contour(hole, cosine, sine, step_x,
                                                 step_y, contour_cls,
                                                 point_cls)
                        for hole in polygon.holes])


def rotate_translate_segment(segment: Segment,
                             cosine: Scalar,
                             sine: Scalar,
                             step_x: Scalar,
                             step_y: Scalar,
                             point_cls: Type[Point],
                             segment_cls: Type[Segment]) -> Segment:
    return segment_cls(rotate_translate_point(segment.start, cosine, sine,
                                              step_x, step_y, point_cls),
                       rotate_translate_point(segment.end, cosine, sine,
                                              step_x, step_y, point_cls))
