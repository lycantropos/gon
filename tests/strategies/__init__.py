from .base import coordinates_strategies
from .factories import (coordinates_to_loops,
                        coordinates_to_points,
                        coordinates_to_polygons,
                        coordinates_to_segments)
from .linear import (invalid_vertices_loops,
                     loops_with_repeated_points,
                     small_loops)
from .primitive import (invalid_points,
                        points,
                        points_strategies)
