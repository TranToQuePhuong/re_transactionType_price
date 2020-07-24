import params
import re
import sys
import functools
from os import path
# data_processing/price
sys.path.append(path.realpath('..'))

USD_2_VND = 23000


def get_money(text, money_bound=1000000):
    val_dict = re.findall(r'\d+', text)
    # Calculate number before currency unit (cur_u)
    prefix = int(val_dict[0]) * money_bound
    if len(val_dict) > 1:
        # Calculate value after keyword
        delete_zeros = re.search(r'(.*(?!0).)*', val_dict[1])
        cleaned_postfix = delete_zeros.group(0)
        # Case '0' -> '' => Must return prefix
        if cleaned_postfix == '':
            return str(prefix)
        if int(cleaned_postfix) < 10:
            postfix = int(cleaned_postfix) * int(money_bound/10)
        elif int(cleaned_postfix) < 100:
            postfix = int(cleaned_postfix) * int(money_bound/100)
        else:
            postfix = int(cleaned_postfix) * int(money_bound/1000)
        val = prefix + postfix
        return str(val)
    # Only one number before cur_u
    else:
        return str(prefix)


def get_money_split(text, money_bound=1000000):
    val_dict = re.findall(r'\d+', text)
    if len(val_dict) > 1:
        prefix = int(val_dict[0]) * money_bound
        if money_bound == 1000000000:
            # Get rid of zeroes
            tmp = re.search(r'[1-9]+0+', val_dict[1])
            if tmp:
                cleaned_postfix = re.sub(r'0+', '', tmp.group(0), flags=re.I)
                val_dict[1] = val_dict[1].replace(tmp.group(0), '')
                cleaned_postfix = val_dict[1] + cleaned_postfix
            else:
                cleaned_postfix = val_dict[1]
        else:
            cleaned_postfix = val_dict[1]

        if len(cleaned_postfix) == 1:
            postfix = int(cleaned_postfix) * int(money_bound/10)
        elif len(cleaned_postfix) == 2:
            postfix = int(cleaned_postfix) * int(money_bound/100)
        elif len(cleaned_postfix) == 3:
            postfix = int(cleaned_postfix) * int(money_bound/1000)
        else:
            postfix = 0
        return str(prefix + postfix)
    # Case .\d+cur_u
    else:
        cleaned_val = re.sub(r'0+', '', val_dict[0])
        val = int(cleaned_val) * int(money_bound/10)
        return str(val)


def clean_price(text, price_cate='full_price'):
    text = re.sub(r'(giá)?\s*(bán|thuê|cho thuê)?\s*:?\s*{}?\s*'.format(params.pr_approximate),
                  '', text, flags=re.I)
    text = re.sub(r'(dự kiến|khoảng|tầm|hơn)', '', text, flags=re.I)
    text = re.sub(r'\s*\/\s*m\s*2', '', text, flags=re.I)
    pr_over_area = re.search(r'{}{}{}'.format(
        params.val_ptrn_rs, params.cur_u_r, r'\s*\/\s*\d+\s*m\s*2'), text, re.I)
    if pr_over_area:
        price_arr = pr_over_area.group(0).split('/')
        price = clean_price(price_arr[0], price_cate=price_cate)
        area = int(re.match(r'\d+', price_arr[1].strip()).group(0))
        return price / area
    if re.search(r'\s*(usd|\$\s*(USD)?|ngàn)\s*', text, re.I):
        if price_cate == 'full_price':
            sub_prices = re.findall(r'\d+', text)
            usd_price = functools.reduce(lambda x, y: x+y, sub_prices)
            vnd_price = int(usd_price) * USD_2_VND
            text = str(vnd_price)
        if price_cate == 'unit_price':
            usd_price = re.sub(
                r'\s*(usd|\$\s*(USD)?|ngàn)\s*', '', text, flags=re.I)
            usd_price = usd_price.replace(',', '.')
            vnd_price = float(usd_price) * USD_2_VND
            text = str(int(vnd_price))
    text = re.sub(r'\s*(VND|VNĐ|đồng|dong|đ)\s*', '', text, flags=re.I)
    # text = re.sub(r'\s*(VND|VNĐ)', '', text, flags=re.I)
    if re.search(r'\s*t[ỉiỷy]\s*\d*', text, re.I):
        if ',' in text or '.' in text:
            text = get_money_split(text, 1000000000)
        else:
            text = get_money(text, 1000000000)
    if re.search(r'\s*(tr|tr(iệ|ie)u)\s*\d*', text, re.I):
        if ',' in text or '.' in text:
            # num [,.] num
            text = get_money_split(text)
        else:
            # num cur_u num
            text = get_money(text)
    if '.' in text:
        text = text.replace('.', '')
    if ',' in text:
        text = text.replace(',', '')
    if re.search(r'th[oỏ]a\s*thu[aạâậ]n', text, re.I):
        text = '0'
    return int(text)
