from tests.strategies import (coordinates_strategies,
                              coordinates_to_shaped_geometries)

shaped_geometries = (coordinates_strategies.flatmap(
        coordinates_to_shaped_geometries))
