from hypothesis import strategies

from gon.base import Multipoint
from .primitive import (invalid_points,
                        repeated_raw_points)

empty_multipoints = strategies.builds(Multipoint)
invalid_points_multipoints = (strategies.lists(invalid_points,
                                               min_size=1)
                              .map(Multipoint))
multipoints_with_repeated_points = repeated_raw_points.map(Multipoint.from_raw)
invalid_multipoints = (empty_multipoints
                       | invalid_points_multipoints
                       | multipoints_with_repeated_points)
