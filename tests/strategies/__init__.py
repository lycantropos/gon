from .base import coordinates_strategies
from .factories import (coordinates_to_contours,
                        coordinates_to_points,
                        coordinates_to_polygons,
                        coordinates_to_segments)
from .linear import (contours_with_repeated_points,
                     invalid_vertices_contours,
                     small_contours)
from .primitive import (invalid_points,
                        points,
                        points_strategies)
