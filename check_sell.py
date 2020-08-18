import re

import full_price, unit_price
import params, field_name


def extract_number(data):
    if re.search(params.u_pr_s, data[0], re.I):
        if unit_price.extract_unit_price(data[0], field_name.cate_sell):
            return True
    return full_price.extract_full_price(data, field_name.cate_sell)


def to_str(lst):
    string = ''.join(lst)
    return string


def extract_number_lst(data):
    if data[0] in [None, []]:
        return [False]
    tmp = data[0]
    if type(data[0]) is list:
        for x in data[0]:
            recur = extract_number_lst([x, data[1]])
            if recur[0]:
                return recur
        return [False]
        # tmp = to_str(data[0])
    if type(data[0]) is str:
        tmp += ' '
        if re.search(params.u_pr_s_area, tmp, re.I):
            u_pr_s = unit_price.extract_unit_price_2(tmp, field_name.cate_sell)
            if u_pr_s[0]:
                return u_pr_s
        return full_price.extract_full_price_2([tmp, data[1]], field_name.cate_sell)
    return [False]


def check_keyword(text):
    text = re.sub(r'l[uũ]y b[aá]n b[ií]ch', '', text, flags=re.I)
    in_1 = re.search(params.s_in_1, text, re.I)
    in_2 = re.search(params.s_in_2, text, re.I)
    text = re.sub(params.s_renting_with_pr_ptrn, '', text, re.I)
    text = re.sub(params.s_renting_with_pr_ptrn_2, '', text, re.I)
    text = re.sub(params.s_renting_with_pr_ptrn_3, '', text, re.I)
    nin_1 = re.search(params.time_u_2, text, re.I)
    if nin_1:
        return False
    if in_1 or in_2:
        return True
    return False


def get_data(data):
    # data có dạng [sub_data_1, sub_data_2]
    # sub_data_x có dạng [text, field]
    #  - text có thể là giá trị của message hoặc price_str
    #  - field có thể là 'message' hoặc 'price_str
    in_1 = re.search(params.s_in_1, data[0], re.I)
    in_2 = re.search(params.s_in_2, data[0], re.I)
    nin_1 = re.search(params.time_u_2, data[0], re.I)
    if not re.search(params.contract, data[0], re.I):
        if in_1 and in_2 and not nin_1:
            if max(data[1]) >0 and max(data[2]) ==0:
                if max(data[1]) >= 100000000 and max(data[1])<=10000000000000:
                    return True
                # else:
                #     return False
    return False

