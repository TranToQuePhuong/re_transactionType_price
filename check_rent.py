import re

import full_price, unit_price
import params


def check_keyword(text):
    valid = 0
    invalid = 0
    if text is None:
        return False
    in_1 = re.search(params.r_valid, text, re.I)
    nin_1 = re.search(params.r_nin_1, text, re.I)
    nin_2 = re.search(params.r_nin_2, text, re.I)
    nin_3 = re.search(params.r_nin_3, text, re.I)
    nin_4 = re.search(params.r_nin_4, text, re.I)
    nin_5 = re.search(params.r_nin_5, text, re.I)
    nin_6 = re.search(params.r_nin_6, text, re.I)
    if in_1:
        valid += 1
    if nin_1:
        invalid += 1
    elif nin_2:
        invalid += 1
    elif nin_3:
        invalid += 1
    elif nin_4:
        invalid += 1
    elif nin_5:
        invalid += 1
    elif nin_6:
        invalid += 1
    if invalid == 0:
        if valid > 0:
            return True
        return False
    return False


def extract_number_boolean(data):
    if data[1] == 'price':
        return full_price.extract_full_price(data, 'rent')
    if unit_price.extract_unit_price(data[0], 'rent'):
        return True
    return full_price.extract_full_price(data, 'rent')


def to_str(lst):
    string = ''.join(lst)
    return string


def extract_number_lst(data):
    if data[0] is None:
        return [False]
    tmp = data[0]
    if type(data[0]) is list:
        for x in data[0]:
            recur = extract_number_lst([x, data[1]])
            if recur[0]:
                return recur
        return [False]
        # tmp = to_str(data[0])
    if data[1] == 'price':
        return full_price.extract_full_price_2([tmp, data[1]], 'rent')
    u_pr = unit_price.extract_unit_price_2(tmp, 'rent')
    if u_pr[0]:
        return u_pr
    return full_price.extract_full_price_2([tmp, data[1]], 'rent')


def get_data(data):
    in_1 = re.search(params.r_valid, data[0], re.I)
    nin_1 = re.search(params.r_nin_1, data[0], re.I)
    nin_2 = re.search(params.r_nin_2, data[0], re.I)
    nin_3 = re.search(params.r_nin_3, data[0], re.I)
    nin_4 = re.search(params.r_nin_4, data[0], re.I)
    nin_5 = re.search(params.r_nin_5, data[0], re.I)
    nin_6 = re.search(params.r_nin_6, data[0], re.I)
    if not re.search(params.contract, data[0], re.I):
        if in_1 and not nin_1 and not nin_2 and not nin_3 and not nin_4 and not nin_5 and not nin_6:
            if max(data[1])==0 and max(data[2])>0:
                if max(data[2]) > 299999 and max(data[2]) <500000000:
                    return True
                # else:
                #     return False
    return False
