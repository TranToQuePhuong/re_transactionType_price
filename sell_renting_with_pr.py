import re

import params
import unit_price, full_price


def get_data(data):
    valid_ptrns = [
        params.s_and_r_ptrn,
        params.s_renting_with_pr_ptrn,
        params.s_renting_with_pr_ptrn_2,
        params.s_renting_with_pr_ptrn_3
    ]
    for x in valid_ptrns:
        matched = re.search(x, data[0], re.I)
        if matched:
            if max(data[1])>0 and max(data[2])>0:
                if max(data[1]) >= 100000000 and max(data[1]) <=10000000000000:
                    if max(data[2]) > 299999 and max(data[2]) < 500000000:
                        return True
                # else:
                #     return False

    return False
