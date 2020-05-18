from hypothesis import given

from gon.compound import Indexable
from . import strategies


@given(strategies.indexables)
def test_basic(indexable: Indexable) -> None:
    assert indexable.index() is None
