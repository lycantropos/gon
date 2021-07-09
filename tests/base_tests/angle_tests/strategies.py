from hypothesis import strategies

from gon.base import Angle
from gon.hints import Scalar
from tests.strategies import (coordinates_strategies,
                              coordinates_to_angles)
from tests.strategies.primitive import (invalid_coordinates,
                                        valid_coordinates)
from tests.utils import (Strategy,
                         pack,
                         to_pairs,
                         to_sign,
                         to_triplets)


def to_non_fractional_coordinates(coordinates: Strategy[Scalar]
                                  ) -> Strategy[Scalar]:
    def to_non_fractional_coordinate(coordinate: Scalar) -> Scalar:
        return coordinate + (to_sign(coordinate) or 1)

    return coordinates.map(to_non_fractional_coordinate)


non_fractional_coordinates_strategies = (coordinates_strategies
                                         .map(to_non_fractional_coordinates))
invalid_angles = ((non_fractional_coordinates_strategies
                   .flatmap(to_pairs).map(pack(Angle)))
                  | strategies.builds(Angle,
                                      invalid_coordinates | valid_coordinates,
                                      invalid_coordinates)
                  | strategies.builds(Angle,
                                      invalid_coordinates, valid_coordinates))
angles = coordinates_strategies.flatmap(coordinates_to_angles)
angles_strategies = coordinates_strategies.map(coordinates_to_angles)
angles_pairs = angles_strategies.flatmap(to_pairs)
angles_triplets = angles_strategies.flatmap(to_triplets)
