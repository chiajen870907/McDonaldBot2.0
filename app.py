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



app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('i3MY/ddSyAqnc9JG/Sbce2EH7N1A48HRWE1NCokvL3w00hNGZPVud1buRLuwkSL9rP8860UKkQTo3h2flGoSijgeZ/LvaepXs/t4x/T/X39BZuJ/wBrS9O43luJDHSa4Tl7OMcuy4TYBuo2nLbiv4AdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('22a4d312cd87888ee4ae3e8c79b989ea')
# 引用私密金鑰
cred = credentials.Certificate('/app/service-account.json')
#cred = credentials.Certificate('C:/Users\HsiehCJ/Desktop/Project/PyCharm/McDonaldBot/service-account.json')

# 初始化firebase，注意不能重複初始化
firebase_admin.initialize_app(cred)
# 初始化firestore
db = firestore.client()

# McDonald------------------


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
    MC_Status=(list['rm'])
    MC_Token=(list['results']['member_info']['access_token'])
    return MC_Status, MC_Token

# --------------------------

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

# 等待伺服器回傳資料
@handler.add(PostbackEvent)
def handle_postback(event):
    if event.postback.data == 'datetime_postback':
        global Set_Time
        Set_Time = event.postback.params['time']
        #print(Set_Time)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text='我知道喇~~\n每天' + event.postback.params['time'] + '準時幫你抽\n （〜^∇^)〜'))
        doc = {
            'Time': Set_Time
        }
        doc_ref = db.collection("Line_User").document(user_id)
        doc_ref.update(doc)
        #print(Set_Time)


def Database_Counter_GetCount():
    Count_path = ('Line_User/Counter')
    doc_ref = db.document(Count_path)
    doc = doc_ref.get()
    Count_result = doc.to_dict()
    #(Count_result)
    Count_Index = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）:{} Count]", "", str(Count_result))
    return Count_Index


def Database_Counter_Increase():
    Count_Index = Database_Counter_GetCount()
    Count_Index = int(Count_Index) + 1
    doc = {
        'Count': Count_Index
    }
    doc_ref = db.collection("Line_User").document('Counter')
    doc_ref.set(doc)
    #print(Count_Index)


def Database_Counter_Decrease():
    Count_Index = Database_Counter_GetCount()
    Count_Index = int(Count_Index) - 1
    doc = {
        'Count': Count_Index
    }
    doc_ref = db.collection("Line_User").document('Counter')
    doc_ref.set(doc)
    # print(Count_Index)


def Database_Get_Token():
    Count = Database_Counter_GetCount()
    Count_path = ('Line_User/Info')
    doc_ref = db.document(Count_path)
    doc = doc_ref.get()
    result = doc.to_dict()
    Index = re.sub("[{} \' :]", "", str(result))
    # print('Index', Index)
    nCount_Index = int(Count) + 1
    for i in range(nCount_Index):
        Index = Index.replace('Token' + str(i), '')
    # print('Database_Check_UserID() ', Index)
    GetToken = Index.split(',')
    # print(type(GetToken))
    return GetToken


def Database_Check_UserID():
    Count_Index = Database_Counter_GetCount()
    Count_path = ('Line_User/Info')
    doc_ref = db.document(Count_path)
    doc = doc_ref.get()
    result = doc.to_dict()
    Index = re.sub("[{} \' :]", "", str(result))
    # print('Index', Index)
    nCount_Index = int(Count_Index) + 1
    for i in range(nCount_Index):
        Index = Index.replace('Token' + str(i), '')
    # print('Database_Check_UserID() ', Index)
    GetToken = Index.split(',')
    for i in range(int(Count_Index)):
        path_ID = ("MD_Token/" + GetToken[i])
        # print('path_ID', path_ID)
        ref = db.document(path_ID)
        doc = ref.get()
        temp_ID = str(doc.to_dict())
        # print('temp_ID ', temp_ID)
        result_ID = re.search(user_id, temp_ID)
        #print('result_ID', result_ID)
        if result_ID is None:
            UserID_Exists = 0
            # ('CantFind')
        else:
            UserID_Exists = 1
            #re.search(user_id, result)
            # ('Find_UserID')
        return UserID_Exists


def McDonald_Get_Stack():
    Token_List = Database_Get_Token()
    Count = int(Database_Counter_GetCount())
    for i in range(Count):
        path_ID = ("MD_Token/" + Token_List[i])
        ref = db.document(path_ID)
        doc = ref.get()
        PushID = str(doc.to_dict())
        PushID = re.sub("[{} \' :]", "", str(PushID))
        PushID = PushID.replace('UserID', '')
        Account = McDonald(Token_List[i])
        line_bot_api.push_message(PushID, TextSendMessage(text=Account.Lottery()))


def McDonald_Lottery():
    Token_List = Database_Get_Token()
    Count = int(Database_Counter_GetCount())
    for i in range(Count):
        path_ID = ("MD_Token/" + Token_List[i])
        ref = db.document(path_ID)
        doc = ref.get()
        PushID = str(doc.to_dict())
        PushID = re.sub("[{} \' :]", "", str(PushID))
        PushID = PushID.replace('UserID', '')
        Account = McDonald(Token_List[i])
        line_bot_api.push_message(PushID, TextSendMessage(text=Account.Lottery()))


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # message = TextSendMessage(text=event.message.text)
    # line_bot_api.reply_message(event.reply_token, message)
    global user_id
    user_id = event.source.user_id
    # ----------------Login-----------------------
    Check = Database_Check_UserID()
    if Check == 1:
        print('存在')
        if event.message.text == 'Lottery':
            McDonald_Lottery()
        # elif event.message.text == '優惠卷123456':
        #     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=McDonald.Coupon_List()))
        # elif event.message.text == '貼紙123456':
        #     line_bot_api.reply_message(event.reply_token, TextSendMessage(text=McDonald.Sticker_List()))

        # if event.message.text == 'DATA123456':
        #     date_picker = TemplateSendMessage(
        #         alt_text='時間設定',
        #         template=ButtonsTemplate(
        #             text=' 我每天幾點幫你抽呢  ヽ(‘ ∇‘ )ノ ',
        #             title='時間設定',
        #             actions=[
        #                     DatetimePickerTemplateAction(label='設定', data='datetime_postback', mode='time')
        #             ]
        #         )
        #     )
        #     line_bot_api.reply_message(event.reply_token, date_picker)
    else:
        temp = event.message.text
        if '/' not in temp:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='注意!!少了斜線(/)  Σ( ° △ °|||)'))
        t = temp.split('/')
        if len(t) > 2:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='多打了斜線哦  Σ( ° △ °|||)'))
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text='帳號:{}\n密碼:{}\n正在嘗試登入麥當勞  \n(●’ω`●）'.format(t[0], t[1])))
        global MC_User_ID, MC_User_PASSWORD
        MC_User_ID = t[0]
        MC_User_PASSWORD = t[1]
        MC_Status, MC_Token = login_MC()
        if MC_Status == '登入成功' and MC_Token != '':
            line_bot_api.push_message(user_id, TextSendMessage(text= MC_Status + " *\(^_^)/* "))
            Database_Counter_Increase()
            Count = Database_Counter_GetCount()
            doc = {
                'Token' + Count: MC_Token
            }
            doc2 = {
                'UserID': user_id
            }
            doc_ref = db.collection("Line_User").document('Info')
            doc2_ref = db.collection("MD_Token").document(MC_Token)
            doc_ref.update(doc)
            doc2_ref.set(doc2)
            line_bot_api.push_message(user_id, TextSendMessage(text='我知道喇~\n每天準時晚上12點幫你抽\nヽ(‘ ∇‘ )ノ'))
        else:
            line_bot_api.push_message(user_id, TextSendMessage(text='錯誤請重新登入\n 〒.〒 '))


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)









