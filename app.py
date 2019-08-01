from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import firebase_admin
import os
import hashlib
import requests
from datetime import datetime
from firebase_admin import credentials
from firebase_admin import firestore
from McDonald import McDonald

app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('a4ZRk4l00GSRM9haYsEAdV90WTEk+LMkWCI71MqObTkXFq8ygRUlbwD7qxeS0+vNX+bMN0FvnTP91dASCXNBuxw5HdN0/vCKcSQxIw+QE4u09ARZUmxg9Cg7NMBfn2EBCpfxNXN70UIDg+YwAs130wdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('62aab4cbbb8fe1efcfd845bc9211e748')
# 引用私密金鑰
cred = credentials.Certificate('/app/service-account.json')
# 初始化firebase，注意不能重複初始化
firebase_admin.initialize_app(cred)
# 初始化firestore
db = firestore.client()

#McDonald------------------
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

def login_MC():
    Username = MC_User_ID
    Password = MC_User_PASSWORD
    # Login and get the imformation
    Account = Mask(Username, Password)
    list = Account.Login()
    # Print the results
    global MC_Status, MC_Token
    MC_Status = (list['rm'])
    MC_Token = (list['results']+['member_info']+['access_token'])


# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # message = TextSendMessage(text=event.message.text)
    # line_bot_api.reply_message(event.reply_token, message)
    user_id = event.source.user_id
    # ----------------Login-----------------------
    path = ("Line_User/" + user_id)
    print(path)
    doc_ref = db.document(path)
    doc = doc_ref.get()
    result = doc.to_dict()
    print(result)
    if result == None:
        print('Login First')
        temp = event.message.text
        if '/' not in temp:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='注意!!少了斜線(/)'))
        t = temp.split('/')
        if len(t) > 2:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請重新輸入-多打了斜線了'))
        line_bot_api.push_message(user_id, TextSendMessage(text='帳號:{}\n密碼:{}\n正在嘗試登入OwO'.format(t[0], t[1])))
        global MC_User_ID, MC_User_PASSWORD
        MC_User_ID = t[0]
        MC_User_PASSWORD = t[1]
        login_MC()
        line_bot_api.push_message(user_id, TextSendMessage(text=MC_Status))
        if MC_Token != '':
            doc = {
                'Token' : MC_Token
            }
            doc_ref = db.collection("Line_User").document(user_id)
            doc_ref.set(doc)










    # doc = {
    #     'Token': "abc@gmail.com"
    # }
    # # doc_ref = db.collection("集合名稱").document("文件id")
    # doc_ref = db.collection("Line_User").document(user_id)
    # # doc_ref提供一個set的方法，input必須是dictionary
    # doc_ref.set(doc)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)












