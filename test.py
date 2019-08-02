import re
result = "  {'Token': '123456789', 'Time': '13:14', 'UserID': 'Uea249350320c7cd2401b3667ed9abdc3'}"
# result2 = re.sub("[\']+|[:{} ]", "", str(result))
# result3 = result2.split(',')
# result4 = result3[0][7:]
# print('{}'.format(result4))

A = re.search(r'Uea249350320c7cd401b3667ed9abdc3',result)
if A == None:
    print('n')
else:
    print('y')