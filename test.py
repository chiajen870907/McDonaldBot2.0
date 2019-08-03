import re
def test():
    result_ID = re.search('1', '5')
    for i in range(10):
        if result_ID is None:
            UserID_Exists = 0
        else:
            UserID_Exists = 1

        return UserID_Exists

def main():

    a = test()
    print(a)
main()