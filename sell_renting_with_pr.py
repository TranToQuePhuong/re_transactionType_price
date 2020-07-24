import re

import params
import unit_price, full_price


def get_data(data):
    valid_ptrns = [
        params.s_renting_with_pr_ptrn,
        params.s_renting_with_pr_ptrn_2,
        params.s_renting_with_pr_ptrn_3
    ]
    for x in valid_ptrns:
        matched = re.search(x, data[0][0], re.I)
        if matched:
            if unit_price.rent(matched.group(0)):
                return True
            if full_price.extract_full_price([matched.group(0), data[0][1], 's_r_w_pr'], 'rent'):
                return True
    return False
