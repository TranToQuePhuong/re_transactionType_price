import re

import params, field_name
import clean_price


def sell(text):
    has_u_pr_s = re.search(r'{}{}{}'
                           .format(params.val_ptrn_s, params.cur_u_s, params.u_pr_s), text, re.I)
    if has_u_pr_s:
        price = has_u_pr_s.group(0)
        if re.search(r'\s*\/\s*1?\s*th([áa]ng)?', price, re.I):
            return False
        u_pr_s = clean_price.clean_price(price)
        if int(u_pr_s) < 1000000:
            return False
        return True
    return False


def rent(text):
    u_pr_ptrn = re.compile('{}{}{}'
                           .format(params.val_ptrn, params.cur_u_r, params.time_u), re.I)
    has_ptrn = re.search(u_pr_ptrn, text)
    if has_ptrn:
        postfix = has_ptrn.group(has_ptrn.lastindex)
        val = has_ptrn.group(0).replace(postfix, '')
        u_pr_r = clean_price.clean_price(val)
        if re.search(r'\/\s*m\s*2(\s*\/\s*1?\s*th([áa]ng)?)?', postfix, re.I):
            if u_pr_r < 20000 or u_pr_r > 4000000:
                return False
        elif re.search(r'(\/\s*1\s*năm|\/\s*năm)', postfix, re.I):
            u_pr_r = int(u_pr_r/12)
            if u_pr_r < 20000 or u_pr_r > 4000000:
                return False
        return True
    return False


def extract_unit_price(text, cate):
    if cate == field_name.cate_sell:
        return sell(text)
    return rent(text)


def sell_2(text):
    has_u_pr_s = re.search(r'{}{}{}'
                           .format(params.val_ptrn_s, params.cur_u_s, params.u_pr_s_area), text, re.I)
    if has_u_pr_s:
        price = has_u_pr_s.group(0)
        if re.search(r'\s*\/\s*1?\s*th([áa]ng)?', price, re.I):
            return [False]
        u_pr_s = clean_price.clean_price(price, 'unit_price')
        if u_pr_s < 500000:
            return [False]
        return [True, u_pr_s, has_u_pr_s.group(0)]
    return [False]


def rent_2(text):
    u_pr_ptrn = re.compile('{}{}{}'
                           .format(params.val_ptrn, params.cur_u_r, params.time_u), re.I)
    has_ptrn = re.search(u_pr_ptrn, text)
    # print(has_ptrn)
    if has_ptrn:
        postfix = has_ptrn.group(has_ptrn.lastindex)
        # print('postfix: ', postfix)
        if re.search(r'\/\s*\d+\s*m\s*2', postfix, re.I):
            val = has_ptrn.group(0)
        else:
            val = has_ptrn.group(0).replace(postfix, '')
        # print('val: ', val)
        u_pr_r = clean_price.clean_price(val, 'unit_price')
        # print('u_pr_r: ', str(u_pr_r))
        if re.search(r'(\/\s*1?\s*th([áa]ng)?\s*\/\s*m\s*2|\/\s*\d*\s*m\s*2(\s*\/\s*1?\s*th([áa]ng)?)?)', postfix, re.I):
            if u_pr_r < 9000 or u_pr_r > 4000000:
                return [False]
            return [True, u_pr_r, has_ptrn.group(0)]
        if re.search(r'(\/\s*1\s*năm|\/\s*năm)', postfix, re.I):
            u_pr_r = int(u_pr_r/12)
            if u_pr_r < 9000 or u_pr_r > 4000000:
                return [False]
            return [True, u_pr_r, has_ptrn.group(0)]
        if u_pr_r > 4000000:
            return [True, u_pr_r, has_ptrn.group(0)]
    return [False]


def extract_unit_price_2(text, cate):
    if cate == field_name.cate_sell:
        return sell_2(text)
    return rent_2(text)
