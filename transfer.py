import re

import params


def get_data(data):
    # data[0][0] is message
    if re.search(params.transfer_ptrn, data[0][0], re.I):
        return True
    return False
