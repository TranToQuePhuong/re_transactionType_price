from re import findall, search, sub, I
import re
import check_rent
import check_sell
import full_price
import sell_and_rent
import sell_renting_with_pr as s_r_w_pr
import sell_renting_without_pr as s_r_wo_pr
import transfer
import params
import json
import PostInfo
import codecs

# Price Sell_Rent
import unit_price
from xacdinh import xacdinh


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
                    price_sell = check_sell.extract_number_lst(x)
                    #print(price_sell)
                    if price_sell[0]:
                        if len(price_sell) == 3:
                            if price_sell[1] == None:
                                price_sell[1] = 0
                            if price_sell[2] == None:
                                price_sell[2] = 0
                            return cal_price_sell(post_info, price_sell[1], price_sell[2]) * 1.0
                        return cal_price_sell(post_info, price_sell[1], x) * 1.0
                if trans_type != 4:
                    if att[i]['type'] == 'area':
                        if type(att[i]['type']) in [float, int]:
                            tmp = float(att[i]['type'])
                        if tmp > 0.0:
                            return cal_price_sell(post_info, tmp, '') * 1.0
    return 0.0


# Transaction_type
#
def get_trans_type(post_info):
    """Phân giải trường `transaction_type` một cách phù hợp
    """
    #att = post_info['attributes']
    #data = [(post_info['content'], 'message'), (getFullPrice(post_info), 'price')]

    # if att[itrans]['content']:
    #     data.append((att[itrans]['content'], 'transaction_type'))
    pText= phuong(post_info)
    priceSell, priceRent = getFullPrice(pText)
    data=[post_info['content'], priceSell, priceRent,post_info['id']]
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
    if s_r_w_pr.get_data(data):
        return 5
    if s_r_wo_pr.get_data(data):
        return 6
    if sell_and_rent.get_data(data):
        return 4
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


s1 = u'ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ'
s0 = u'AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy'


def remove_accents(input_str):
    s = ''
    for c in input_str:
        if c in s1:
            s += s0[s1.index(c)]
        else:
            s += c
    return s


def find_sub_list(sl, l):
    results = []
    sll = len(sl)
    for ind in (i for i, e in enumerate(l) if e == sl[0]):
        if l[ind:ind + sll] == sl:
            results.append((ind, ind + sll - 1))
    # print(results)
    return results


def getPriceSpace(textPrice):
    price = ''
    # print(textPrice)
    for i in textPrice:
        # print(i)
        if i.isdigit() or i == ',' or i == '.':
            price = price + i
        else:
            break
    return price


# print(getPriceSpace('45trm2'))

numbers = r'(\d+)\s*(,\s*\d+)*(\.\s*\d+)*'
cur_u_man_r = r'\s*(trieu\s*\d*|trieu\s*\d*|tr\s+\d*|t[i|y]\s*)\s*(\/\s*1?\s*thang)?(\/\s*1?\s*nam)?(\/\s*1?\s*m\s?2)?'


def get_price_keyword(data):
    result = []
    content_tmp = ''
    for attr in data['attributes']:
        content_tmp += attr['content'] + ' '
    content_tmp = remove_accents(content_tmp).lower()
    content = ''
    for i in range(len(content_tmp)):
        if content_tmp[i] == '\n' or content_tmp[i] == '\r':
            continue
        content += content_tmp[i]
    # result.append(data['id'])
    cur_list = re.findall(numbers + cur_u_man_r, content)
    for cur in cur_list:
        str = ''
        for word in cur:
            if word == '' or cur.index(word) == 0:
                str += word
            elif word[0] == '.' or word[0] == ',':
                str += word[0] + word[2:len(word)]
            else:
                str += ' ' + word
        if str[-1] == ' ':
            str = str[0:len(str) - 1]
        result.append(str)
    return result


def phuong(data):
    ban = []
    thue = []
    aBan = []
    aThue = []
    addrB = []
    addrT = []

    index = []
    ind = []
    #for data in dataset:
    ban.append(data['id'])
    thue.append(data['id'])
    content = ''
    for attrs in data['attributes']:
        content += attrs['content'] + ' '
    content = remove_accents(data['content']).lower().split(' ')
    # print(content[135])
    for c in range(0, len(content)):
        if content[c] in ['#ban', 'ban', 'ban,', 'ban.', 'ban:', '#nhuong', 'nhuong', 'nhuong,', 'nhuong.', 'nhuong:']:
            addrB.append(c)
        if content[c] in ['thue', 'thue,', 'thue.', 'thue:']:
            addrT.append(c)
        continue
    ban.append(addrB)
    thue.append(addrT)
    aBan=ban
    aThue=thue
    # print("hi",aBan)
    # print("he",aThue)
    # aBan.append(ban)
    # aThue.append(thue)
    # ban = []
    # thue = []
    # addrB = []
    # addrT = []

    ind.append(data['id'])
    test = get_price_keyword(data)
    # print("test", test)
    text = []
    addr = []
    for t in test:
        # t.split(' ')
        for i in content:
            # print(i)
            iPrice = getPriceSpace(i)
            # print(iPrice)
            if iPrice == t.split(' ')[0]:
                # print(content.index(i))
                text.append(t)
                addr.append(content.index(i))
                break
    ind.append(text)
    ind.append(addr)
    # print(data['id'])
    index=ind
    #ind = []
    text = []
    addr = []
    # print("Price index: ", index)
    # print("Ban index: ", aBan)
    # print("Thue index: ", aThue)

    res = []
    result = []
    Done = []
    #for i in range(0, len(dataset)):
    price = []
    #print(aBan)
    if len(index[1]) == 0:
        res.append(data)
        price.append("0 ty+None")
    else:
        res.append(data)
        if index[1] != []:
            for p in index[1]:
                if aBan[1] == [] and aThue[1] == []:
                    price.append(p + "+None")
                elif aBan[1] != [] and aThue[1] == []:
                    # if p not in Done:
                    #     Done.append(p)
                    price.append(p + "+Ban")
                elif aBan[1] == [] and aThue[1] != []:
                    # if p not in Done:
                    #     Done.append(p)
                    price.append(p + "+Thue")
                else:
                    sellB = []
                    rentB = []
                    sellA = []
                    rentA = []
                    maxsellB = -1
                    maxrentB = -1
                    # for q in range(0, len(index[2])):
                    if len(aBan[1]) >= 1:
                        for b in range(0, len(aBan[1])):
                            if aBan[1][b] < index[2][index[1].index(p)]:
                                maxsellB = aBan[1][b]
                                # sellB.append(aBan[1][b])
                            elif aBan[1][b] > index[2][index[1].index(p)]:
                                sellA.append(aBan[1][b])
                                break
                            else:
                                continue
                        if maxsellB != -1:
                            sellB.append(maxsellB)

                    if len(aThue[1]) >= 1:
                        for th in range(0, len(aThue[1])):
                            if aThue[1][th] < index[2][index[1].index(p)]:
                                maxrentB = aThue[1][th]
                                #rentB.append(aThue[1][th])
                            elif aThue[1][th] > index[2][index[1].index(p)]:
                                rentA.append(aThue[1][th])
                                break
                            else:
                                continue
                        if maxrentB != -1:
                            rentB.append(maxrentB)
                    # print("Price index: ", index)
                    # print("hi", sellB)
                    # print("lo",rentB)
                    # print(p)
                    # print(Done)
                    if sellB != [] and rentB != []:

                        if sellB[0] < rentB[0]:

                            if p not in Done:
                                Done.append(p)
                                price.append(p + "+Thue")
                        else:
                            if p not in Done:
                                Done.append(p)
                                price.append(p + "+Ban")
                    elif sellB != [] and rentB == []:
                        if p not in Done:
                            Done.append(p)
                            price.append(p + "+Ban")
                    elif sellB == [] and rentB != []:
                        if p not in Done:
                            Done.append(p)
                            price.append(p + "+Thue")
                    else:
                        #print("hihi", index)
                        if sellA != [] and rentA != []:
                            if sellA[0] < rentA[len(rentA) - 1]:
                                if p not in Done:
                                    Done.append(p)
                                    price.append(p + "+Ban")
                            else:
                                if p not in Done:
                                    Done.append(p)
                                    price.append(p + "+Thue")
                        elif sellA != [] and rentA == []:
                            if p not in Done:
                                Done.append(p)
                                price.append(p + "+Ban")
                        elif sellA == [] and rentA != []:
                            if p not in Done:
                                Done.append(p)
                                price.append(p + "+Thue")
                        elif sellA == [] and rentA == []:
                            price.append(p + "+None")
                    sellA = []
                    sellB = []
                    rentA = []
                    rentB = []
    res.append(price)
    result=res
    #result.append(res)
        #res = []
        # print(result)

    return result


def getFullPrice(listPhuong):
    lstPriceSell = []
    lstPriceRent = []
    # lstPriceUnknown = []
    for p in listPhuong[1]:
        priceAndType = p.split('+')
        priceAndType.insert(0, listPhuong[0]) # ???????????????????????
        # print(priceAndType)

        resultPrice = get_price(priceAndType)

        # print('result price', resultPrice)
        if resultPrice[1] == 0:
            lstPriceSell.append(resultPrice[0])
        elif resultPrice[1] == 1:
            lstPriceRent.append(resultPrice[0])
        # elif resultPrice[1] == 2 and lstPriceRent != [] and lstPriceSell != []:
        #     lstPriceSell.append(0)
        #     lstPriceRent.append(0)
    if not lstPriceRent:
        lstPriceRent.append(0)
    if not lstPriceSell:
        lstPriceSell.append(0)
    return lstPriceSell,lstPriceRent

    #print('Price Sell', lstPriceSell)
    #print('Price Rent', lstPriceRent)
    #print('\n')
    # print(lstPriceUnknown)


def get_price(priceAndType):
    ty = ['ty', 'ti']
    trieu = ['trieu', 'tr']
    nam = ['nam']

    gia = []

    priceAndType[1] = remove_accents(priceAndType[1]).lower().split(' ')
    # print("a", priceAndType[1])

    for t in ty:
        if t in priceAndType[1] or (t + 'TL') in priceAndType[1]:
            k = 1000000000
    for tr in trieu:
        if tr in priceAndType[1] or (tr + 'TL') in priceAndType[1]:
            k = 1000000

    if ',' in priceAndType[1][0]:
        lstT = priceAndType[1][0].split(',')
        priceAndType[1][0] = lstT[1]
        priceAndType[1].insert(0, ',')
        priceAndType[1].insert(0, lstT[0])
        pivot = priceAndType[1].index(',')
        f = priceAndType[1][pivot - 1]
        s = priceAndType[1][pivot + 1]
        if f.isdigit() and s.isdigit():
            gia.append(float(f + '.' + s) * k)

    if '.' in priceAndType[1][0]:
        lstT = priceAndType[1][0].split('.')
        priceAndType[1][0] = lstT[1]
        priceAndType[1].insert(0, '.')
        priceAndType[1].insert(0, lstT[0])
        # print(priceAndType[1])
        pivot = priceAndType[1].index('.')
        if pivot < len(priceAndType[1]) - 1:
            f = priceAndType[1][pivot - 1]
            s = priceAndType[1][pivot + 1]
            if f.isdigit() and s.isdigit():
                gia.append(float(f + '.' + s) * k)

    if len(gia) == 0:
        check_t_tr = 0
        for t in ty:
            if t in priceAndType[1] or (t + 'TL') in priceAndType[1]:
                pivot = priceAndType[1].index(t)
                k = 1000000000
                if pivot < len(priceAndType[1]) - 1:
                    if priceAndType[1][pivot - 1].isdigit():
                        if priceAndType[1][pivot + 1].isdigit():
                            gia.append(k * float(priceAndType[1][pivot - 1] + '.' + priceAndType[1][pivot + 1]))
                            check_t_tr += 1
                        else:
                            gia.append(k * float(priceAndType[1][pivot - 1]))

                else:
                    if priceAndType[1][pivot - 1].isdigit():
                        gia.append(k * float(priceAndType[1][pivot - 1]))

        if check_t_tr != 1:
            check_t = 0
            for tr in trieu:
                if tr in priceAndType[1] or (tr + 'TL') in priceAndType[1]:
                    pivot = priceAndType[1].index(tr)
                    k = 1000000
                    if priceAndType[1][pivot - 1].isdigit():
                        gia.append(k * float(priceAndType[1][pivot - 1]))
                check_t = 1

            if check_t == 1:
                if 'm' in priceAndType[1]:
                    tmp = str(priceAndType[0]['id']) + 'can xac dinh lai'
                    if xacdinh(priceAndType[0]) > 0 and xacdinh(priceAndType[0]) != tmp:
                        #print("Area: ", xacdinh(priceAndType[0]))
                        if len(gia) > 0:
                            gia[0] = gia[0] * xacdinh(priceAndType[0])
    for n in nam:
        if n in priceAndType[1]:
            if len(gia) > 0:
                gia[0] = gia[0] / 12

    # print(priceAndType[2])
    if priceAndType[2] == 'Ban':
        gia.append(0)
    elif priceAndType[2] == 'Thue':
        gia.append(1)
    elif priceAndType[2] == 'None':
        gia.append(2)

    # print("giá", gia)
    return gia


# with open('data.json', "rb") as json_file:
with open('data.json', 'rb') as json_file:
    dataset = json.loads(json_file.read())

    count_1=0
    count_2=0
    count_3=0
    count_4=0
    count_5=0
    count_6=0
    count_7=0
    for data in dataset:
        #print(data['id'])
        #print(get_trans_type(data)
        # if data['id'] != 119696:
        #     continue
        if get_trans_type(data) == 1:
            count_1 = count_1 + 1
        elif get_trans_type(data)==2:
            count_2 = count_2 + 1
        elif get_trans_type(data)==3:
            count_3 = count_3 + 1
        elif get_trans_type(data)==4:
            # print(data['id'])
            # print("Transaction_type: ", get_trans_type(data, tmp1, tmp2))
            # print(data['content'])
            count_4 = count_4 + 1
        elif get_trans_type(data)==5:
            # print(data['id'])
            # print("Transaction_type: ", get_trans_type(data, tmp1, tmp2))
            # print(data['content'])
            count_5 = count_5 + 1
        elif get_trans_type(data)==6:
            # print(data['id'])
            # print("Transaction_type: ", get_trans_type(data, tmp1, tmp2))
            # print(data['content'])
            count_6 = count_6 + 1
        elif get_trans_type(data)==7:
            count_7 = count_7 + 1
        # print(get_price_keyword(data))
        # print(phuong(data))
    print(count_1)
    print(count_2)
    print(count_3)
    print(count_4)
    print(count_5)
    print(count_6)
    print(count_7)










    # dataset = json.load(json_file)
    # test=[[[118941], ['25 tr/ tháng', '70 tỉ', '6.4 tỉ', '5 tr/ m2']]
    # listDatasetTest = []
    # for i in dataset:
    #     if i['id'] == 119364:
    #         listDatasetTest.append(i)
    # print(phuong(listDatasetTest))

    #newdata = phuong(dataset)
    # print(newdata)


    # for i in newdata:
    #     if len(i) == 0:
    #         print(i)
    #         continue
    #     else:
    #         print(i[0]['id'])
    #         print(i[1])
    #         getFullPrice(i)

        #
        # for i in test:
        #     #print(i)
        #     #print(data['id'])
        #     #print(thue)
        #     if ban == [] and thue==[]:
        #         i=i+'+None'
        #         #print(i)
        #         continue
        #     icontent = i.lower().split(' ')
        #     #print(icontent)
        #     dBan = 10000000
        #     dThue = 10000000
        #     if find_sub_list(icontent,content) != []:
        #         ind=find_sub_list(icontent, content)[0][0]
        #         #print("Index: ",ind)
        #         if len(ban)>0:
        #             for j in ban:
        #                 #print(c)
        #                 if abs(ind-j)<dBan:
        #                     #print("JBan: ",j)
        #                     dBan=abs(ind-j)
        #                 else:
        #                     continue
        #         if len(thue)>0:
        #             for j in thue:
        #                 if abs(ind-j)<dThue:
        #                     #print("JThue: ",j)
        #                     dThue=abs(ind-j)
        #                 else:
        #                     continue
        #         if len(ban)>0 and len(thue)>0:
        #             if dBan < dThue:
        #                 i = i + '+Bán'
        #             else:
        #                 i = i + '+Thuê'
        #         elif len(ban)>0 and len(thue)==0:
        #             print(len(thue))
        #             i=i+'+Bán'
        #         elif len(ban)==0 and len(thue)>0:
        #             i = i + '+Thuê'
        #         print("Ban: ",dBan)
        #         print("Thue: ",dThue)
        #         print(data['id'])
        #         print(i)
        # ban=[]
        # thue=[]
        # print(data['id'])
        # print(i)

    # a = ['một', 'con', 'vịt', 'có', '25', 'cái', 'cánh', 'giá', '25', 'triệu', '/', 'tháng']
    # b = ['25', 'triệu', '/', 'tháng']
    # print(find_sub_list(b, a))

    # ty=['ty','ti']
    # trieu=['trieu','tr']
    # nam=['nam']
    # ty=r't[iIĩĨỉỈyYỹỸỷỶ]'
    # for data in dataset:
    #     attribute = data['attributes']
    #     # if data['id'] != 118318:
    #     #   continue
    #     print(data['id'])
    #     price_sell = 0
    #     price_rent = 0
    #     for i in range(0, len(attribute)):
    #         gia = []
    #         if attribute[i]['type'] == 'price':
    #             # print(attribute[i]['content'])
    #             price = remove_accents(attribute[i]['content']).lower().split(' ')
    #             for word in ['toi','den','-', '~']:
    #                 while word in price:
    #                     price = price[price.index(word) + 1: len(price)]
    #
    #             k = 1
    #             # print(price)
    #             print(price)
    #             for t in ty:
    #                 if t in price or (t + 'TL') in price[::-1]:
    #                     k = 1000000000
    #             for tr in trieu:
    #                 if tr in price or (tr + 'TL') in price:
    #                     k = 1000000
    #
    #             if ',' in price:
    #                 pivot = price.index(',')
    #                 # pivot=price.index('.')
    #                 f = price[pivot - 1]
    #                 s = price[pivot + 1]
    #                 if f.isdigit() and s.isdigit():
    #                     gia.append(float(f + '.' + s) * k)
    #                     # print(data['id'])
    #                     # print(price)
    #                     # print(gia)
    #             if '.' in price:
    #                 pivot = price.index('.')
    #                 # pivot=price.index('.')
    #                 if pivot < len(price) - 1:
    #                     f = price[pivot - 1]
    #                     s = price[pivot + 1]
    #                     if f.isdigit() and s.isdigit():
    #                         gia.append(float(f + '.' + s) * k)
    #
    #             # print(price)
    #             if len(gia) == 0:
    #                 check_t_tr = 0
    #                 for t in ty:
    #                     if t in price or (t + 'TL') in price[::-1]:
    #                         pivot = price.index(t)
    #                         k = 1000000000
    #                         if pivot < len(price) - 1:
    #                             if price[pivot - 1].isdigit():
    #                                 if price[pivot + 1].isdigit():
    #                                     gia.append(k * float(price[pivot - 1] + '.' + price[pivot + 1]))
    #                                     check_t_tr += 1
    #                                 else:
    #                                     gia.append(k * float(price[pivot - 1]))
    #
    #                         else:
    #                             if price[pivot - 1].isdigit():
    #                                 gia.append(k * float(price[pivot - 1]))
    #
    #                 if check_t_tr != 1:
    #                     check_t=0
    #                     for tr in trieu:
    #                         if tr in price or (tr + 'TL') in price:
    #                             pivot = price.index(tr)
    #                             k = 1000000
    #                             if price[pivot - 1].isdigit():
    #                                 gia.append(k * float(price[pivot - 1]))
    #                         check_t=1
    #
    #                     if check_t==1:
    #                         if 'm' in price:
    #                                 tmp = str(data['id']) + 'can xac dinh lai'
    #                                 if xacdinh(data) > 0 and xacdinh(data) != tmp:
    #                                     print("Area: ",xacdinh(data))
    #                                     if len(gia) >0:
    #                                         gia[0]=gia[0] * xacdinh(data)
    #             for n in nam:
    #                 if n in price:
    #                     if len(gia) > 0:
    #                         gia[0] = gia[0] /12
    #
    #
    #             print(gia)
    #
    #
    #
    #             # print(price)
    #             # print(gia)
    #             j = i
    #             while True:
    #                 j = j - 1
    #                 if j < 0:
    #                     break
    #                 content = attribute[j]['content'].lower()
    #                 if 'bán' in content:
    #                     if len(gia) > 0:
    #                         price_sell = gia[0]
    #                         print('Price sell =', price_sell)
    #                         break
    #                 elif 'thuê' in content:
    #                     if len(gia) > 0:
    #                         price_rent = gia[0]
    #                         print('Price rent =', price_rent)
    #                         break
    #         if i == len(attribute) - 1:
    #             if price_sell == 0:
    #                 print('Price sell = ', price_sell)
    #             if price_rent == 0:
    #                 print('Price rent = ', price_rent)
    #
    # # dataset = json.load(json_file)
    # # count_1=0
    # # count_2=0
    # # count_3=0
    # # count_4=0
    # # count_5=0
    # # count_6=0
    # # count_7=0
    # # for data in dataset:
    # #     att = data['attributes']
    # #     tmp1=-1
    # #     tmp2=-1
    # #     for i in range(0, len(att)):
    # #         if att[i]['type'] == 'price':
    # #             tmp1=i
    # #         if att[i]['type'] == 'transaction_type':
    # #             tmp2=i
    # #     #print(data['id'])
    # #     #print("Transaction_type: ", get_trans_type(data,tmp1,tmp2))
    # #         if att[i]['type'] == 'price':
    # #           print("Price_sell: ", get_price_sell(data,get_trans_type(data,tmp1,tmp2),att[i]['content']))
    # #           print("Price_rent: ", get_price_rent(data,get_trans_type(data,tmp1,tmp2),att[i]['content']))
    # #     if get_trans_type(data,tmp1,tmp2)==1:
    # #         count_1 = count_1 + 1
    # #     elif get_trans_type(data,tmp1,tmp2)==2:
    # #         count_2 = count_2 + 1
    # #     elif get_trans_type(data,tmp1,tmp2)==3:
    # #         count_3 = count_3 + 1
    # #     elif get_trans_type(data,tmp1,tmp2)==4:
    # #         print(data['id'])
    # #         print("Transaction_type: ", get_trans_type(data, tmp1, tmp2))
    # #         print(data['content'])
    # #         count_4 = count_4 + 1
    # #     elif get_trans_type(data,tmp1,tmp2)==5:
    # #         print(data['id'])
    # #         print("Transaction_type: ", get_trans_type(data, tmp1, tmp2))
    # #         print(data['content'])
    # #         count_5 = count_5 + 1
    # #     elif get_trans_type(data,tmp1,tmp2)==6:
    # #         print(data['id'])
    # #         print("Transaction_type: ", get_trans_type(data, tmp1, tmp2))
    # #         print(data['content'])
    # #         count_6 = count_6 + 1
    # #     elif get_trans_type(data,tmp1,tmp2)==7:
    # #         count_7 = count_7 + 1
    # #    # print("\n")
    # #
    # # print(count_1)
    # # print(count_2)
    # # print(count_3)
    # # print(count_4)
    # # print(count_5)
    # # print(count_6)
    # # print(count_7)
    # #
    # # print ("Price_sell: ", get_price_sell(data,get_trans_type(data), price))
    # #
    # #
    # #
    #
    #
# data =  {
#     "id": 118318,
#     "content": "Bán nhà 2 mặt tiền Nguyễn Trãi, P Bến Thành, quận 1, gần chợ Bến Thành 300m.\n\n\n\nDT: 8.5 x 20m . Vuông vức mặt tiền Nguyễn Trãi và mặt hẻm 8m không bi lộ giới không lỗi phong thủy, Siêu vị trí có 1 không 2.\r\n\r\r\n\r Nhà 1 trệt 8 lầu thang máy đẹp lung linh.\r\n\r\r\n\rHiện đang cho thuê kinh doanh làm khách sạn và văn phòng với giá 450 triệu/tháng.\r\n\rGiá bán: 125 tỷ thương lượng\r\n\r\r\n\rGọi ngay:0933.221.393 Hương Hồ (Zalo ,Viber 24/7).",
#     "realestate_type": 2,
#     "floor": 9.0,
#     "attributes": [
#       {
#         "content": "Bán",
#         "type": "transaction_type"
#       },
#       {
#         "content": "nhà",
#         "type": "realestate_type"
#       },
#       {
#         "content": "2",
#         "type": "normal"
#       },
#       {
#         "content": "mặt tiền",
#         "type": "position"
#       },
#       {
#         "content": "Nguyễn Trãi",
#         "type": "addr_street"
#       },
#       {
#         "content": ", P",
#         "type": "normal"
#       },
#       {
#         "content": "Bến Thành",
#         "type": "addr_ward"
#       },
#       {
#         "content": ",",
#         "type": "normal"
#       },
#       {
#         "content": "quận 1",
#         "type": "addr_district"
#       },
#       {
#         "content": ", gần",
#         "type": "normal"
#       },
#       {
#         "content": "chợ",
#         "type": "surrounding"
#       },
#       {
#         "content": "Bến Thành",
#         "type": "surrounding_name"
#       },
#       {
#         "content": "300 m . \n DT :",
#         "type": "normal"
#       },
#       {
#         "content": "8 . 5 x 20 m",
#         "type": "area"
#       },
#       {
#         "content": ". Vuông vức",
#         "type": "normal"
#       },
#       {
#         "content": "mặt tiền",
#         "type": "position"
#       },
#       {
#         "content": "Nguyễn Trãi",
#         "type": "addr_street"
#       },
#       {
#         "content": "và mặt",
#         "type": "normal"
#       },
#       {
#         "content": "hẻm",
#         "type": "position"
#       },
#       {
#         "content": "8 m không bi lộ giới không lỗi phong thủy , Siêu vị trí có 1 không 2 . \n",
#         "type": "normal"
#       },
#       {
#         "content": "Nhà",
#         "type": "realestate_type"
#       },
#       {
#         "content": "1 trệt",
#         "type": "interior_floor"
#       },
#       {
#         "content": "8 lầu",
#         "type": "interior_floor"
#       },
#       {
#         "content": "thang máy đẹp lung linh . \n Hiện đang",
#         "type": "normal"
#       },
#       {
#         "content": "cho thuê",
#         "type": "potential"
#       },
#       {
#         "content": "kinh doanh",
#         "type": "potential"
#       },
#       {
#         "content": "làm khách sạn",
#         "type": "potential"
#       },
#       {
#         "content": "và",
#         "type": "normal"
#       },
#       {
#         "content": "văn phòng",
#         "type": "potential"
#       },
#       {
#         "content": "với giá 450 triệu / tháng . \n Giá bán :",
#         "type": "normal"
#       },
#       {
#         "content": "125 tỷ",
#         "type": "price"
#       },
#       {
#         "content": "thương lượng \n Gọi ngay : 0933 . 221 . 393 Hương Hồ ( Zalo , Viber 24 / 7 ) .",
#         "type": "normal"
#       }
#     ]
# }
# print(phuong(data))