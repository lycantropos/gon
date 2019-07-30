from hypothesis import strategies
from lz.functional import pack

from gon.angular import Angle
from tests.strategies import points

angles = (strategies.lists(points,
                           min_size=3,
                           max_size=3,
                           unique=True)
          .map(pack(Angle)))
