from hypothesis import strategies

from gon.base import Vector
from tests.strategies import (angles,
                              coordinates_strategies,
                              coordinates_to_points,
                              coordinates_to_vectors,
                              invalid_points,
                              points)
from tests.utils import (cleave_in_tuples,
                         identity,
                         pack,
                         to_pairs,
                         to_triplets)

invalid_vectors = (strategies.builds(Vector, invalid_points | points,
                                     invalid_points)
                   | strategies.builds(Vector, invalid_points, points))
vectors = coordinates_strategies.flatmap(coordinates_to_vectors)
vectors_strategies = coordinates_strategies.map(coordinates_to_vectors)
vectors_pairs = vectors_strategies.flatmap(to_pairs)
zero_vectors_with_vectors = (
    (coordinates_strategies.flatmap(cleave_in_tuples(coordinates_to_points,
                                                     coordinates_to_vectors))
     .map(pack(lambda point, vector: (Vector(point, point), vector))))
)
vectors_pairs_with_scalars = coordinates_strategies.flatmap(
        cleave_in_tuples(coordinates_to_vectors, coordinates_to_vectors,
                         identity)
)
vectors_triplets = vectors_strategies.flatmap(to_triplets)
vectors_with_points = (coordinates_strategies
                       .flatmap(cleave_in_tuples(coordinates_to_vectors,
                                                 coordinates_to_points)))
vectors_points_with_angles = strategies.tuples(vectors_with_points, angles)
vectors_points_with_angles_pairs = strategies.tuples(vectors_with_points,
                                                     angles, angles)
