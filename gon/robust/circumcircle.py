from gon.base import Point
from . import bounds
from .utils import (scale_expansion,
                    square,
                    sum_expansions,
                    two_diff_tail,
                    two_product,
                    two_two_diff,
                    two_two_sum)


def determinant(first_vertex: Point,
                second_vertex: Point,
                third_vertex: Point,
                point: Point) -> float:
    adx, ady = first_vertex.x - point.x, first_vertex.y - point.y
    bdx, bdy = second_vertex.x - point.x, second_vertex.y - point.y
    cdx, cdy = third_vertex.x - point.x, third_vertex.y - point.y

    adx_bdy, adx_cdy = adx * bdy, adx * cdy
    bdx_ady, bdx_cdy = bdx * ady, bdx * cdy
    cdx_ady, cdx_bdy = cdx * ady, cdx * bdy

    a_lift = adx * adx + ady * ady
    b_lift = bdx * bdx + bdy * bdy
    c_lift = cdx * cdx + cdy * cdy

    det = (a_lift * (bdx_cdy - cdx_bdy)
           + b_lift * (cdx_ady - adx_cdy)
           + c_lift * (adx_bdy - bdx_ady))
    permanent = ((abs(bdx_cdy) + abs(cdx_bdy)) * a_lift
                 + (abs(cdx_ady) + abs(adx_cdy)) * b_lift
                 + (abs(adx_bdy) + abs(bdx_ady)) * c_lift)
    error_bound = bounds.to_circumcircle_error_a(permanent)
    if det > error_bound or -det > error_bound:
        return det
    return determinant_adapt(first_vertex, second_vertex, third_vertex, point,
                             permanent)


def determinant_adapt(first_vertex: Point,
                      second_vertex: Point,
                      third_vertex: Point,
                      point: Point,
                      permanent: float) -> float:
    adx, ady = first_vertex.x - point.x, first_vertex.y - point.y
    bdx, bdy = second_vertex.x - point.x, second_vertex.y - point.y
    cdx, cdy = third_vertex.x - point.x, third_vertex.y - point.y

    bdx_cdy, bdx_cdy_tail = two_product(bdx, cdy)
    cdx_bdy, cdx_bdy_tail = two_product(cdx, bdy)
    bc = two_two_diff(bdx_cdy, bdx_cdy_tail, cdx_bdy, cdx_bdy_tail)
    axbc, aybc = scale_expansion(bc, adx), scale_expansion(bc, ady)
    a_det = sum_expansions(scale_expansion(axbc, adx),
                           scale_expansion(aybc, ady))

    cdx_ady, cdx_ady_tail = two_product(cdx, ady)
    adx_cdy, adx_cdy_tail = two_product(adx, cdy)
    ca = two_two_diff(cdx_ady, cdx_ady_tail, adx_cdy, adx_cdy_tail)
    bxca, byca = scale_expansion(ca, bdx), scale_expansion(ca, bdy)
    b_det = sum_expansions(scale_expansion(bxca, bdx),
                           scale_expansion(byca, bdy))

    adx_bdy, adx_bdy_tail = two_product(adx, bdy)
    bdx_ady, bdx_ady_tail = two_product(bdx, ady)
    ab = two_two_diff(adx_bdy, adx_bdy_tail, bdx_ady, bdx_ady_tail)
    cxab, cyab = scale_expansion(ab, cdx), scale_expansion(ab, cdy)
    c_det = sum_expansions(scale_expansion(cxab, cdx),
                           scale_expansion(cyab, cdy))

    result_expansion = sum_expansions(sum_expansions(a_det, b_det), c_det)

    det = sum(result_expansion)
    error_bound = bounds.to_circumcircle_error_b(permanent)
    if det >= error_bound or -det >= error_bound:
        return det

    adx_tail = two_diff_tail(first_vertex.x, point.x, adx)
    ady_tail = two_diff_tail(first_vertex.y, point.y, ady)
    bdx_tail = two_diff_tail(second_vertex.x, point.x, bdx)
    bdy_tail = two_diff_tail(second_vertex.y, point.y, bdy)
    cdx_tail = two_diff_tail(third_vertex.x, point.x, cdx)
    cdy_tail = two_diff_tail(third_vertex.y, point.y, cdy)

    if (not adx_tail and not ady_tail
            and not bdx_tail and not bdy_tail
            and not cdx_tail and not cdy_tail):
        return det

    error_bound = (bounds.to_circumcircle_error_c(permanent)
                   + bounds.to_determinant_error(det))

    det += (((adx * adx + ady * ady) * ((bdx * cdy_tail + cdy * bdx_tail)
                                        - (bdy * cdx_tail + cdx * bdy_tail))
             + 2.0 * (adx * adx_tail + ady * ady_tail)
             * (bdx * cdy - bdy * cdx))
            + ((bdx * bdx + bdy * bdy) * ((cdx * ady_tail + ady * cdx_tail)
                                          - (cdy * adx_tail + adx * cdy_tail))
               + 2.0 * (bdx * bdx_tail + bdy * bdy_tail)
               * (cdx * ady - cdy * adx))
            + ((cdx * cdx + cdy * cdy) * ((adx * bdy_tail + bdy * adx_tail)
                                          - (ady * bdx_tail + bdx * ady_tail))
               + 2.0 * (cdx * cdx_tail + cdy * cdy_tail)
               * (adx * bdy - ady * bdx)))

    if det >= error_bound or -det >= error_bound:
        return det

    aa = (0.0,) * 4
    bb = (0.0,) * 4
    cc = (0.0,) * 4

    if bdx_tail or bdy_tail or cdx_tail or cdy_tail:
        adx_squared, adx_squared_tail = square(adx)
        ady_squared, ady_squared_tail = square(ady)
        aa = two_two_sum(adx_squared, adx_squared_tail,
                         ady_squared, ady_squared_tail)

    if adx_tail or ady_tail or cdx_tail or cdy_tail:
        bdx_squared, bdx_squared_tail = square(bdx)
        bdy_squared, bdy_squared_tail = square(bdy)
        bb = two_two_sum(bdx_squared, bdx_squared_tail,
                         bdy_squared, bdy_squared_tail)

    if adx_tail or ady_tail or bdx_tail or bdy_tail:
        cdx_squared, cdx_squared_tail = square(cdx)
        cdy_squared, cdy_squared_tail = square(cdy)
        cc = two_two_sum(cdx_squared, cdx_squared_tail,
                         cdy_squared, cdy_squared_tail)

    if adx_tail:
        axtbc = scale_expansion(bc, adx_tail)
        temp16a = scale_expansion(axtbc, 2.0 * adx)
        axtcc = scale_expansion(cc, adx_tail)
        temp16b = scale_expansion(axtcc, bdy)
        axtbb = scale_expansion(bb, adx_tail)
        temp16c = scale_expansion(axtbb, -cdy)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if ady_tail:
        aytbc = scale_expansion(bc, ady_tail)
        temp16a = scale_expansion(aytbc, 2.0 * ady)
        aytbb = scale_expansion(bb, ady_tail)
        temp16b = scale_expansion(aytbb, cdx)
        aytcc = scale_expansion(cc, ady_tail)
        temp16c = scale_expansion(aytcc, -bdx)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if bdx_tail:
        bxtca = scale_expansion(ca, bdx_tail)
        temp16a = scale_expansion(bxtca, 2.0 * bdx)
        bxtaa = scale_expansion(aa, bdx_tail)
        temp16b = scale_expansion(bxtaa, cdy)
        bxtcc = scale_expansion(cc, bdx_tail)
        temp16c = scale_expansion(bxtcc, -ady)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if bdy_tail:
        bytca = scale_expansion(ca, bdy_tail)
        temp16a = scale_expansion(bytca, 2.0 * bdy)
        bytcc = scale_expansion(cc, bdy_tail)
        temp16b = scale_expansion(bytcc, adx)
        bytaa = scale_expansion(aa, bdy_tail)
        temp16c = scale_expansion(bytaa, -cdx)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if cdx_tail:
        cxtab = scale_expansion(ab, cdx_tail)
        temp16a = scale_expansion(cxtab, 2.0 * cdx)
        cxtbb = scale_expansion(bb, cdx_tail)
        temp16b = scale_expansion(cxtbb, ady)
        cxtaa = scale_expansion(aa, cdx_tail)
        temp16c = scale_expansion(cxtaa, -bdy)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if cdy_tail:
        cytab = scale_expansion(ab, cdy_tail)
        temp16a = scale_expansion(cytab, 2.0 * cdy)
        cytaa = scale_expansion(aa, cdy_tail)
        temp16b = scale_expansion(cytaa, bdx)
        cytbb = scale_expansion(bb, cdy_tail)
        temp16c = scale_expansion(cytbb, -adx)
        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        result_expansion = sum_expansions(result_expansion, temp48)

    if adx_tail or ady_tail:
        if bdx_tail or bdy_tail or cdx_tail or cdy_tail:
            ti, ti_tail = two_product(bdx_tail, cdy)
            tj, tj_tail = two_product(bdx, cdy_tail)
            u = two_two_sum(ti, ti_tail, tj, tj_tail)

            negate = -bdy
            ti, ti_tail = two_product(cdx_tail, negate)
            negate = -bdy_tail
            tj, tj_tail = two_product(cdx, negate)
            v = two_two_sum(ti, ti_tail, tj, tj_tail)

            bct = sum_expansions(u, v)

            ti, ti_tail = two_product(bdx_tail, cdy_tail)
            tj, tj_tail = two_product(cdx_tail, bdy_tail)
            bctt = two_two_diff(ti, ti_tail, tj, tj_tail)
        else:
            bct = bctt = (0.0,)

        if adx_tail:
            temp16a = scale_expansion(axtbc, adx_tail)
            axtbct = scale_expansion(bct, adx_tail)
            temp32a = scale_expansion(axtbct, 2.0 * adx)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            if bdy_tail:
                temp8 = scale_expansion(cc, adx_tail)
                temp16a = scale_expansion(temp8, bdy_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            if cdy_tail:
                temp8 = scale_expansion(bb, -adx_tail)
                temp16a = scale_expansion(temp8, cdy_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            temp32a = scale_expansion(axtbct, adx_tail)
            axtbctt = scale_expansion(bctt, adx_tail)
            temp16a = scale_expansion(axtbctt, 2.0 * adx)
            temp16b = scale_expansion(axtbctt, adx_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

        if ady_tail:
            temp16a = scale_expansion(aytbc, ady_tail)
            aytbct = scale_expansion(bct, ady_tail)
            temp32a = scale_expansion(aytbct, 2.0 * ady)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            temp32a = scale_expansion(aytbct, ady_tail)
            aytbctt = scale_expansion(bctt, ady_tail)
            temp16a = scale_expansion(aytbctt, 2.0 * ady)
            temp16b = scale_expansion(aytbctt, ady_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

    if bdx_tail or bdy_tail:
        if adx_tail or ady_tail or cdx_tail or cdy_tail:
            ti, ti_tail = two_product(cdx_tail, ady)
            tj, tj_tail = two_product(cdx, ady_tail)
            u = two_two_sum(ti, ti_tail, tj, tj_tail)
            negate = -cdy
            ti, ti_tail = two_product(adx_tail, negate)
            negate = -cdy_tail
            tj, tj_tail = two_product(adx, negate)
            v = two_two_sum(ti, ti_tail, tj, tj_tail)
            cat = sum_expansions(u, v)

            ti, ti_tail = two_product(cdx_tail, ady_tail)
            tj, tj_tail = two_product(adx_tail, cdy_tail)
            catt = two_two_diff(ti, ti_tail, tj, tj_tail)
        else:
            cat = catt = (0.0,)

        if bdx_tail:
            temp16a = scale_expansion(bxtca, bdx_tail)
            bxtcat = scale_expansion(cat, bdx_tail)
            temp32a = scale_expansion(bxtcat, 2.0 * bdx)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            if cdy_tail:
                temp8 = scale_expansion(aa, bdx_tail)
                temp16a = scale_expansion(temp8, cdy_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            if ady_tail:
                temp8 = scale_expansion(cc, -bdx_tail)
                temp16a = scale_expansion(temp8, ady_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            temp32a = scale_expansion(bxtcat, bdx_tail)
            bxtcatt = scale_expansion(catt, bdx_tail)
            temp16a = scale_expansion(bxtcatt, 2.0 * bdx)
            temp16b = scale_expansion(bxtcatt, bdx_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

        if bdy_tail:
            temp16a = scale_expansion(bytca, bdy_tail)
            bytcat = scale_expansion(cat, bdy_tail)
            temp32a = scale_expansion(bytcat, 2.0 * bdy)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)
            temp32a = scale_expansion(bytcat, bdy_tail)
            bytcatt = scale_expansion(catt, bdy_tail)
            temp16a = scale_expansion(bytcatt, 2.0 * bdy)
            temp16b = scale_expansion(bytcatt, bdy_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

    if cdx_tail or cdy_tail:
        if adx_tail or ady_tail or bdx_tail or bdy_tail:
            ti, ti_tail = two_product(adx_tail, bdy)
            tj, tj_tail = two_product(adx, bdy_tail)
            u = two_two_sum(ti, ti_tail, tj, tj_tail)
            negate = -ady
            ti, ti_tail = two_product(bdx_tail, negate)
            negate = -ady_tail
            tj, tj_tail = two_product(bdx, negate)
            v = two_two_sum(ti, ti_tail, tj, tj_tail)

            abt = sum_expansions(u, v)

            ti, ti_tail = two_product(adx_tail, bdy_tail)
            tj, tj_tail = two_product(bdx_tail, ady_tail)
            abtt = two_two_diff(ti, ti_tail, tj, tj_tail)
        else:
            abt = abtt = (0.0,)

        if cdx_tail:
            temp16a = scale_expansion(cxtab, cdx_tail)
            cxtabt = scale_expansion(abt, cdx_tail)
            temp32a = scale_expansion(cxtabt, 2.0 * cdx)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)

            if ady_tail:
                temp8 = scale_expansion(bb, cdx_tail)
                temp16a = scale_expansion(temp8, ady_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            if bdy_tail:
                temp8 = scale_expansion(aa, -cdx_tail)
                temp16a = scale_expansion(temp8, bdy_tail)
                result_expansion = sum_expansions(result_expansion, temp16a)

            temp32a = scale_expansion(cxtabt, cdx_tail)
            cxtabtt = scale_expansion(abtt, cdx_tail)
            temp16a = scale_expansion(cxtabtt, 2.0 * cdx)
            temp16b = scale_expansion(cxtabtt, cdx_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)

        if cdy_tail:
            temp16a = scale_expansion(cytab, cdy_tail)
            cytabt = scale_expansion(abt, cdy_tail)
            temp32a = scale_expansion(cytabt, 2.0 * cdy)
            temp48 = sum_expansions(temp16a, temp32a)
            result_expansion = sum_expansions(result_expansion, temp48)
            temp32a = scale_expansion(cytabt, cdy_tail)
            cytabtt = scale_expansion(abtt, cdy_tail)
            temp16a = scale_expansion(cytabtt, 2.0 * cdy)
            temp16b = scale_expansion(cytabtt, cdy_tail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            result_expansion = sum_expansions(result_expansion, temp64)
    return result_expansion[-1]
