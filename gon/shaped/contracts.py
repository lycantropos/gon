from gon.angular import Orientation
from .hints import Vertices
from .utils import (_to_non_neighbours,
                    to_angles,
                    to_edges)


def vertices_forms_convex_polygon(vertices: Vertices) -> bool:
    if len(vertices) == 3:
        return True
    orientations = (angle.orientation for angle in to_angles(vertices))
    base_orientation = next(orientations)
    # orientation change means
    # that internal angle is greater than 180 degrees
    return all(orientation == base_orientation for orientation in orientations)


def vertices_forms_strict_polygon(vertices: Vertices) -> bool:
    return all(angle.orientation is not Orientation.COLLINEAR
               for angle in to_angles(vertices))


def self_intersects(vertices: Vertices) -> bool:
    if len(vertices) == 3:
        return False
    edges = tuple(to_edges(vertices))
    for index, edge in enumerate(edges):
        # skipping neighbours because they always intersect
        # NOTE: first & last edges are neighbours
        if any(edge.intersects_with(non_neighbour)
               for non_neighbour in _to_non_neighbours(index, edges)):
            return True
    return False
