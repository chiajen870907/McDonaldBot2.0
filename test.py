import re


result = "{'Token1': 'ElwCo9+jfBwATACG', 'Token2': 'zwAlTgDIEwIiYi08'}"
Index = re.sub("[{} \' :]", "", str(result))

for i in range(10):
    Index = Index.replace('Token' + str(i), '')
    print(Index)