#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 14:17:41 2020

@author: naivegiraffe
"""

vi = "ÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚÝàáâãèéêìíòóôõùúýĂăĐđĨĩŨũƠơƯưẠạẢảẤấẦầẨẩẪẫẬậẮắẰằẲẳẴẵẶặẸẹẺẻẼẽẾếỀềỂểỄễỆệỈỉỊịỌọỎỏỐốỒồỔổỖỗỘộỚớỜờỞởỠỡỢợỤụỦủỨứỪừỬửỮữỰựỲỳỴỵỶỷỸỹ"
en = "AAAAEEEIIOOOOUUYaaaaeeeiioooouuyAaDdIiUuOoUuAaAaAaAaAaAaAaAaAaAaAaAaEeEeEeEeEeEeEeEeIiIiOoOoOoOoOoOoOoOoOoOoOoOoUuUuUuUuUuUuUuYyYyYyYy"
""" File này sẽ kết hợp NLP API và các hàm tự viết để cố gắng phân giải
các thuộc tính của bất động sản từ 2 nguồn là crawler gửi lên và NLP phân giải
"""

from re import findall, search, sub, I

from app.modules.make_up.api.api_NLP_communicate import get_from_api
from app.modules.make_up.utils import remove_accents

# mặc dù cũng thuộc nhóm chức năng chuẩn hóa,
# nhưng hàm 'normalize_price' lại được gọi ở đây vì như thế sẽ tiện hơn
from app.modules.make_up.miscellaneous.normalize.utils import normalize_price



from data_processing.main import filter_post, filter_post_option
from data_processing.check_rent import check_rent
from data_processing.check_sell import check_sell
from data_processing.common import params

FILLING_ATTRS = [
    "address_number",
    "address_street",
    "address_district",
    "address_ward",
    "address_city",
    "position_street",
    "surrounding",
    "surrounding_name",
    "surrounding_characteristics",
    "transaction_type",
    "realestate_type",
    "potential",
    "area_origin",
    "area_cal",
    "price",
    "price_m2",
    "price_rent",
    "price_sell",
    "floor",
    "interior_room",
    "orientation",
    "project",
    "legal",
    "contact_phone"
]

#############################################################################
## HÀM TRÍCH XUẤT SỐ ĐIỆN THOẠI
#############################################################################
re0 = r"(0\d{9})"
re1 = r"(\+84(\d|\.|\s){5,13}\d)"
re2 = r"\D(0(\d|\.|\s){5,13}\d)"
re3 = r"0{5}"

import json
import codecs

list_ID0 = []
list_ID1 = []
list_ID2 = []
list_ID3 = []
list_ID4 = []
list_ID5 = []
with open('data.json', 'rb') as json_data:
    data_set = json.loads(json_data.read())
    print(len(data_set), "datas loaded succesfully")
    listSpam = ['24 / 24','24 / 7','1 / 500']
    listNear = ['cách','cạnh','gần','kề'] # danh sách những tính từ đồng nghĩa với gần
    listMT = ['mặt tiền','mặt đường','mặt phố']
    listPlural = ['2','3','hai','ba']
    listSingularSlash = ['1 sẹc','một sẹc','1 /','một /']
    listPluralSlash = ['2 sẹc', 'hai sẹc', '2 /', 'hai /','3 sẹc', 'ba sẹc', '3 /', 'ba /']
    listH = ['hẻm','hẽm'] # em nghĩ có thêm các từ như 'ngõ','kiệt' nhưng không chắc lắm

def get_attribute(post_info):
    '''Dùng NLP API và Geo Google API để trích xuất các thuộc tính từ nội dung bài post
    :Args:
    - post_info: instance thuôc class PostInfo

    :Rets:
    - None - hàm này sẽ modify trực tiếp vào `post_info` nên không return gì cả
    '''

    ##########################################################################################################
    # Tiền xử lí một chút với nội dung của bài post
    ##########################################################################################################

    # trường hợp một số page_source như landber.com thì trường địa chỉ đôi khi ghi không đúng
    # nên cách an toàn là thêm nội dung trường địa chỉ vào nội dung bài post để NLP detect một thể
    # tuy nhiên, để tránh phương hại đến nội dung gốc của bài post, sẽ xử lí trên một biến riêng, và biến đó là 'new_content'
    new_content = '' + post_info.get_info("content")
    if post_info.get_info("address_street"):
        new_content = new_content + " Địa chỉ: " + post_info.get_info("address_street")

    if post_info.get_info("title"):
        new_content = post_info.get_info("title") + " - " + new_content

    # thay thế kí tự '₫' bởi chuỗi " giá "
    new_content = new_content.replace('₫', " giá ")

    # thêm loại bất động sản (realestate_type) và loại giao dịch (transaction_type) nếu có vào nội dung
    tmp = ""
    if post_info.get_info('transaction_type'):
        tmp = tmp + post_info.get_info('transaction_type')
    if post_info.get_info('realestate_type'):
        tmp = tmp + ' ' + post_info.get_info('realestate_type')
    if tmp != "":
        new_content = tmp + ' ' + new_content



    ##########################################################################################################
    # phân tích các thuộc tính của bài post bằng cách dùng NLP API để phân giải thuộc tính
    # và Geo API để phân giải kinh độ, vĩ độ
    ##########################################################################################################
    attributes = extract_attributes(new_content, post_info)




    ##########################################################################################################
    ## Xử lí một vài trường hợp đặc biệt trước
    ##########################################################################################################
    attributes['transaction_type'] = get_trans_type(post_info)
    post_info.set_info('transaction_type', attributes['transaction_type'])

    price, _, price_m2, _, area_tmp = get_price(post_info, attributes)
    area, area_origin = get_area(post_info, attributes)
    floor = get_floor(post_info, attributes)
    project, street, ward, district, city = get_street(post_info)

    # cập nhật area hoặc price_m2
    if area == 0 and area_tmp != 0 and area_tmp:
        area = float(area_tmp)

    # Nov 9, 2019: bên anh Phùng bảo không cần nhân
    # # nhân diện tích với số tầng để tìm ra diện tích thật của bất động sản
    # area = area * floor

    if (price_m2 is None or price_m2 == 0) and price != 0 and area != 0:
        price_m2 = price / area if price else 0


    ##########################################################################################################
    # sau khi đã phân tích nội dung bài post bằng NLP API và các thuộc tính đã được lưu trong 'attributes',
    # gán chúng vào instace class PostInfo
    ##########################################################################################################
    for attribute in FILLING_ATTRS:
        if attribute == "price":
            post_info.set_info(attribute, price)
        elif attribute == "price_m2":
            post_info.set_info(attribute, price_m2)
        elif attribute == "area_cal":
            post_info.set_info(attribute, area)
        elif attribute == "floor":
            post_info.set_info(attribute, floor)
        elif attribute == "area_origin":
            post_info.set_info(attribute, area_origin if area_origin is not None else [0, 0])
        elif attribute == "address_street" and street is not None:
            post_info.set_info(attribute, street)
        elif attribute == "contact_phone":
            post_info.set_info(attribute, getPhone(new_content))
        elif attribute == "realestate_type":
            if attributes[attribute] == "":
                post_info.set_info(attribute, None)
            else:
                post_info.set_info(attribute, attributes[attribute])

        elif post_info.get_info(attribute) is None:
            if attributes[attribute] == "":
                post_info.set_info(attribute, None)
            else:
                post_info.set_info(attribute, attributes[attribute])
    post_info.set_info('price_rent', get_price_rent(
        post_info, attributes['transaction_type'], attributes['price_str']))
    post_info.set_info('price_sell', get_price_sell(
        post_info, attributes['transaction_type'], attributes['price_str']))

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


def to_str(data):
    if type(data) is str:
        return data
    if type(data) is list:
        return ''.join(data)
    return data


def cal_price_rent(post_info, raw_price, x):
    if x == '':
        return raw_price * post_info.get_info('area')
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

def extract_attributes(new_content, post_info):
    '''Dùng NLP API để phân tích các thuộc tính từ `new_content` là một phiên bản có chỉnh sửa lại
    một vài thứ của content nguyên bản gửi từ crawler
    '''
    tmp = get_from_api(new_content)

    if post_info.get_info('area_cal'):
        tmp['area_cal'] = post_info.get_info('area_cal')

    if post_info.get_info('legal'):
        tmp['legal'] = post_info.get_info('legal')

    if post_info.get_info('orientation'):
        tmp['orientation'] = post_info.get_info('orientation')

    return tmp


def get_price(post_info, attributes):
    if post_info.get_info('price_str') is not None:
        return normalize_price(post_info.get_info('price_str'))
    else:
        price_min = 0
        price_max = 0
        price_m2 = 0
        area_tmp = 0


        for tmp in attributes['price_str']:
            price = normalize_price(tmp)
            if price_min == 0 and price[0]:
                price_min = price[0]
            if price_max == 0 and price[1]:
                if price_min > 0 and price_max > price_min:
                    price_max = price[1]
            if price_m2 == 0 and price[2]:
                price_m2 = price[2]
            if area_tmp == 0 and price[4]:
                area_tmp = price[4]

        # if reach here that means none of attribute related to price extracted by NLP API is valuable
        return price_min, price_max, price_m2, None, area_tmp



# regex for area
re_area = r"(\d+\.\d+|\d+)"
def extract_area(str_area):
    """Tính toán diện tích cũng như kích thước của chiều dài và chiều rộng của bđs nếu có

    :Args:
    - str_area - string chứa diện tích

    :Rets
    - float, None - nếu string diện tích không chứa thông tin về các chiều
    - float, [float, float] - nếu string diện tích chứa thông tin về các chiều
    """
    str_area = str_area.replace(" ", "").replace(",", ".").replace(
        "m2", "").replace("m", "").replace("ha", "0000")

    if str_area == "":
        return None, None

    if search(pattern=r"(x|\*)", string=str_area) is None:
        numbers_extraction = findall(re_area, str_area)

        if len(numbers_extraction) == 0:
            return None, None
        return max(numbers_extraction), None

    is_total_area_available = None
    if search(r"=((\d+\.*\d*)*)", str_area):
        is_total_area_available = float(findall(r"=([0-9\.]*)", str_area)[0])

    tmp = 1
    str_area = sub(r"=(.+)", "", str_area)
    dimensions = findall(pattern=re_area, string=str_area)
    for i, element in enumerate(dimensions):
        dimensions[i] = float(element)
        tmp = tmp * dimensions[i]
    dimensions.sort()

    return tmp if is_total_area_available is None else is_total_area_available, dimensions

def get_area(post_info, attributes):
    """Xử lí diện tích cũng như kích thước của chiều dài và chiều rộng của bđs nếu có

    :Args:
    - post_info - instance của class PostInfo chứa các thông tin có trước từ crawler gửi lên
    - attributes - list các thuộc tính trích xuất được từ NLP api

    :Rets
    - float, None - nếu chỉ tìm thấy được con số diện tích
    - float, [float, float] - có cả diện tích và thông tin các chiều
    """

    if post_info.get_info('area_str') is not None:
        # trường "area_str" gửi lên từ crawler đã có sẵn giá trị,
        # công việc tiếp theo chỉ là tìm trường "area_origin
        dimensions = None
        for area in attributes['area_str']:
            _, dimensions = extract_area(area)
            if dimensions is not None:
                break

        if isinstance(post_info.get_info('area_str'), str):
            return float(extract_area(post_info.get_info('area_str'))[0]), dimensions
        else:
            return float(post_info.get_info('area_cal')), dimensions
    else:
        for area in attributes['area_str']:
            t, dimensions = extract_area(area)
            if t:
                return float(t), dimensions

        # if reaches here, no any string of area extracted by NLP API found
        return 0, None



def remove_accents(input_str):
    """Đổi các ký tự từ Unicode sang dạng không dấu và in thường
    Arguments:
        input_str {str} -- string cần chuyển đổi
    Returns:
        str -- string nếu chuyển đổi thành công
        None - otherwise
    """

    if input_str is None:
        return 'none'

    s = ""
    for c in input_str:
        if c in vi:
            s += en[vi.index(c)]
        else:
            s += c
    return s.lower()


import json

with open('data.json', encoding="utf8") as json_file:
    data = json.load(json_file)

    ####
    # list các keyword cần check, ở dạng lower và không dấu vì check trên str đã remove_accents()
    ####

    # có trường hợp viết tắt như 'mtg' thì không phải 'mt' nên 'mt' sẽ được thành 'mt '

    # có trường hợp content chứa '1800m2 mat tien', nghĩa là diện tích + mặt tiền.
    # nếu chỉ xét '2 mat tien' có thể bị sai nên em cách ra thành check ' 2 mat tien'
    # tương tự với tất cả trường hợp có '2' ở đầu

    banthue=[0] * len(data)

    i = 0
    for p in data:
        # O(1)
        i = i + 1
        if "ban" in remove_accents(p['content']):
            if "thue" in remove_accents(p['content']):
                banthue[i]= 1

        # Đơn giản là xét ngược xuống, vì:
        #
        # nếu đã có 'hai mat tien' thì chắc chắn nó sẽ là position_street = 2
        # trong 'hai mat tien' cũng có 'mat tien' nhưng vì đã thuộc position_street = 2 (đúng)
        # nên nó không còn thuộc position_street = 1 (sai) nữa
        #
        # các trường hợp đặc biệt như content rao bán cùng lúc nhiều nhà, vừa có nhà position_street = 1
        # vừa có nhà position_street = 2 em đã hỏi trong file excel, ví dụ id = 120251

        # Chưa xét / tên đường, sẽ trình bày sau trong buổi meet
    for i in banthue:
        print(i)

# Xuất ra lại một file mới có thêm thuộc tính 'position_street'
with open('data_fullcontext_new.json', 'w', encoding='utf8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=2)
