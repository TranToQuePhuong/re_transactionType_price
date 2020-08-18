import re

import params


def get_data(data):
    # data[0][0] is message
    if re.search(params.transfer_ptrn, data[0], re.I):
        if max(data[1]) >0 :
            if max(data[1]) <= 500000000 :
                return True
        if max(data[2]) >0:
            if max(data[2]) <=500000000:
                return True

    #
    return False
