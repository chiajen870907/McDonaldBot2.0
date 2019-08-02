import re
t = " {'Token': 'xxxx', 'Time': '15:22'} "
temp = re.sub("[\']+|[:{} ]", "", str(t))

temp2 = temp.split(',')
temp3 = temp2[0][5:]
print('{}'.format(temp3))