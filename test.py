import re
Count_Index = 2
nCount_Index = int(Count_Index) + 5
# result = "{'Token1': 'ElwCo9+jfBwATACG', 'Token2': 'zwAlTgDIEwIiYi08'}"
# # Index = re.sub("[{} \' :]", "", str(result))
Index = 'Token1ElwCo9+jfBwATACG,Token2zwAlTgDIEwIiYi08'
for i in range(nCount_Index):
    TokenList = Index.replace('Token' + str(i), '')
    print(TokenList)
print('Database_Check_UserID() ', TokenList)
GetToken = Index.split(',')
print('GetToken:', GetToken[0])
# t = Index.split(',')
# print(t[0])
