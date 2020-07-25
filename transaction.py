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
    att = post_info['attributes']
    for i in range(0, len(att)):
        if att[i]['type'] == 'area':
            if x == '':
                return raw_price * att[i]['content']
            price = raw_price
            rent_ptrn = params.val_ptrn + params.cur_u_r + params.time_u
            if type(x) is not str:
                txt = to_str(x[0])
            else:
                txt = x
            if search(rent_ptrn, txt, I):
                if search(r'\/\s*\d*\s*m\s*2', txt, I):
                    price *= att[i]['content']
                if search(r'\/\s*1?\s*năm', txt, I):
                    price /= 12
            return price


def get_price_rent(post_info, trans_type, attr_price_str):
    if trans_type in [2, 4, 5, 7]:
        att = post_info['attributes']
        for i in range(0, len(att)):
            if att[i]['type'] == 'price':
                data = [(post_info['content'], 'message'),
                        (att[i]['type'], 'price'),
                        (attr_price_str, 'price')]
                for x in data:
                    price_rent = check_rent.extract_number_lst(x)
                    if price_rent[0]:
                        if len(price_rent) == 3:
                            return cal_price_rent(post_info, price_rent[1], price_rent[2]) * 1.0
                        return cal_price_rent(post_info, price_rent[1], x) * 1.0
                if att[i]['type'] == 'area':
                    if type(att[i]['content']) in [float, int]:
                        tmp = float(att[i]['content'])
                        if tmp > 0.0:
                            return cal_price_rent(post_info, tmp, '') * 1.0
    return 0.0


def cal_price_sell(post_info, raw_price, x):
    att = post_info['attributes']
    for i in range(0, len(att)):
        if att[i]['type'] == 'area':
            if x == '':
                return raw_price * att[i]['content']
            if x == 'price':
                return raw_price
            price = raw_price
            sell_ptrn = params.val_ptrn_s + params.cur_u_s
            txt = to_str(x[0])
            if search(sell_ptrn, txt, I):
                if search(params.u_pr_s_area, txt, I):
                    price *= att[i]['content']
            return price


def get_price_sell(post_info, trans_type, attr_price_str):
    if trans_type in [1, 3, 4, 5, 6, 7]:
        att = post_info['attributes']
        for i in range(0, len(att)):
            if att[i]['type'] == 'price':
                data = [(post_info['content'], 'message'),
                    (att[i]['content'], 'price'),
                    (attr_price_str, 'price')]
                for x in data:
                    price_sell=check_sell.extract_number_lst(x)
                    if price_sell[0]:
                        if len(price_sell) == 3:
                            return cal_price_sell(post_info, price_sell[1], price_sell[2]) * 1.0
                        return cal_price_sell(post_info, price_sell[1], x) * 1.0
                if trans_type != 4:
                    if att[i]['type'] =='area':
                        if type(att[i]['type']) in [float, int]:
                            tmp = float(att[i]['type'])
                        if tmp > 0.0:
                            return cal_price_sell(post_info, tmp, '') * 1.0
    return 0.0


#Transaction_type
def get_trans_type(post_info,iprice,itrans):
    """Phân giải trường `transaction_type` một cách phù hợp
    """
    att = post_info['attributes']
    data = [(post_info['content'],'message'),(att[iprice]['content'],'price')]

    if att[itrans]['content']:
        data.append((att[itrans]['content'], 'transaction_type'))
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
    elif s_r_w_pr.get_data(data):
        return 5
    elif s_r_wo_pr.get_data(data):
        return 6
    elif check_rent.get_data(data):
        return 2
    elif check_sell.get_data(data):
        return 1
    elif transfer.get_data(data):
        return 3
    # if s_w_b_p.get_data(data):
    #     return "Post bán và có tiềm năng kinh doanh"
    else:
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
    count_1=0
    count_2=0
    count_3=0
    count_4=0
    count_5=0
    count_6=0
    count_7=0
    for data in dataset:
        att = data['attributes']
        tmp1=-1
        tmp2=-1
        for i in range(0, len(att)):
            if att[i]['type'] == 'price':
                tmp1=i
            if att[i]['type'] == 'transaction_type':
                tmp2=i
        print(data['id'])
        #print(data['content'])
        print("Transaction_type: ", get_trans_type(data,tmp1,tmp2))
        #   if att[i]['type'] == 'price':
        #      print("Price_sell: ", get_price_sell(data,get_trans_type(data),att[i]['content']))
        #      print("Price_rent: ", get_price_rent(data,get_trans_type(data),att[i]['content']))
        if get_trans_type(data,tmp1,tmp2)==1:
            count_1 = count_1 + 1
        elif get_trans_type(data,tmp1,tmp2)==2:
            count_2 = count_2 + 1
        elif get_trans_type(data,tmp1,tmp2)==3:
            count_3 = count_3 + 1
        elif get_trans_type(data,tmp1,tmp2)==4:
            count_4 = count_4 + 1
        elif get_trans_type(data,tmp1,tmp2)==5:
            count_5 = count_5 + 1
        elif get_trans_type(data,tmp1,tmp2)==6:
            count_6 = count_6 + 1
        elif get_trans_type(data,tmp1,tmp2)==7:
            count_7 = count_7 + 1
        print("\n")

    print(count_1)
    print(count_2)
    print(count_3)
    print(count_4)
    print(count_5)
    print(count_6)
    print(count_7)

       # print ("Price_sell: ", get_price_sell(data,get_trans_type(data), price))



