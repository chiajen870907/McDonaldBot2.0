from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import firebase_admin
import os
import re
import hashlib
import requests
from datetime import datetime
from firebase_admin import credentials
from firebase_admin import firestore
from McDonald import McDonald

cred = credentials.Certificate('C:/Users/HsiehCJ/Desktop/Project/PyCharm/McDonaldBot/service-account.json')
# 初始化firebase，注意不能重複初始化
firebase_admin.initialize_app(cred)
# 初始化firestore
db = firestore.client()


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

def Database_Read_Data(Read_path):
    doc_ref = db.document(Read_path)
    doc = doc_ref.get()
    Read_result = doc.to_dict()
    return Read_result

def login_MC():
    global lag
    lag = 0
    if lag == 0:
        print('here1')
        Old_Token = 'Uea249350320c7cd2401b3667ed9abdc3'
        Username = '097300201'
        Password = 'break7520'
        # Login and get the imformation
        print('here2')
        Account = Mask(Username, Password)
        list = Account.Login()
        # Print the results
        MC_Status = (list['rm'])
        MC_Token = (list['results']['member_info']['access_token'])
        return MC_Status, MC_Token, Old_Token

def McDonald_Get_State():
    Path = 'Check/FdEjegADAOCxAHw6'
    result = Database_Read_Data(Path)
    result = re.sub("[{} \' :]", "", str(result))
    result = result.replace('Token', '')
    return result

def McDonald_Get_CouponList():
    #result = McDonald_Get_State()
    Account = McDonald('FdEjegADAOCxAHw6')
    Coupon_List = Account.Coupon_List()
    Coupon_List = re.sub("[\s+\.\!\/_$%^*(+\"\']+|[+——！。？、~@#￥%……&*（）:{}\[\] ]", "", str(Coupon_List))
    Coupon_List = Coupon_List.replace(',', "\n")
    return Coupon_List

a = McDonald_Get_CouponList()
print(a)