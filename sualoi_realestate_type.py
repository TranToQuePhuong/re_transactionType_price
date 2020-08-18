import re
from api.make_up_alternative import api_urls
from api.make_up_alternative.utils import remove_accents


def sualoi_realestate_type(post: dict) -> (int, bool):
    """ Hàm sẽ tìm loại bất động san của bài đăng

        Args:
            post_info (dict): dict chứa thông tin cần thiết để tìm loại bất động sản

        Returns:
             int : loại bất động sản của bài đăng
             bool: can con nguoi kiem tra neu True, default la False (khong can kiem tra)
    """
    realestate_type = post['realestate_type']
    content = remove_accents(post['content'])
    re_check = False

    # Kiem tra loai BDS la DAT
    if realestate_type == 1:

        # Dat tho cu
        if re.search(r"dat\s+tho\s+cu|dat\s+tc|dat\s+o\s+tai\s+(do\s+thi|nong\s+thon)|mat\s+tien|dat\s+kiet", content) is not None:
            realestate_type = 1

        # Dat nen/ Dat du an
        elif re.search(r'"dat\s+nen\s|dat\s+nen\s+tho\s+cu|dat\s+du\s+an|dat\s+xay\s+dung|khu\s+du\s+an|nen\s+dat|phan\s+lo|dat_nen"', content) is not None:
            realestate_type = 10

        # Dat trong cay/ Dat nong nghiep
        elif re.search(r'(\s?dat\s+trong\s+cay|((\s?dat\s+)?(nong\s+nghiep|lam\s+nghiep)))\s?', content) is not None:
            realestate_type = 9

        else:
            re_check = True

    # Kiem tra loai BDS la nha tro/ day tro/ phong tro
    elif realestate_type == 7:

        # Day nha tro/ Day phong tro
        if re.search(r'((ban\s)?day\s(nha\s|phong\s)?tro)|(ban\s(gap\s)?nha\stro\s)|(nha\s+tro\s+(can\s)?ban)', content) is not None:
            realestate_type = 7

        # Phong tro
        elif re.search(r'(phong\stro)|(phong\s(trong\s|(trong\scan\sho\s))?cho\sthue)|(cho\sthue\sphong\s)|\
                           (o\sghep)|((cho\sthue\s)?(can\sho|chdv|chmn|ccmn|(chung\scu\smini)|(nha\stro)))', content) is not None:
            realestate_type = 8

        else:
            re_check = True

    elif realestate_type == 3:
        if re.search(r'(can\s+ho\s+dich\s+vu\s+(cao\s+cap)?)|(chdv\s)', content) is not None:
            realestate_type = 2

        elif re.search(r'((chung\scu\s|can\sho\s)+(cao\scap)?|penhouse|pen-house|pen\shouse|ph)', content) is not None:
            realestate_type = 3

        else:
            re_check = True

    # Cac loai BDS khac
    else:
        pass

    return dict(value=realestate_type, re_check=re_check)
