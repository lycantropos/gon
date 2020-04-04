from hypothesis_geometry import planar

from gon.hints import Coordinate
from tests.utils import Strategy, to_pairs, to_triplets

from gon.linear import Contour
from tests.strategies import coordinates_strategies

raw_contours = coordinates_strategies.flatmap(planar.contours)
contours = raw_contours.map(Contour.from_raw)


def coordinates_to_contours(coordinates: Strategy[Coordinate]
                            ) -> Strategy[Contour]:
    return planar.contours(coordinates).map(Contour.from_raw)


contours_strategies = coordinates_strategies.map(coordinates_to_contours)
contours_pairs = contours_strategies.flatmap(to_pairs)
contours_triplets = contours_strategies.flatmap(to_triplets)
