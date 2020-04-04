from hypothesis_geometry import planar

from gon.linear import Contour
from tests.strategies import (coordinates_strategies,
                              coordinates_to_contours,
                              invalid_contours)
from tests.utils import (to_pairs,
                         to_triplets)

raw_contours = coordinates_strategies.flatmap(planar.contours)
contours = raw_contours.map(Contour.from_raw)
invalid_contours = invalid_contours
contours_strategies = coordinates_strategies.map(coordinates_to_contours)
contours_pairs = contours_strategies.flatmap(to_pairs)
contours_triplets = contours_strategies.flatmap(to_triplets)
