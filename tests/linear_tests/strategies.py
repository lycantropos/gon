from tests.strategies import (coordinates_strategies,
                              coordinates_to_linear_geometries)

linear_geometries = coordinates_strategies.flatmap(
        coordinates_to_linear_geometries)
