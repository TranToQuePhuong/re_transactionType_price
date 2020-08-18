import json
import re
from xacdinh import xacdinh


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

numbers = r'(\d+)\s*(,\s*\d+)*(\.\s*\d+)*'
cur_u_man_r = r'\s*(dong|trieu\s*\d*|trieu\s*\d*|tr\s*\d*|t[i|y]\s*\d*|USD|\$\s*(USD)?)\s*(\/\s*1?\s*thang)?(\/\s*1?\s*nam)?(\/\s*1?\s*m\s?2)?'
def get_price_keyword(data):
  result = []
  content_tmp = remove_accents(data['content']).lower()
  content = ''
  for i in range(len(content_tmp)):
    if content_tmp[i] == '\n' or content_tmp[i] == '\r':
      continue
    content += content_tmp[i]
  result.append(data)
  cur_list = re.findall(numbers + cur_u_man_r, content)
  lst = []
  for cur in cur_list:
    str = ''
    for word in cur:
      if word == '' or cur.index(word) == 0 or word[0] == '.' or word[0] == ',':
        str += word
      else:
        str += ' ' + word
    lst.append(str+'+Bán')
  result.append(lst)  
  return result


def getFullPrice(listPhuong):
    lstPriceSell = []
    lstPriceRent = []
    # lstPriceUnknown = []

    for p in listPhuong[1]:
        priceAndType = p.split('+')
        priceAndType.insert(0, listPhuong[0])

        resultPrice = get_price(priceAndType)

        # print('result price', resultPrice)
        if resultPrice[1] == 0:
            lstPriceSell.append(resultPrice[0])
        elif resultPrice[1] == 1:
            lstPriceRent.append(resultPrice[0])
        elif resultPrice[1] == 2:
            lstPriceSell.append(0)
            lstPriceRent.append(0)
        
    print('Price Sell', lstPriceSell)
    print('Price Rent', lstPriceRent)
    print('\n')
    # print(lstPriceUnknown)



def get_price(priceAndType):
    ty=['ty','ti']
    trieu=['trieu','tr']
    nam=['nam']

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
            check_t=0
            for tr in trieu:
                if tr in priceAndType[1] or (tr + 'TL') in priceAndType[1]:
                    pivot = priceAndType[1].index(tr)
                    k = 1000000
                    if priceAndType[1][pivot - 1].isdigit():
                        gia.append(k * float(priceAndType[1][pivot - 1]))
                check_t=1

            if check_t==1:
                if 'm' in priceAndType[1]:
                        tmp = str(priceAndType[0]['id']) + 'can xac dinh lai'
                        if xacdinh(priceAndType[0]) > 0 and xacdinh(priceAndType[0]) != tmp:
                            print("Area: ",xacdinh(priceAndType[0]))
                            if len(gia) >0:
                                gia[0]=gia[0] * xacdinh(priceAndType[0])
    for n in nam:
        if n in priceAndType[1]:
            if len(gia) > 0:
                gia[0] = gia[0] /12

    # print(priceAndType[2])
    if priceAndType[2] == 'Bán':
        gia.append(0)
    elif priceAndType[2] == 'Thuê':
        gia.append(1)
    elif priceAndType[2] == 'None':
        gia.append(2)

    # print("giá", gia)
    return gia

    

#
# with open('data.json', encoding="utf-8") as json_file:
#     dataset = json.load(json_file)
#
#     for data in dataset:
#         passList = [118250]
#         if data['id'] in passList:
#             continue

        # lstTemp = []
        # att = data['attributes']
        # for i in att:
        #     if i['type'] == 'price':
        #         lstTemp.append(i['content'] + '+' + 'Bán')

        # print(lstTemp)

        # getFullPrice([data, lstTemp])

    
        # listHung = get_price_keyword(data)
        # print(listHung[1])
        # getFullPrice(listHung)


    # getFullPrice([dataset[0], ['14,5 tr+Bán']])


        