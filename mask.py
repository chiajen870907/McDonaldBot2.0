import hashlib
import requests
from
from datetime import datetime

class Mask(object):
    """docstring for Mask."""

    def __init__(self, account, password):
        super(Mask, self).__init__()
        self.paramString = account + password                              # Just Username + Password
        self.account = account                                             # Username
        self.password = password                                           # Password
        self.access_token = ""                                             # Token
        self.str1 = datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S') # Device Time
        self.str2 = '2.2.0'                                                # App Version
        self.str3 = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')      # Call time
        self.ModelId = 'MIX 3'                                             # Model ID
        self.OsVersion = '9'                                               # Android OS Version
        self.Platform = 'Android'                                          # Platform
        self.DeviceUuid = 'device_uuid'                                    # Device Uuid
        self.OrderNo = self.DeviceUuid + self.str3                         # Order No
        self.cardNo = 'cardNo'                                             # Card NO

    def Login(self):
        # Mask = MD5('Mc' + OrderNo + Platform + OsVersion + ModelId + DeviceUuid + str1 + str2 + paramString + 'Donalds')
        data = 'Mc%s%s%s%s%s%s%s%sDonalds' % (
            self.OrderNo,
            self.Platform,
            self.OsVersion,
            self.ModelId,
            self.DeviceUuid,
            self.str1,
            self.str2,
            self.paramString
        )
        mask = hashlib.md5()
        mask.update(data.encode('utf-8'))

        # Form data
        json = {
            "account" : self.account,
            "password": self.password,
            "OrderNo" : self.OrderNo,
            "mask"    : mask.hexdigest(),
            "source_info": {
                "app_version": self.str2,
                "device_time": self.str1,
                "device_uuid": self.DeviceUuid,
                "model_id"   : self.ModelId,
                "os_version" : self.OsVersion,
                "platform"   : self.Platform,
            }
        }

        # Get the response
        response = requests.post('https://api.mcddaily.com.tw/login_by_mobile', json = json).text

        # Clean the garbage date
        response = response.replace('null', '""')
        response = response.replace('true', '"true"')
        response = response.replace('false', '"false"')

        # Convert the string to dictionary type
        response = eval(response)

        # Get the token
        self.access_token =  response['results']['member_info']['access_token']

        # Return the dictionary type of response
        return response

    def CardIM(self):
        # Mask = MD5('Mc' + OrderNo + access_token + cardNo + callTime + 'Donalds')
        data = 'Mc%s%s%s%sDonalds' % (
            self.OrderNo,
            self.access_token,
            self.cardNo,
            self.str3,
        )
        mask = hashlib.md5()
        mask.update(data.encode('utf-8'))

        # From data
        json = {
            "OrderNo"     : self.OrderNo,
            "access_token": self.access_token,
            "callTime"    : self.str3,
            "cardNo"      : self.cardNo,
            "mask"        : mask.hexdigest(),
        }

        # Get the response
        response = requests.post('https://api.mcddaily.com.tw/queryBonus', json = json).text

        # Convert the string to dictionary type
        response = eval(response)

        # Return the dictionary type of response
        return response

# Login example
def Main():
    # User login page
    Username = input('Username : ')
    Password = input('Password : ')

    # Login and get the imformation
    Account = Mask(Username, Password)
    list = Account.Login()

    # Print the results
    print('')
    print('Login status : ' + list['rm'])
    print('Username     : ' + list['results']['member_info']['name']['last_name'] + list['results']['member_info']['name']['first_name'])
    print('Token        : ' + list['results']['member_info']['access_token'])

# Card imformation example
def Card():

    # Login and get the token
    Account = Mask('Username', 'Password')
    Account.Login()

    # Get the card imformation
    list = Account.CardIM()

    # Print the results
    print('')
    print('Money  : ' + list['bonusList'][2]['bonusVO']['qunatity'])
    print('Points : ' + list['bonusList'][1]['bonusVO']['qunatity'])

if __name__ == '__main__':
    Main()
