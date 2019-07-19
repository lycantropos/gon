from hypothesis import strategies

from gon.angular import Angle
from tests.strategies import points

angles = strategies.builds(Angle, points, points, points)
