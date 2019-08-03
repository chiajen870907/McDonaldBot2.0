
def test():
    x = 0
    for i in range(10):
        if i==1:
            x = 1
            break
        print('r')
    return x

a = test()
print(a)