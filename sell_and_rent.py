import re

import full_price
import params
import unit_price


def get_data(data):
    if data[0] is None:
        return False
    text = data[0].replace('\n', '').replace('\r', '')
    invalid_ptrns = [ #hợp đồng thuê, đang cho thuê các thứ các thứ
        params.s_and_r_ptrn,
        params.s_renting_with_pr_ptrn
    ]
    valid_ptrns = [ #vừa thuê vừa bán các kiểu các kiểu
        params.s_renting_with_pr_ptrn_2,
        params.s_renting_with_pr_ptrn_3
    ]
    for x in invalid_ptrns:
        if not re.search(x, data[0], re.I):
            for y in valid_ptrns:
                if re.search(y, data[0], re.I):
                    if max(data[1])>0 and max(data[2])>0:
                        if max(data[1]) >= 100000000 and max(data[1]) <= 10000000000000:
                            if max(data[2]) > 299999 and max(data[2]) < 500000000:
                                # print(data[1])
                                # print(data[2])
                                # print(data[3])
                                return True
                        # else:
                        #     return False

            # if unit_price.rent(matched.group(0)):
            #     return True
            # if full_price.extract_full_price([matched.group(0), data[0][1], 's_r_w_pr'], 'rent'):
            #     return True
            # if unit_price.sell(matched.group(0)):
            #     return True
    return False

