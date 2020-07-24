import re

import params


def get_data(data):
    if data[0][0] is None:
        return False
    text = data[0][0].replace('\n', '').replace('\r', '')
    if re.search(params.s_and_r_ptrn, text, re.I):
        return True
