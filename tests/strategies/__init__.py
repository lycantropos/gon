from .base import (angles,
                   coordinates_strategies)
from .discrete import invalid_multipoints
from .factories import (coordinates_to_angles,
                        coordinates_to_contours,
                        coordinates_to_linear_geometries,
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
                        coordinates_to_shaped_geometries,
                        coordinates_to_vectors,
                        to_non_zero_coordinates,
                        to_zero_coordinates)
from .linear import (contours_with_repeated_points,
                     invalid_contours,
                     invalid_linear_geometries,
                     invalid_multisegments,
                     invalid_segments,
                     invalid_vertices_contours)
from .primitive import (invalid_points,
                        points,
                        repeated_points)
from .shaped import (invalid_multipolygons,
                     invalid_polygons,
                     invalid_shaped_geometries)
