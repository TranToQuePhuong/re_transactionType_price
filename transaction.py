from re import findall, search, sub, I
import check_rent
import check_sell
import sell_and_rent
import sell_renting_with_pr as s_r_w_pr
import sell_renting_without_pr as s_r_wo_pr
import transfer
import params
import json
import PostInfo
import codecs


#Price Sell_Rent
def to_str(data):
    if type(data) is str:
        return data
    if type(data) is list:
        return ''.join(data)
    return data


def cal_price_rent(post_info, raw_price, x):
    if x == '':
        return raw_price * post_info.get_info('area_cal')
    price = raw_price
    rent_ptrn = params.val_ptrn + params.cur_u_r + params.time_u
    if type(x) is not str:
        txt = to_str(x[0])
    else:
        txt = x
    if search(rent_ptrn, txt, I):
        if search(r'\/\s*\d*\s*m\s*2', txt, I):
            price *= post_info.get_info('area_cal')
        if search(r'\/\s*1?\s*năm', txt, I):
            price /= 12
    return price


def get_price_rent(post_info, trans_type, attr_price_str):
    if trans_type in [2, 4, 5, 7]:
        data = [(post_info.get_info('content'), 'message'),
                (post_info.get_info('price_str'), 'price_str'),
                (attr_price_str, 'price_str')]
        for x in data:
            price_rent = check_rent.extract_number_lst(x)
            if price_rent[0]:
                if len(price_rent) == 3:
                    return cal_price_rent(post_info, price_rent[1], price_rent[2]) * 1.0
                return cal_price_rent(post_info, price_rent[1], x) * 1.0
        if type(post_info.get_info('price_m2')) in [float, int]:
            tmp = float(post_info.get_info('price_m2'))
            if tmp > 0.0:
                return cal_price_rent(post_info, tmp, '') * 1.0
    return 0.0


def cal_price_sell(post_info, raw_price, x):
    if x == '':
        return raw_price * post_info.get_info('area_cal')
    if x == 'f_price':
        return raw_price
    price = raw_price
    sell_ptrn = params.val_ptrn_s + params.cur_u_s
    txt = to_str(x[0])
    if search(sell_ptrn, txt, I):
        if search(params.u_pr_s_area, txt, I):
            price *= post_info.get_info('area_cal')
    return price


def get_price_sell(post_info, trans_type, attr_price_str):
    if trans_type in [1, 3, 4, 5, 6, 7]:
        data = [(post_info.get_info('content'), 'message'),
                (post_info.get_info('price_str'), 'price_str'),
                (attr_price_str, 'price_str')]
        for x in data:
            price_sell=check_sell.extract_number_lst(x)
            if price_sell[0]:
                if len(price_sell) == 3:
                    return cal_price_sell(post_info, price_sell[1], price_sell[2]) * 1.0
                return cal_price_sell(post_info, price_sell[1], x) * 1.0
        if trans_type != 4:
            if type(post_info.get_info('price_m2')) in [float, int]:
                tmp = float(post_info.get_info('price_m2'))
                if tmp > 0.0:
                    return cal_price_sell(post_info, tmp, '') * 1.0
    return 0.0


#Transaction_type
def get_trans_type(post_info):
    """Phân giải trường `transaction_type` một cách phù hợp
    """

    data = [(post_info.get_info('content'), 'message'),
            (post_info.get_info('price_str'), 'price_str')]
    if post_info.get_info('transaction_type'):
        data.append((post_info.get_info('transaction_type'), 'transaction_type'))
        return filter_post(data)
    """
    Options:
        1 - Post chỉ bán
        2 - Post chỉ thuê
        3 - Post sang nhượng
        4 - Post vừa bán vừa thuê
        5 - Post bán, đang cho thuê, có giá thuê
        6 - Post bán, đang cho thuê, không có giá thuê
        7 - Khác
    """
    for x in [4, 5, 6, 2, 1, 3, 7]:
        if x == 2:
            data.append(('thuê', 'transaction_type'))
        if x in [5, 6]:
            if filter_post_option(data=data, option=1):
                if filter_post_option(data=data, option=x):
                    return x
        elif filter_post_option(data=data, option=x):
            return x


def filter_post(data):
    '''
    1 - Post chỉ bán
    2 - Post chỉ thuê
    3 - Post sang nhượng
    4 - Post vừa bán vừa thuê
    5 - Post bán, đang cho thuê, có giá thuê
    6 - Post bán, đang cho thuê, không có giá thuê
    7 - Khác
    '''
    if sell_and_rent.get_data(data):
        return 4
    if s_r_w_pr.get_data(data):
        return 5
    if s_r_wo_pr.get_data(data):
        return 6
    if check_rent.get_data(data):
        return 2
    if check_sell.get_data(data):
        return 1
    if transfer.get_data(data):
        return 3
    # if s_w_b_p.get_data(data):
    #     return "Post bán và có tiềm năng kinh doanh"
    return 7


def filter_post_option(data, option):
    '''
    Options:
        1 - bán
        2 - thuê
        3 - sang nhượng
        4 - vừa bán vừa thuê
        5 - bán, đang cho thuê, có giá thuê
        6 - bán, đang cho thuê, không có giá thuê
        7 - khác
    '''
    if option == 3:
        return transfer.get_data(data)
    if option == 4:
        return sell_and_rent.get_data(data)
    if option == 5:
        return s_r_w_pr.get_data(data)
    if option == 6:
        return s_r_wo_pr.get_data(data)
    if option == 2:
        return check_rent.get_data(data)
    if option == 1:
        return check_sell.get_data(data)
    if option == 7:
        return True

with open('data.json', encoding="utf-8") as json_file:
    dataset = json.load(json_file)
    for data in dataset:
        post_info = PostInfo()
        print (get_trans_type(post_info))



