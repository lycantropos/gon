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
    aa = [0.0] * 4
    ab = [0.0] * 4
    bb = [0.0] * 4
    bc = [0.0] * 4
    ca = [0.0] * 4
    cc = [0.0] * 4
    u = [0.0] * 4
    v = [0.0] * 4
    abtt = [0.0] * 4
    bctt = [0.0] * 4
    catt = [0.0] * 4

    adx = first_vertex.x - point.x
    bdx = second_vertex.x - point.x
    cdx = third_vertex.x - point.x
    ady = first_vertex.y - point.y
    bdy = second_vertex.y - point.y
    cdy = third_vertex.y - point.y

    bdxcdy1, bdxcdy0 = two_product(bdx, cdy)
    cdxbdy1, cdxbdy0 = two_product(cdx, bdy)
    bc[3], bc[2], bc[1], bc[0] = two_two_diff(bdxcdy1, bdxcdy0,
                                              cdxbdy1, cdxbdy0)

    axbc = scale_expansion(bc, adx)
    axxbc = scale_expansion(axbc, adx)
    aybc = scale_expansion(bc, ady)
    ayybc = scale_expansion(aybc, ady)
    adet = sum_expansions(axxbc, ayybc)

    cdxady1, cdxady0 = two_product(cdx, ady)
    adxcdy1, adxcdy0 = two_product(adx, cdy)

    ca[3], ca[2], ca[1], ca[0] = two_two_diff(cdxady1, cdxady0,
                                              adxcdy1, adxcdy0)

    bxca = scale_expansion(ca, bdx)
    bxxca = scale_expansion(bxca, bdx)
    byca = scale_expansion(ca, bdy)
    byyca = scale_expansion(byca, bdy)
    bdet = sum_expansions(bxxca, byyca)

    adxbdy1, adxbdy0 = two_product(adx, bdy)
    bdxady1, bdxady0 = two_product(bdx, ady)
    ab[3], ab[2], ab[1], ab[0] = two_two_diff(adxbdy1, adxbdy0,
                                              bdxady1, bdxady0)

    cxab = scale_expansion(ab, cdx)
    cxxab = scale_expansion(cxab, cdx)
    cyab = scale_expansion(ab, cdy)
    cyyab = scale_expansion(cyab, cdy)
    cdet = sum_expansions(cxxab, cyyab)

    abdet = sum_expansions(adet, bdet)
    fin1 = sum_expansions(abdet, cdet)

    det = sum(fin1)
    error_bound = bounds.to_circumcircle_error_b(permanent)
    if (det >= error_bound) or (-det >= error_bound):
        return det

    adxtail = two_diff_tail(first_vertex.x, point.x,
                            adx)
    adytail = two_diff_tail(first_vertex.y, point.y,
                            ady)
    bdxtail = two_diff_tail(second_vertex.x, point.x,
                            bdx)
    bdytail = two_diff_tail(second_vertex.y, point.y,
                            bdy)
    cdxtail = two_diff_tail(third_vertex.x, point.x,
                            cdx)
    cdytail = two_diff_tail(third_vertex.y, point.y,
                            cdy)

    if ((adxtail == 0.0) and (bdxtail == 0.0) and (cdxtail == 0.0)
            and (adytail == 0.0) and (bdytail == 0.0) and (cdytail == 0.0)):
        return det

    error_bound = (bounds.to_circumcircle_error_c(permanent)
                   + bounds.to_determinant_error(det))

    det += (((adx * adx + ady * ady) * ((bdx * cdytail + cdy * bdxtail)
                                        - (bdy * cdxtail + cdx * bdytail))
             + 2.0 * (adx * adxtail + ady * adytail) * (bdx * cdy - bdy * cdx))
            + ((bdx * bdx + bdy * bdy) * ((cdx * adytail + ady * cdxtail)
                                          - (cdy * adxtail + adx * cdytail))
               + 2.0 * (bdx * bdxtail + bdy * bdytail) * (
                       cdx * ady - cdy * adx))
            + ((cdx * cdx + cdy * cdy) * ((adx * bdytail + bdy * adxtail)
                                          - (ady * bdxtail + bdx * adytail))
               + 2.0 * (cdx * cdxtail + cdy * cdytail) * (
                       adx * bdy - ady * bdx)))

    if (det >= error_bound) or (-det >= error_bound):
        return det

    finnow = fin1

    if ((bdxtail != 0.0) or (bdytail != 0.0)
            or (cdxtail != 0.0) or (cdytail != 0.0)):
        adxadx1, adxadx0 = square(adx)
        adyady1, adyady0 = square(ady)
        aa[3], aa[2], aa[1], aa[0] = two_two_sum(adxadx1, adxadx0,
                                                 adyady1, adyady0)

    if ((cdxtail != 0.0) or (cdytail != 0.0)
            or (adxtail != 0.0) or (adytail != 0.0)):
        bdxbdx1, bdxbdx0 = square(bdx)
        bdybdy1, bdybdy0 = square(bdy)
        bb[3], bb[2], bb[1], bb[0] = two_two_sum(bdxbdx1, bdxbdx0,
                                                 bdybdy1, bdybdy0)

    if ((adxtail != 0.0) or (adytail != 0.0)
            or (bdxtail != 0.0) or (bdytail != 0.0)):
        cdxcdx1, cdxcdx0 = square(cdx)
        cdycdy1, cdycdy0 = square(cdy)
        cc[3], cc[2], cc[1], cc[0] = two_two_sum(cdxcdx1, cdxcdx0,
                                                 cdycdy1, cdycdy0)

    if adxtail != 0.0:
        axtbc = scale_expansion(bc, adxtail)
        temp16a = scale_expansion(axtbc, 2.0 * adx)

        axtcc = scale_expansion(cc, adxtail)
        temp16b = scale_expansion(axtcc, bdy)

        axtbb = scale_expansion(bb, adxtail)
        temp16c = scale_expansion(axtbb, -cdy)

        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        finother = sum_expansions(finnow, temp48)
        finnow, finother = finother, finnow

    if adytail != 0.0:
        aytbc = scale_expansion(bc, adytail)
        temp16a = scale_expansion(aytbc, 2.0 * ady)

        aytbb = scale_expansion(bb, adytail)

        temp16b = scale_expansion(aytbb, cdx)

        aytcc = scale_expansion(cc, adytail)

        temp16c = scale_expansion(aytcc, -bdx)

        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)

        finother = sum_expansions(finnow,
                                  temp48)
        finnow, finother = finother, finnow

    if bdxtail != 0.0:
        bxtca = scale_expansion(ca, bdxtail)

        temp16a = scale_expansion(bxtca, 2.0 * bdx)

        bxtaa = scale_expansion(aa, bdxtail)
        temp16b = scale_expansion(bxtaa, cdy)

        bxtcc = scale_expansion(cc, bdxtail)
        temp16c = scale_expansion(bxtcc, -ady)

        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        finother = sum_expansions(finnow,
                                  temp48)
        finnow, finother = finother, finnow

    if bdytail != 0.0:
        bytca = scale_expansion(ca, bdytail)

        temp16a = scale_expansion(bytca, 2.0 * bdy)

        bytcc = scale_expansion(cc, bdytail)
        temp16b = scale_expansion(bytcc, adx)

        bytaa = scale_expansion(aa, bdytail)
        temp16c = scale_expansion(bytaa, -cdx)

        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        finother = sum_expansions(finnow,
                                  temp48)
        finnow, finother = finother, finnow

    if cdxtail != 0.0:
        cxtab = scale_expansion(ab, cdxtail)

        temp16a = scale_expansion(cxtab, 2.0 * cdx)

        cxtbb = scale_expansion(bb, cdxtail)
        temp16b = scale_expansion(cxtbb, ady)

        cxtaa = scale_expansion(aa, cdxtail)
        temp16c = scale_expansion(cxtaa, -bdy)

        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        finother = sum_expansions(finnow,
                                  temp48)
        finnow, finother = finother, finnow

    if cdytail != 0.0:
        cytab = scale_expansion(ab, cdytail)

        temp16a = scale_expansion(cytab, 2.0 * cdy)

        cytaa = scale_expansion(aa, cdytail)
        temp16b = scale_expansion(cytaa, bdx)

        cytbb = scale_expansion(bb, cdytail)
        temp16c = scale_expansion(cytbb, -adx)

        temp32a = sum_expansions(temp16a, temp16b)
        temp48 = sum_expansions(temp16c, temp32a)
        finother = sum_expansions(finnow,
                                  temp48)
        finnow, finother = finother, finnow

    if (adxtail != 0.0) or (adytail != 0.0):
        if ((bdxtail != 0.0) or (bdytail != 0.0)
                or (cdxtail != 0.0) or (cdytail != 0.0)):
            ti1, ti0 = two_product(bdxtail, cdy)
            tj1, tj0 = two_product(bdx, cdytail)
            u[3], u[2], u[1], u[0] = two_two_sum(ti1, ti0, tj1, tj0)

            negate = -bdy
            ti1, ti0 = two_product(cdxtail, negate)
            negate = -bdytail
            tj1, tj0 = two_product(cdx, negate)
            v[3], v[2], v[1], v[0] = two_two_sum(ti1, ti0, tj1, tj0)

            bct = sum_expansions(u, v)

            ti1, ti0 = two_product(bdxtail, cdytail)
            tj1, tj0 = two_product(cdxtail, bdytail)
            bctt[3], bctt[2], bctt[1], bctt[0] = two_two_diff(ti1, ti0, tj1,
                                                              tj0)
        else:
            bct = [0.0]
            bctt = [0.0]

        if adxtail != 0.0:
            temp16a = scale_expansion(axtbc, adxtail)
            axtbct = scale_expansion(bct, adxtail)

            temp32a = scale_expansion(axtbct, 2.0 * adx)
            temp48 = sum_expansions(temp16a, temp32a)
            finother = sum_expansions(finnow, temp48)
            finnow, finother = finother, finnow

            if bdytail != 0.0:
                temp8 = scale_expansion(cc, adxtail)

                temp16a = scale_expansion(temp8, bdytail)
                finother = sum_expansions(finnow, temp16a)
                finnow, finother = finother, finnow

            if cdytail != 0.0:
                temp8 = scale_expansion(bb, -adxtail)
                temp16a = scale_expansion(temp8, cdytail)
                finother = sum_expansions(finnow, temp16a)
                finnow, finother = finother, finnow

            temp32a = scale_expansion(axtbct, adxtail)
            axtbctt = scale_expansion(bctt, adxtail)

            temp16a = scale_expansion(axtbctt, 2.0 * adx)

            temp16b = scale_expansion(axtbctt, adxtail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            finother = sum_expansions(finnow, temp64)
            finnow, finother = finother, finnow

        if adytail != 0.0:
            temp16a = scale_expansion(aytbc, adytail)
            aytbct = scale_expansion(bct, adytail)

            temp32a = scale_expansion(aytbct, 2.0 * ady)
            temp48 = sum_expansions(temp16a, temp32a)
            finother = sum_expansions(finnow, temp48)
            finnow, finother = finother, finnow

            temp32a = scale_expansion(aytbct, adytail)
            aytbctt = scale_expansion(bctt, adytail)

            temp16a = scale_expansion(aytbctt, 2.0 * ady)

            temp16b = scale_expansion(aytbctt, adytail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            finother = sum_expansions(finnow, temp64)
            finnow, finother = finother, finnow

    if (bdxtail != 0.0) or (bdytail != 0.0):
        if ((cdxtail != 0.0) or (cdytail != 0.0)
                or (adxtail != 0.0) or (adytail != 0.0)):
            ti1, ti0 = two_product(cdxtail, ady)
            tj1, tj0 = two_product(cdx, adytail)
            u[3], u[2], u[1], u[0] = two_two_sum(ti1, ti0, tj1, tj0)
            negate = -cdy
            ti1, ti0 = two_product(adxtail, negate)
            negate = -cdytail
            tj1, tj0 = two_product(adx, negate)
            v[3], v[2], v[1], v[0] = two_two_sum(ti1, ti0, tj1, tj0)
            cat = sum_expansions(u, v)

            ti1, ti0 = two_product(cdxtail, adytail)
            tj1, tj0 = two_product(adxtail, cdytail)
            catt[3], catt[2], catt[1], catt[0] = two_two_diff(ti1, ti0, tj1,
                                                              tj0)
        else:
            cat = [0.0]
            catt = [0.0]

        if bdxtail != 0.0:
            temp16a = scale_expansion(bxtca, bdxtail)
            bxtcat = scale_expansion(cat, bdxtail)

            temp32a = scale_expansion(bxtcat, 2.0 * bdx)
            temp48 = sum_expansions(temp16a, temp32a)
            finother = sum_expansions(finnow, temp48)
            finnow, finother = finother, finnow
            if cdytail != 0.0:
                temp8 = scale_expansion(aa, bdxtail)
                temp16a = scale_expansion(temp8, cdytail)
                finother = sum_expansions(finnow, temp16a)
                finnow, finother = finother, finnow

            if adytail != 0.0:
                temp8 = scale_expansion(cc, -bdxtail)
                temp16a = scale_expansion(temp8, adytail)
                finother = sum_expansions(finnow, temp16a)
                finnow, finother = finother, finnow

            temp32a = scale_expansion(bxtcat, bdxtail)
            bxtcatt = scale_expansion(catt, bdxtail)

            temp16a = scale_expansion(bxtcatt, 2.0 * bdx)

            temp16b = scale_expansion(bxtcatt, bdxtail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            finother = sum_expansions(finnow, temp64)
            finnow, finother = finother, finnow

        if bdytail != 0.0:
            temp16a = scale_expansion(bytca, bdytail)
            bytcat = scale_expansion(cat, bdytail)

            temp32a = scale_expansion(bytcat, 2.0 * bdy)
            temp48 = sum_expansions(temp16a, temp32a)
            finother = sum_expansions(finnow, temp48)
            finnow, finother = finother, finnow

            temp32a = scale_expansion(bytcat, bdytail)
            bytcatt = scale_expansion(catt, bdytail)

            temp16a = scale_expansion(bytcatt, 2.0 * bdy)

            temp16b = scale_expansion(bytcatt, bdytail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            finother = sum_expansions(finnow, temp64)
            finnow, finother = finother, finnow

    if (cdxtail != 0.0) or (cdytail != 0.0):
        if ((adxtail != 0.0) or (adytail != 0.0)
                or (bdxtail != 0.0) or (bdytail != 0.0)):
            ti1, ti0 = two_product(adxtail, bdy)
            tj1, tj0 = two_product(adx, bdytail)
            u[3], u[2], u[1], u[0] = two_two_sum(ti1, ti0, tj1, tj0)
            negate = -ady
            ti1, ti0 = two_product(bdxtail, negate)
            negate = -adytail
            tj1, tj0 = two_product(bdx, negate)
            v[3], v[2], v[1], v[0] = two_two_sum(ti1, ti0, tj1, tj0)

            abt = sum_expansions(u, v)

            ti1, ti0 = two_product(adxtail, bdytail)
            tj1, tj0 = two_product(bdxtail, adytail)
            abtt[3], abtt[2], abtt[1], abtt[0] = two_two_diff(ti1, ti0,
                                                              tj1, tj0)
        else:
            abt = [0.0]
            abtt = [0.0]

        if cdxtail != 0.0:
            temp16a = scale_expansion(cxtab, cdxtail)
            cxtabt = scale_expansion(abt, cdxtail)

            temp32a = scale_expansion(cxtabt, 2.0 * cdx)
            temp48 = sum_expansions(temp16a, temp32a)
            finother = sum_expansions(finnow, temp48)
            finnow, finother = finother, finnow
            if adytail != 0.0:
                temp8 = scale_expansion(bb, cdxtail)
                temp16a = scale_expansion(temp8, adytail)
                finother = sum_expansions(finnow, temp16a)
                finnow, finother = finother, finnow

            if bdytail != 0.0:
                temp8 = scale_expansion(aa, -cdxtail)
                temp16a = scale_expansion(temp8, bdytail)
                finother = sum_expansions(finnow, temp16a)
                finnow, finother = finother, finnow

            temp32a = scale_expansion(cxtabt, cdxtail)
            cxtabtt = scale_expansion(abtt, cdxtail)

            temp16a = scale_expansion(cxtabtt, 2.0 * cdx)

            temp16b = scale_expansion(cxtabtt, cdxtail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            finother = sum_expansions(finnow, temp64)
            finnow, finother = finother, finnow

        if cdytail != 0.0:
            temp16a = scale_expansion(cytab, cdytail)
            cytabt = scale_expansion(abt, cdytail)

            temp32a = scale_expansion(cytabt, 2.0 * cdy)
            temp48 = sum_expansions(temp16a, temp32a)
            finother = sum_expansions(finnow, temp48)
            finnow, finother = finother, finnow

            temp32a = scale_expansion(cytabt, cdytail)
            cytabtt = scale_expansion(abtt, cdytail)

            temp16a = scale_expansion(cytabtt, 2.0 * cdy)
            temp16b = scale_expansion(cytabtt, cdytail)
            temp32b = sum_expansions(temp16a, temp16b)
            temp64 = sum_expansions(temp32a, temp32b)
            finother = sum_expansions(finnow, temp64)
            finnow, finother = finother, finnow

    return finnow[-1]
