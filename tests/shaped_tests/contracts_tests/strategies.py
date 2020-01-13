from tests.strategies import (scalars_strategies,
                              scalars_to_triangles_vertices)

triangles_vertices = scalars_strategies.flatmap(scalars_to_triangles_vertices)
