import re
import params


def get_data(data):
    # data [0][0] is message
    with_pr_1 = re.search(params.s_renting_with_pr_ptrn_1, data[0], re.I)
    with_pr_2 = re.search(params.s_renting_with_pr_ptrn_2, data[0], re.I)
    with_pr_3 = re.search(params.s_renting_with_pr_ptrn_3, data[0], re.I)
    with_pr_4 = re.search(params.s_and_r_ptrn, data[0][0], re.I)
    if re.search(params.contract, data[0], re.I):
        if not with_pr_1 and not with_pr_2 and not with_pr_3 and not with_pr_4:
            if max(data[1])>0 and max(data[2])==0:
                if max(data[1]) >= 100000000 and max(data[1]) <= 10000000000000:
                    return True
                # else:
                #     return False
    return False
