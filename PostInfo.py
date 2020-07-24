
class PostInfo:
    def __init__(self):
        self._info = {
            # nhóm các trường phía trên là các trường có thể gửi lên từ crawler, trong khi các trường phía dưới là trích xuất được
            "content"                       : None,
            "title"                         : None,
            "page_source"                   : None,
            "price_str"                     : None,
            "area_str"                      : None,
            "address_number"                : None,
            "address_street"                : None,
            "address_district"              : None,
            "address_ward"                  : None,
            "address_city"                  : None,
            "floor"                         : None,
            "interior_room"                 : None,
            'long'                          : None,
            'lat'                           : None,
            "legal"                         : None,
            "orientation"                   : None,
            "transaction_type"              : None,
            "realestate_type"               : None,
            "project"                       : None,
            "contact_phone"                 : None,
            "created_by"                    : None,
            "number_duplicated_post"        : None,
            "hash_post_key"                 : None,

            "position_street"               : None,
            "surrounding"                   : None,
            "surrounding_name"              : None,
            "surrounding_characteristics"   : None,
            "potential"                     : None,
            "area_origin"                   : None,
            "area_cal"                      : None,
            "price"                         : None,
            "price_m2"                      : None,
            "price_rent"                    : None,
            "price_sell"                    : None,
        }

    def set_info_all(self, info):
        '''Gán các attribute của parameter `info` cho `self._info`
        '''
        for key, value in info.items():
            self._info[key] = value

        # nếu trường `price_str` hoặc `area_str` gửi lên là chuỗi rỗng ("") thì cho nó thành None
        self._info['price_str'] = None if self._info['price_str'] == "" else self._info['price_str']
        self._info['area_str']  = None if self._info['area_str']  == "" else self._info['area_str']

    def get_info(self, attribute):
        return self._info[attribute]

    def set_info(self, attribute, value):
        self._info[attribute] = value

    def set_common_value(self):
        for key, value in self._info.items():
            if value == "":
                self._info[key] = None

    def get_info_all(self):
        return self._info

    def get_info_for_pushing(self):
        '''Trả về các trường để gửi trả cho crawler

        :Return:
        - dict: nếu dữ liệu của post đủ informative để gửi lên DB
        - None: nếu dữ liệu không đủ informative (too few attributes have value) hoặc giá trị hash là None: có nghĩa là có post tương tự trên DB rồi
        '''

        # xoá những trường thừa
        for attr in ["price_str", "area_str", "price"]:
            del self._info[attr]

        # chuẩn hóa lại một vài giá trị cho phù hợp
        self._info['area_cal'] = 0 if self._info['area_cal'] is None or self._info['area_cal'] == "" else self._info['area_cal']
        self._info['price_m2'] = 0 if self._info['area_cal'] is None else self._info['price_m2']

        self._info['surrounding']                 = ', '.join(self._info["surrounding"])                 if len(self._info["surrounding"])                 > 0 else None
        self._info['surrounding_name']            = ', '.join(self._info["surrounding_name"])            if len(self._info["surrounding_name"])            > 0 else None
        self._info['surrounding_characteristics'] = ', '.join(self._info["surrounding_characteristics"]) if len(self._info["surrounding_characteristics"]) > 0 else None

        self._info['price_rent'] = round(self._info['price_rent']) if isinstance(self._info['price_rent'], float) else None
        self._info['price_sell'] = round(self._info['price_sell']) if isinstance(self._info['price_sell'], float) else None


        return self._info

    def get_n_attr_None(self):
        '''Trả về số lượng các attribute man giá trị None
        '''
        n = 0
        for _, value in self._info.items():
            if value is None:
                n += 1
        return n
