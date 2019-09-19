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
    if det >= error_bound or -det >= error_bound:
        return det

    return determinant_adapt(vertex, first_ray_point,
                             second_ray_point, det_sum)


def determinant_adapt(vertex: Point,
                      first_ray_point: Point,
                      second_ray_point: Point,
                      det_sum: float) -> float:
    acx = vertex.x - second_ray_point.x
    bcx = first_ray_point.x - second_ray_point.x
    acy = vertex.y - second_ray_point.y
    bcy = first_ray_point.y - second_ray_point.y

    det_left, det_left_tail = two_product(acx, bcy)
    det_right, det_right_tail = two_product(acy, bcx)

    b = two_two_diff(det_left, det_left_tail, det_right, det_right_tail)
    det = sum(b)
    error_bound = bounds.to_counterclockwise_error_b(det_sum)
    if (det >= error_bound) or (-det >= error_bound):
        return det

    acx_tail = two_diff_tail(vertex.x, second_ray_point.x, acx)
    bcx_tail = two_diff_tail(first_ray_point.x, second_ray_point.x, bcx)
    acy_tail = two_diff_tail(vertex.y, second_ray_point.y, acy)
    bcy_tail = two_diff_tail(first_ray_point.y, second_ray_point.y, bcy)
    if not acx_tail and not acy_tail and not bcx_tail and not bcy_tail:
        return det

    error_bound = (bounds.to_counterclockwise_error_c(det_sum)
                   + bounds.to_determinant_error(det))
    det += ((acx * bcy_tail + bcy * acx_tail)
            - (acy * bcx_tail + bcx * acy_tail))

    if (det >= error_bound) or (-det >= error_bound):
        return det

    s, s_tail = two_product(acx_tail, bcy)
    t, t_tail = two_product(acy_tail, bcx)
    u = two_two_diff(s, s_tail, t, t_tail)
    c1 = sum_expansions(b, u)

    s, s_tail = two_product(acx, bcy_tail)
    t, t_tail = two_product(acy, bcx_tail)
    u = two_two_diff(s, s_tail, t, t_tail)
    c2 = sum_expansions(c1, u)

    s, s_tail = two_product(acx_tail, bcy_tail)
    t, t_tail = two_product(acy_tail, bcx_tail)
    u = two_two_diff(s, s_tail, t, t_tail)
    return sum_expansions(c2, u)[-1]
