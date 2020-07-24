""" File này chứa các hàm dùng để chuẩn hoá từng trường của bài đăng
"""

# -*- coding: utf-8 -*-
from re import search, findall, sub, I

from app.modules.make_up.miscellaneous import std_districts, std_cities, std_pages
import app.modules.make_up.miscellaneous.normalize.convention as convention
from app.modules.make_up.miscellaneous.normalize.Price import Price
from app.modules.make_up.utils import remove_accents


def normalize_page(str_page):
    """Chuẩn hoá lại trường 'page_source' trong PostInfo
    """
    try:
        for page_source in std_pages:
            if search(r"{}".format(page_source['page_source']), str_page):
                return page_source['id']
    except TypeError:
        pass
    return 7


re_addr1 = r"(\d*.*\d*[^\sa-z\W])"
re_addr2 = r"\d{5,8}"                   # search for the mobile number
def normalize_address(str_addr):
    if str_addr is None or str_addr == "" or search(re_addr2, str_addr):
        return None

    str_addr = remove_accents(str_addr)

    if search(re_addr1, str_addr):
        return findall(re_addr1, str_addr)[0]
    else:
        return str_addr



def normalize_street(str_street):
    """ Chuẩn hoá trường 'address_street'
    """
    if str_street is None or str_street == "":
        return None

    str_street = sub(r"ql",     "quốc lộ",        str_street)
    str_street = sub(r"dt|đt",  "đường tỉnh",     str_street)
    str_street = sub(r"tl",     "tỉnh lộ",        str_street)
    str_street = sub(r"tnhau",  "thoại ngọc hầu", str_street)
    str_street = sub(r"hl",     "hương lộ",       str_street)
    str_street = sub(r"\d{4,}", "",               str_street)

    return str_street


re_district_1 = r"Q|q\D*(\d{1,2})"
re_district_2 = r"q \. "
def normalize_district(str_district):
    """ Chuẩn hoá trường 'address_district'
    """
    if str_district is None or str_district == "":
        return 0

    # tránh trường hợp quốc lộ và tương tự
    if search(r"qu.c", str_district):
        # return str_district
        pass

    elif search(re_district_1, str_district) and search(r"\d+", str_district):
        str_district = "quan " + search(r"\d+", str_district).group()

    else:
        str_district = sub(re_district_2, "", str_district)
        str_district = sub(r'pn', "phu nhuan", str_district)
        str_district = sub(r'tb', "tan binh", str_district)
        str_district = sub(r'gv', "go vap", str_district)
        str_district = sub(r'bt', "binh thanh", str_district)
        str_district = sub(r'tp', "", str_district)
        str_district = sub(r'tx', "", str_district)
        # str_district = sub(r'huy.n', "", str_district)

    str_district = remove_accents(str_district)

    for district in std_districts:
        if str_district == district['name']:
            return district['id']
    return 0


re_ward_1 = r"p|P|f|F\D*(\d{1,2})"
re_ward_2 = r"f|p \. "
def normalize_ward(str_ward):
    """ Chuẩn hoá trường 'address_ward'
    """
    if str_ward is None or str_ward == "":
        return None

    str_ward = str_ward.lower()
    if search(re_ward_1, str_ward) and search(r"\d+", str_ward):
        return search(r"\d+", str_ward).group()

    str_ward = sub(re_ward_2, "", str_ward)
    str_ward = sub(r"hbp", "hiệp bình phước", str_ward)
    str_ward = sub(r"xã\s?", "", str_ward)
    str_ward = sub(r"btd", "bình trưng đông", str_ward)

    # # sửa trường hợp tên phường chỉ có số, mà không có chữ gì cả (ví dụ "5") thì sẽ
    # # tự động thêm chữ "phường" vào trước số đó
    # if search(r"\d+", str_ward) and search(r"\D", str_ward) is None:
    #     str_ward = str_ward

    return sub(r"phường|p\.", '', str_ward)



def normalize_city(post_info):
    '''Chuẩn hóa thành phố/tỉnh

    :Args:
    - post_info - instance của class PostInfo

    :Rets:
    - số đại diện tên thành phố
    '''

    ## thử xem tên quận đã tìm được chưa, nếu tìm được rồi thì từ đó mà truy ra khỏi cần làm bước sau mất công
    if post_info.get_info('address_district') and post_info.get_info('address_district') > 0:
        return std_districts[post_info.get_info('address_district') - 1]['city_id']

    str_city = post_info.get_info('address_city')
    if str_city is None or str_city == "":
        return 0

    str_city = sub(r"tp [\. ]?", "", str_city).lower()
    tmp = str_city
    str_city = remove_accents(str_city)

    isFound = False
    for tag, value in convention.CITIES.items():
        for alias in value['alias']:
            if search(alias, str_city):
                tmp = tag
                isFound = True
                break

        if isFound:
            break

     # đổi tên quận thành id tương ứng
    for city in std_cities:
        if search(r"{}".format(city['name']), tmp):
            return city['id']
    return 0



def positionElement_classify(str_position):
    """Phân loại string 'str_position' thành một trong các loại sau
    - mặt tiền
    - 2 mặt tiền
    - hẻm
    - hẻm 2 mặt tiền

    :Args:
    - str_position - string có thể chứa thông tin về position

    :Rets:
    - một trong các giá trị sau:
        + mặt tiền
        + 2 mặt tiền
        + hẻm
        + hẻm 2 mặt tiền
        + None
    """

    str_position = remove_accents(str_position)
    str_position = str_position.replace("hai", "2")

    if search(r"cach mat tien .{0,30}\d+\s*m", str_position):
        return "hẻm"
    if search(r"mat tien hem", str_position, I):
        return "hẻm"
    if search(r"hem|ngo|hxh", str_position, I):
        if search(r"2 mat tien", str_position, I):
            return "2 mặt tiền hẻm"
        return "hẻm"
    if search(r"2 mat tien", str_position):
        return "2 mặt tiền"
    if search(r"[2-9]\s*mat tien", str_position, I):
        return "mặt tiền"
    if search(r"mat (tien|pho|duong)", str_position, I):
        return "mặt tiền"



def position_classify(position):
    """Xác định xem là trường hợp nào trong 6 trường hợp được liệt kê ở document

    :Args:
    - position - list các cụm 'position_street' được phân giải từ NLP API

    :Rets:
    - các số nguyên dương từ 1 đến 6 đại diện cho các giá trị đã ghi trong document
    """
    # Bước đầu tiên: kiểm tra các yếu tố 'hẻm', 'mặt tiền' xuất hiện trong
    # tất cả các từ được phân giải từ NLP API
    is_2_fronts, is_front, is_alley = False, False, False
    for word in position:
        tmp = positionElement_classify(word)
        # Nếu là '2 mặt tiền hẻm thì trả về luôn'
        if tmp == "2 mặt tiền hẻm":
            return 5
        if tmp == "hẻm":
            is_alley = True
        if tmp == "2 mặt tiền":
            is_2_fronts = True
        if tmp == "mặt tiền":
            is_front = True

    # Bước tiếp theo: kết hợp các kết quả tìm được cho ra kết quả cuối cùng
    if is_alley:
        if is_2_fronts:
            return 5
        return 3
    if is_2_fronts:
        return 2
    if is_front:
        return 1

    return 6



def normalize_position_street(post_info):
    """Chuẩn hóa trường `position_street` dựa vào trường `address_number` 
    và các trường `postion_street` được phân giải bở NLP API

    :Args:
    - str_position
    - str_addressnumber

    :Rets:
    - int đại diện cho thông tin
    """
    position = post_info.get_info('position_street')
    if position is None or len(position) == 0:
        return 6
    address = post_info.get_info('address_number')

    ###############
    ## Trường hợp 1: Có địa chỉ
    if address is not None:
        ## Trường hợp 1.1: Địa chỉ có 2 sẹc
        if search(r"\/\d+\/", address):
            return 4
        ## Trường hợp 1.2: Địa chỉ có 1 sẹc
        if search(r"\/", address):
            return position_classify(position)
        ## Trường hợp 1.3: Địa chỉ không có sẹc
        if position_classify(position) == 6:
            return 1

    ## Trường hợp 2: Không có địa chỉ
    return position_classify(position)



def normalize_transaction_type(transaction_type):
    '''Return the standardized transaction type
    In this version, it returns the alias names of the transaction
    '''
    # if transaction_type == []:
    #     return None
    # if type(transaction_type) is str:
    #     transaction_type = [transaction_type]

    # for str_transaction_type, i in zip(transaction_type, range(len(transaction_type))):
    #     is_found_flag = False
    #     str_transaction_type = remove_accents(str_transaction_type)

    #     for tag, value in convention.TRANSACTION_TYPE.items():
    #         for alias in value['aliases']:
    #             if search(alias, str_transaction_type):
    #                 transaction_type[i] = tag
    #                 is_found_flag =  True

    #         if is_found_flag == False:
    #             transaction_type[i] = "khác"

    # # eliminate 2 same transaction_types
    # result = []
    # for transaction_type in transaction_type:
    #     if transaction_type not in result:
    #         result.append(transaction_type)

    # return ','.join(result)
    return transaction_type



def normalize_realestate_type(str_realestate_type):
    '''Chuẩn hóa các loại bất động sản thành ID tương ứng
    '''
    if str_realestate_type is None or str_realestate_type == "":
        return 6

    str_realestate_type = remove_accents(str_realestate_type)

    for tag, value in convention.REALESTATE_TYPE.items():
        for alias in value['aliases']:
            if search(alias, str_realestate_type):
                return tag

    return 6



def normalize_legal(str_legal):
    """ Chuẩn hoá trường 'legal'
    """
    if str_legal is None or str_legal == "":
        return 2

    str_legal = remove_accents(str_legal)

    if search(r"hong|sh", str_legal):
        return 3
    elif search(r"do|sd", str_legal):
        return 3
    else:
        return 1



def normalize_price(str_price):
    '''Phân giải giá trị price_min, price_max
       Có thể phá hiện được trường 'price_m2' hoặc 'area'

    :Args:
    str_price - string of price extracted by NLP API

    :Returns:
    a 5-element tuple of: (price_min, price_max, price_min_m2, price_max_m2, area), None value may be one of 5 elements in tuple
    '''

    # remove phone number if exists
    str_price = sub(r"(0\d{7,10})", "", str_price)

    # basic processing
    str_price = remove_accents(str_price)

    str_price = sub('Mười', '10', str_price)
    str_price = sub('mười', '10', str_price)
    str_price = sub('tỏi', 'ty', str_price)

    str_price = remove_accents(str_price)

    for number, spelling in convention.NUMBER.items():
        str_price = sub(r"\b{}\b".format(spelling), number, str_price)

    # subtitute unconventional spelling name to conventional one
    for conventional, value in convention.NUMBER_CARDINALITY.items():
        for alias in value['aliases']:

            # this command for the case: 33t / m2
            if (alias == 't'or alias == 'tt') and search(r"m|m2", str_price):
                str_price = sub(r"\b({})\b".format(
                    alias), "trieu", str_price)
            else:
                str_price = sub(r"\b({})\b".format(
                    alias), conventional, str_price)

    # remove space
    str_price = sub(r'\s', '', str_price)

    # recognize m2, usd
    # we have to check the following condition because in some case the price is "570 tr / 1100 m 2"
    # this price is for the whole 1100-meter-square land, not per meter square
    is_price_m2 = False
    is_usd = False
    area = search(r"\d{2,}met|\d{2,}m2|\d{2,}m", str_price)
    if area is None:
        if search(r"1metvuong|metvuong|met|m2|m|\d+lo|\d+can", str_price):
            str_price = sub(
                r"1metvuong|metvuong|met|m2|m|\d+lo|\d+can", "", str_price)
            is_price_m2 = True
    else:
        # the price has the form ""800 tr / 191 m 2"
        area = float(sub(r"metvuong|met|m2|m", "", area.group()))
        str_price = sub(r"\d{2,}met|\d{2,}m2|\d{2,}m", "", str_price)

    for alias in convention.FOREIGN_CURRENCY['usd']:
        if search(alias, str_price):
            is_usd = True
            break

    # split str_price into 2 parts
    for divider in convention.DIVIDERS:
        str_price = sub(r"{}".format(divider), convention.MAIN_DIVIDER, str_price)

    str_price_parts = []
    for part in str_price.split(convention.MAIN_DIVIDER):
        if part != '':
            str_price_parts.append(Price(part, is_price_m2, is_usd))

    # each part recognizes itself
    for part in str_price_parts:
        part.recognize()

    # if one of part are price_m2 or dollar or has biggest cardinality available, set it to the rest
    if len(str_price_parts) > 1:
        # there are 2 parts of price

        # for cardinality, it is a little bit different
        #  if 2 parts have their own biggest cardinality, ignore this case
        #  if part 2 has while part 1 doesn't, there are 2 cases:
        #    - 2 parts share the same cardinality
        #    - part 1 has lower cardinality

        # below only solves first case given, for the second case, it will be solve after calculating value for each part
        if str_price_parts[0].get_biggest_cardinality() is None:
            str_price_parts[0].set_biggest_cardinality(
                str_price_parts[1].get_biggest_cardinality())

    # calculate price and print out
    for i in range(len(str_price_parts)):
        str_price_parts[i].calculate_price()
        # str_price_parts[i].debug()

    # return results
    if len(str_price_parts) == 0:
        return None, None, None, None, None

    price_min = str_price_parts[0].get_price()
    price_min_m2 = str_price_parts[0].get_price_m2()
    if len(str_price_parts) > 1:
        price_max = str_price_parts[1].get_price()
        price_max_m2 = str_price_parts[1].get_price_m2()
    else:
        price_max = price_max_m2 = None

    # solve the second case of the problem of missing cardinality of first part
    if price_max and price_min:
        while price_min > price_max:
            price_min = price_min / 1000

    return price_min, price_max, price_min_m2, price_max_m2, area



def normalize_orientation(str_orientation):
    """ Chuẩn hoá trường 'orientation'
    """

    if str_orientation is None or str_orientation == "":
        return None
    rmvAccent_str = remove_accents(str_orientation)
    if search(r"dn|dong nam", rmvAccent_str):
        return "đông - nam"
    if search(r"db|dong bac", rmvAccent_str):
        return "đông - bắc"
    if search(r"tn|tay nam", rmvAccent_str):
        return "tây - nam"
    if search(r"tb|tay bac", rmvAccent_str):
        return "tây - bắc"
    if search(r"dong", rmvAccent_str):
        return "đông"
    if search(r"tay", rmvAccent_str):
        return "tây"
    if search(r"bac", rmvAccent_str):
        return "bắc"
    if search(r"nam", rmvAccent_str):
        return "nam"

    return None



def normalize_surrounding_name(surrounding_long_name):
    """ Chuẩn hoá trường 'surrounding_name'
    """

    if len(surrounding_long_name) == 0:
        return surrounding_long_name

    full_name_list = []
    for surrounding_name in surrounding_long_name:
        if surrounding_name == "":
            continue

        # thay thế một vài từ viết tắt bằng từ hợp lí
        for short_name, full_name in convention.SURROUNDING_NAME.items():
            surrounding_name = surrounding_name.replace(short_name, full_name)

        full_name_list.append(surrounding_name)

    if full_name_list is None:
        return []
    else:
        return_list = []

        for name in full_name_list:
            # chuẩn hoá `name` chút xíu
            # với trường hợp 'uỷ ban nhân dân phường, quận, thì nếu có chữ quận, phường ở dạng viết tắt thì ghi tường minh ra chữ 'quận', 'phường'
            name = name.replace('.', '')
            name = name.replace(',', '')

            if search(r"ph..ng|qu.n", name) is None:
                tmp = findall(r".. ban nh.n d.n p(.*)", name)
                if len(tmp) > 0:
                    name = "uỷ ban nhân dân phường" + tmp[0]
                tmp = findall(r".. ban nh.n d.n q(.*)", name)
                if len(tmp) > 0:
                    name = "uỷ ban nhân dân quận" + tmp[0]

            return_list.append(name)

        return return_list



def normalize_potential(potential):
    """Chuẩn hóa trường 'potential'
    """
    if potential is None or len(potential) == 0:
        # mặc định luôn để: tiềm năng là kinh doanh
        return [2]

    for i, p in enumerate(potential):
        tmp = remove_accents(p)
        if search(r"thue", tmp):
            potential[i] = 1
        elif search(r"caphe|coffe|ca phe", tmp):
            potential[i] = 3
        elif search(r"ks|khach san", tmp):
            potential[i] = 4
        else:
            potential[i] = 2

    return list(dict.fromkeys(potential))
