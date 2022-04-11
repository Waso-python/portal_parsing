import re

def only_digit(val):
    res = ''
    for i in val:
        if i in ['0','1','2','3','4','5','6','7','8','9','0',',','.']:
            res += i
    return res


def get_inn(val):
    res = ''
    res = re.search("ИНН: \d{10}",val)
    return res

# s_text = 'hgfcjhkhh867878'
# s_text = 'ГОСУДАРСТВЕННОЕ БЮДЖЕТНОЕ ДОШКОЛЬНОЕ ОБРАЗОВАТЕЛЬНОЕ УЧРЕЖДЕНИЕ ДЕТСКИЙ САД № 22 КОЛПИНСКОГО РАЙОНА САНКТ-ПЕТЕРБУРГА (ИНН: 7817027443)'

# pr = get_inn(s_text)[0][5:16] if get_inn(s_text) else '0000000000'



# print(pr)