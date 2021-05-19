from itertools import chain
from typing import Sequence

from ground.hints import Point

MIN_COUNT = 3


def rotate_positions(vertices: Sequence[Point]) -> Sequence[Point]:
    return vertices[:1] + vertices[:0:-1]


def equal(left: Sequence[Point],
          right: Sequence[Point],
          same_oriented: bool) -> bool:
    if len(left) != len(right):
        return False
    try:
        index = right.index(left[0])
    except ValueError:
        return False
    right_step = 1 if same_oriented else -1
    size = len(left)
    indices = chain(zip(range(size),
                        range(index, size)
                        if same_oriented
                        else range(index, -1, right_step)),
                    zip(range(size - index if same_oriented else index + 1,
                              size),
                        range(index)
                        if same_oriented
                        else range(size - 1, index - 1, right_step)))
    return all(left[left_index] == right[right_index]
               for left_index, right_index in indices)
