from hypothesis import given

from gon.hints import Permutation
from gon.utils import inverse_permutation
from . import strategies


@given(strategies.identity_permutations)
def test_identity(permutation: Permutation) -> None:
    assert inverse_permutation(permutation) == permutation


@given(strategies.permutations)
def test_involution(permutation: Permutation) -> None:
    assert inverse_permutation(inverse_permutation(permutation)) == permutation
