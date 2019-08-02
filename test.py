import re
result = "  ['UserID1234', 'Token123456789', 'Time1231'] "
result2 = re.sub("[\']+|[:{} ]", "", str(result))
result3 = result2.split(',')
result4 = result3[0][7:]
print('{}'.format(result4))