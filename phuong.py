import json
import codecs

def funcPhuong(listHung):
    ban=[]
    thue=[]
    tmpB=0
    tmpT=0
    aBan=[]
    aThue=[]
    ctmp = ''

    for i in listHung[1]:
        if ban == [] and thue == []:
            i = i + '+None'
            # print(i)
            continue
        icontent = i.lower().split(' ')
        # print(icontent[0])
        dBan = 10000000
        dThue = 10000000
        if find_sub_list(icontent, listHung[0]['content']) != []:
            ind = find_sub_list(icontent, listHung[0]['content'])[0][0]
            # print("Index: ",ind)
            if len(ban) > 0:
                for j in ban:
                    # print(c)
                    if abs(ind - j) < dBan:
                        # print("JBan: ",j)
                        dBan = abs(ind - j)
                    else:
                        continue
            if len(thue) > 0:
                for j in thue:
                    if abs(ind - j) < dThue:
                        # print("JThue: ",j)
                        dThue = abs(ind - j)
                    else:
                        continue
            if dBan < dThue:
                i = i + '+Bán'
            else:
                i = i + '+Thuê'
            # print("Ban: ",dBan)
            # print("Thue: ",dThue)
            print(i)
    ban = []
    thue = []


def find_sub_list(sl,l):
    results=[]
    sll=len(sl)
    for ind in (i for i,e in enumerate(l) if e==sl[0]):
        if l[ind:ind+sll]==sl:
            results.append((ind,ind+sll-1))
    #print(results)
    return results

with open('data.json', 'rb') as json_file:
    dataset = json.loads(json_file.read())
    for data in dataset:

        lstTemp = []
        att = data['attributes']
        for i in att:
            if i['type'] == 'price':
                lstTemp.append(i['content'])

        print(lstTemp)
        funcPhuong([data, lstTemp])