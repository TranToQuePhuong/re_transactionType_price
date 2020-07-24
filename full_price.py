import re

import params
import clean_price


def sell(text, price):
    if price > params.rent_range[1]:
        return True
    elif price > 150000000:
        if re.search(r'bán.*{}'.format(params.land_wh), text, re.I):
            return True
    return False


def rent(data, price):
    if data[1] == 'price_str':
        pr_check = params.rent_range[0] < price < params.rent_range[1]
        if pr_check is True:
            return True
        return False
    if len(data) == 3:
        if params.rent_range[0] < price < params.rent_range[1]:
            return True
    elif re.search(params.r_valid, data[0], re.I):
        pr_check = params.rent_range[0] < price < params.rent_range[1]
        if pr_check is True:
            return True
        return False
    return False


def extract_full_price(data, cate):
    # has_price = re.search(
    #     r'{}{}'.format(params.val_ptrn_s, params.cur_u_man_s), data[0], re.I)
    ptrn = params.val_ptrn_rs + params.cur_u_man_s
    matches = re.findall(ptrn, data[0], re.I)
    for match in matches:
        has_price = re.search(ptrn, ''.join(match), re.I)
        if has_price:
            price = has_price.group(0)
            if re.search(params.time_u, price, re.I):
                return False
            f_pr = clean_price.clean_price(price)
            if cate == 'rent':
                if sell(data[0], f_pr):
                    return True
            if cate == 'rent':
                if rent(data, f_pr):
                    return True
    if re.search(r'(thỏa thuận|thương lượng)', data[0], re.I):
        return False
    return False


def sell_2(text, price):
    if price > params.rent_range[1]:
        return [True, price, 'f_price']
    elif price > 150000000:
        if re.search(r'bán.*{}'.format(params.land_wh), text, re.I):
            return [True, price, 'f_price']
    return [False]


def rent_2(data, price):
    if data[1] == 'price_str':
        pr_check = params.rent_range[0] < price < params.rent_range[1]
        if len(data) == 3:
            if data[2] in [2, 3, 4, 6]:
                pr_check = 1500000 < price < params.rent_range[1]
        if pr_check is True:
            return [True, price, 'f_price']
        return [False]
    if re.search(params.r_valid, data[0], re.I):
        pr_check = params.rent_range[0] < price < params.rent_range[1]
        if pr_check is True:
            return [True, price, 'f_price']
        return [False]
    return [False]


def extract_full_price_2(data, cate):
    # has_price = re.search(
    #     r'{}{}'.format(params.val_ptrn_s, params.cur_u_man_s), data[0], re.I)
    # if has_price:
    #     price = has_price.group(0)
    #     if re.search(params.time_u, price, re.I):
    #         return [False]
    #     f_pr = clean_price.clean_price(price)
    #     if cate == 'rent':
    #         return sell_2(data[0], f_pr)
    #     if cate is 'rent':
    #         return rent_2(data, f_pr)
    ptrn = params.numbers + params.cur_u_man_s
    matches = re.findall(ptrn, data[0], re.I)
    for match in matches:
        has_price = re.search(ptrn, ''.join(match), re.I)
        if has_price:
            price = has_price.group(0)
            if re.search(params.time_u, price, re.I):
                return [False]
            f_pr = clean_price.clean_price(price)
            if cate == 'rent':
                sell_price = sell_2(data[0], f_pr)
                if sell_price[0]:
                    return sell_price
            if cate == 'rent':
                rent_price = rent_2(data, f_pr)
                if rent_price[0]:
                    return rent_price
    if re.search(r'(thỏa thuận|thương lượng)', data[0], re.I):
        return [False]
    return [False]
