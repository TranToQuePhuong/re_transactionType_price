import re

def xacdinh(dict_input: dict) -> float:
    """Phân biệt cái gì đó ahihi, mọi người sửa lại dòng này cho đúng nhé.
    Arguments:
        inp_str {dict} -- dict chứa 3 thông tin sau:
            id              : id của bài đăng
            content         : content của bài đăng
            realestate_type : loại bất động sản
            floor           : số tầng
    Returns:
        float - gía trị của biến area_cal
    Như trong doc thì có 3 loại diện tích:"""
    area_cal = 0
    datas = dict_input["attributes"]
    a = []
    offical = None
    floor=0
    price=[]
    area_array=[]
    for i in range(0, len(datas)):
        con_tent = datas[i]["content"]
        kind = datas[i]["type"]
        if kind == "interior_floor" :
            num=re.findall("\d+",con_tent)
            if len(num) !=0 :
                maxx=int(num[0])
                for j in num :
                    maxx=max(maxx,int(j))
                floor += maxx
        if kind== "price" :
            if re.search("\d+[.]?\d*",con_tent) is not None:
                price.append(float(re.search("\d+[.]?\d*",con_tent).group()))
        if kind == "area":
            con_tent = con_tent.replace(" ", "")
            cur = ""
            if re.search(r"\d+[.]?\d*(m|m2)?[xX*]\d+[.]?\d*(m|m2)?=\d+[.]?\d*(m|m2)?", con_tent) is not None :
                cur = re.search(r"=\d+[.]?\d*(m|m2)?", con_tent).group()
            elif re.search(r"\d+[.]?\d*(m|m2)?[xX*]\d+[.]?\d*(m|m2)?", con_tent) is not None:
                cur = re.search(r"\d+[.]?\d*(m|m2)?[xX*]\d+[.]?\d*(m|m2)?", con_tent).group()
            elif re.search(r"(ngang)?\d+[.]?\d*(m|m2)?[xX*]?(dai)?\d+[.]?\d*(m|m2)?", con_tent) is not None:
                cur = re.search(r"(ngang)?\d+[.]?\d*(m|m2)?[xX*]?(dai)?\d+[.]?\d*(m|m2)?", con_tent).group()
            elif re.search(r"\d+[.]?\d*(m|m2)", con_tent) is not None:
                cur = re.search(r"\d+[.]?\d*(m|m2)", con_tent).group()
            if cur == "" :
                ans = re.search(r"\d+[.]?\d*", con_tent)
                if ans is not None:
                    ans = float(ans.group())
                    if "ha" in con_tent : ans*=10000
                    a.append(ans)
            else:
                cur = cur.replace("m2", "")
                res = re.findall(r"\d+[.]?\d*", cur)
                area=0

                if len(res) == 1: area = float(res[0])
                if len(res) == 2: area = float(res[0]) * float(res[1])
                area_array.append(area)
                if offical is not None:
                    return area
                area_cal=max(area,area_cal)
        else : offical= None
        if kind == "normal":
            offical = re.search("(DT cong nhan)|(DTCN)|(cong nhan)|CN", con_tent, re.IGNORECASE)
            if offical is not None:
                offical = offical.group()
    if len(price) !=0 :
        if len(area_array) == len(price) :
            minn=price[0]
            for i in price : minn=min(minn,i)
            for i in range(0,len(price)) :
                if price[i]==minn:
                    return area_array[i]
    else : 
        if len(area_array) >1 : print(dict_input["id"], "can xac dinh lai")
    if area_cal != 0: return area_cal
    if len(a) != 0:
        area_cal = max(a)
    ############################
    ## Return
    ############################
    if floor : return float(area_cal/floor)
    if area_cal==0 : return -1
    return area_cal
