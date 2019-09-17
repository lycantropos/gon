from gon.base import Point
from . import bounds
from .utils import (sum_expansions,
                    two_diff_tail,
                    two_product,
                    two_two_diff)


def determinant(vertex: Point,
                first_ray_point: Point,
                second_ray_point: Point) -> float:
    det_left = ((vertex.x - second_ray_point.x)
                * (first_ray_point.y - second_ray_point.y))
    det_right = ((vertex.y - second_ray_point.y)
                 * (first_ray_point.x - second_ray_point.x))
    det = det_left - det_right

    if det_left > 0.0:
        if det_right <= 0.0:
            return det
        else:
            det_sum = det_left + det_right
    elif det_left < 0.0:
        if det_right >= 0.0:
            return det
        else:
            det_sum = -det_left - det_right
    else:
        return det

    error_bound = bounds.to_counterclockwise_error_a(det_sum)
    if (det >= error_bound) or (-det >= error_bound):
        return det

    return determinant_adapt(vertex, first_ray_point,
                             second_ray_point, det_sum)


def determinant_adapt(first_coordinates: Point,
                      second_coordinates: Point,
                      third_coordinates: Point,
                      det_sum: float) -> float:
    b = [0] * 4

    acx = first_coordinates.x - third_coordinates.x
    bcx = second_coordinates.x - third_coordinates.x
    acy = first_coordinates.y - third_coordinates.y
    bcy = second_coordinates.y - third_coordinates.y

    det_left, det_left_tail = two_product(acx, bcy)
    det_right, det_right_tail = two_product(acy, bcx)

    b[3], b[2], b[1], b[0] = two_two_diff(det_left, det_left_tail,
                                          det_right, det_right_tail)

    det = sum(b)
    error_bound = bounds.to_counterclockwise_error_b(det_sum)
    if (det >= error_bound) or (-det >= error_bound):
        return det

    acx_tail = two_diff_tail(first_coordinates.x, third_coordinates.x, acx)
    bcx_tail = two_diff_tail(second_coordinates.x, third_coordinates.x, bcx)
    acy_tail = two_diff_tail(first_coordinates.y, third_coordinates.y, acy)
    bcy_tail = two_diff_tail(second_coordinates.y, third_coordinates.y, bcy)

    if ((acx_tail == 0.0) and (acy_tail == 0.0)
            and (bcx_tail == 0.0) and (bcy_tail == 0.0)):
        return det

    error_bound = (bounds.to_counterclockwise_error_c(det_sum)
                   + bounds.to_determinant_error(det))
    det += ((acx * bcy_tail + bcy * acx_tail)
            - (acy * bcx_tail + bcx * acy_tail))

    if (det >= error_bound) or (-det >= error_bound):
        return det

    s1, s0 = two_product(acx_tail, bcy)
    t1, t0 = two_product(acy_tail, bcx)
    u = [0] * 4
    u[3], u[2], u[1], u[0] = two_two_diff(s1, s0, t1, t0)

    c1 = sum_expansions(b, u)

    s1, s0 = two_product(acx, bcy_tail)
    t1, t0 = two_product(acy, bcx_tail)
    u[3], u[2], u[1], u[0] = two_two_diff(s1, s0, t1, t0)
    c2 = sum_expansions(c1, u)

    s1, s0 = two_product(acx_tail, bcy_tail)
    t1, t0 = two_product(acy_tail, bcx_tail)
    u[3], u[2], u[1], u[0] = two_two_diff(s1, s0, t1, t0)
    return sum_expansions(c2, u)[-1]
