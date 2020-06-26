from .base import (coordinates_strategies,
                   rational_coordinates_strategies)
from .factories import (coordinates_to_contours,
                        coordinates_to_mixes,
                        coordinates_to_multipoints,
                        coordinates_to_multipolygons,
                        coordinates_to_multisegments,
                        coordinates_to_points,
                        coordinates_to_polygons,
                        coordinates_to_segments)
from .linear import (contours_with_repeated_points,
                     invalid_segments,
                     invalid_vertices_contours)
from .primitive import (invalid_points,
                        points,
                        points_strategies,
                        repeated_raw_points)
from .shaped import invalid_polygons
