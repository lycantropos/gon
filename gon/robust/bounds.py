from typing import Tuple

from gon.hints import Scalar


def _to_epsilon_and_splitter() -> Tuple[float, float]:
    every_other = True
    epsilon, splitter = 1, 1
    check = 1
    while True:
        last_check = check
        epsilon /= 2
        if every_other:
            splitter *= 2
        every_other = not every_other
        check = 1 + epsilon
        if check == 1 or check == last_check:
            break
    splitter += 1
    return epsilon, splitter


epsilon, splitter = _to_epsilon_and_splitter()


def to_determinant_error(determinant: Scalar) -> Scalar:
    local_epsilon = type(determinant)(epsilon)
    return (3 + 8 * local_epsilon) * local_epsilon * abs(determinant)


def to_counterclockwise_error_a(det_sum: Scalar) -> Scalar:
    local_epsilon = type(det_sum)(epsilon)
    return local_epsilon * (3 + 16 * local_epsilon) * det_sum


def to_counterclockwise_error_b(det_sum: Scalar) -> Scalar:
    local_epsilon = type(det_sum)(epsilon)
    return local_epsilon * (2 + 12 * local_epsilon) * det_sum


def to_counterclockwise_error_c(det_sum: Scalar) -> Scalar:
    local_epsilon = type(det_sum)(epsilon)
    return local_epsilon * local_epsilon * (9 + 64 * local_epsilon) * det_sum


def to_circumcircle_error_a(permanent: Scalar) -> Scalar:
    local_epsilon = type(permanent)(epsilon)
    return (10 + 96 * local_epsilon) * local_epsilon * permanent


def to_circumcircle_error_b(permanent: Scalar) -> Scalar:
    local_epsilon = type(permanent)(epsilon)
    return local_epsilon * (4 + 48 * local_epsilon) * permanent


def to_circumcircle_error_c(permanent: Scalar) -> Scalar:
    local_epsilon = type(permanent)(epsilon)
    return (local_epsilon * local_epsilon * (44 + 576 * local_epsilon)
            * permanent)
