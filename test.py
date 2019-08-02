import re
result = " {'Token': 'xxxx', 'Time': '15:22'} "
result2 = re.sub("[\']+|[:{} ]", "", str(result))
result3 = result2.split(',')
result3 = temp2[0][5:]
print('{}'.format(temp3))