from collections import Counter

from hypothesis import given

from gon.linear import Loop
from . import strategies


@given(strategies.loops)
def test_basic(loop: Loop) -> None:
    isinstance(loop.reverse(), Loop)


@given(strategies.loops)
def test_sizes(loop: Loop) -> None:
    result = loop.reverse()

    assert len(result.vertices) == len(loop.vertices)


@given(strategies.loops)
def test_elements(loop: Loop) -> None:
    result = loop.reverse()

    assert Counter(result.vertices) == Counter(loop.vertices)
    assert result.vertices[0] == result.vertices[0]


@given(strategies.loops)
def test_orientation(loop: Loop) -> None:
    result = loop.reverse()

    assert result.orientation is not loop.orientation


@given(strategies.loops)
def test_involution(loop: Loop) -> None:
    result = loop.reverse()

    assert result.reverse() == loop
