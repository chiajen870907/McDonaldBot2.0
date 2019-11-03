from linebot.exceptions import (InvalidSignatureError)
from linebot import (LineBotApi, WebhookHandler)
from linebot.models import *

from flask import Flask, request, abort
from datetime import datetime

from firebase_admin import credentials
from firebase_admin import firestore

import firebase_admin
import requests
import hashlib
import random
import os
import re

from McDonald import McDonald


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('i3MY/ddSyAqnc9JG/Sbce2EH7N1A48HRWE1NCokvL3w00hNGZPVud1buRLuwkSL9rP8860UKkQTo3h2flGoSijgeZ/LvaepXs/t4x/T/X39BZuJ/wBrS9O43luJDHSa4Tl7OMcuy4TYBuo2nLbiv4AdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('22a4d312cd87888ee4ae3e8c79b989ea')
# private_key
private_key = credentials.Certificate('/app/service-account.json')


# 初始化firebase，注意不能重複初始化
firebase_admin.initialize_app(private_key)
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
        headers = {
            'Connection': 'close'
        }
        # Get the response
        response = requests.post('https://api.mcddaily.com.tw/login_by_mobile', json=json, headers=headers).text

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
        response = requests.post('https://api.mcddaily.com.tw/queryBonus', json=json).text

        # Convert the string to dictionary type
        response = eval(response)

        # Return the dictionary type of response
        return response


def login_MC():
    Username = t[0]
    Password = t[1]
    # Login and get the imformation
    Account = Mask(Username, Password)
    info = Account.Login()
    MC_Status = (info['rm'])
    MC_Token = (info['results']['member_info']['access_token'])
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
    temp = event.postback.data
    if temp == 'Login' and db.collection('Check').document(user_id).get().exists == False:
        MC_Status, MC_Token = login_MC()
        if MC_Status == '登入成功' and MC_Token != '':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=MC_Status + '\n每天準時晚上12點幫你抽\nヽ(‘ ∇‘ )ノ'))
            Database_Counter_Increase()
            Count = Database_Counter_GetCount()
            doc = {
                'Token' + str(Count): MC_Token
            }
            doc2 = {
                'UserID': user_id
            }
            doc3 = {
                'Token': MC_Token
            }
            doc_ref = db.collection("Line_User").document('Info')
            doc2_ref = db.collection("MD_Token").document(MC_Token)
            doc3_ref = db.collection("Check").document(user_id)
            doc_ref.update(doc)
            doc2_ref.set(doc2)
            doc3_ref.set(doc3)
        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=MC_Status + '\n 〒.〒 '))


def Database_Read_Data(path):
    doc_ref = db.document(path)
    doc = doc_ref.get()
    Read_result = doc.to_dict()
    return Read_result


def Database_Counter_GetCount():
    Path = 'Line_User/Counter'
    result = Database_Read_Data(Path)
    result = re.sub("[\s+\.\!\/_,$%^*(+\"\']+|[+——！，。？、~@#￥%……&*（）:{} Count]", "", str(result))
    return int(result)


def Database_Counter_Increase():
    Count = Database_Counter_GetCount()
    Count = Count + 1
    doc = {
        'Count': Count
    }
    doc_ref = db.collection("Line_User").document('Counter')
    doc_ref.set(doc)


def Database_Get_Token():
    Path = 'Line_User/Info'
    Count = Database_Counter_GetCount()
    result = Database_Read_Data(Path)
    print(result)
    Index = re.sub("[{} \' :]", "", str(result))
    for i in range(Count):
        Index = Index.replace('Token' + str(i), '')
    GetToken = Index.split(',')
    return GetToken


def Database_Check_UserID():
    Count = Database_Counter_GetCount()
    Path = 'Line_User/Info'
    result = Database_Read_Data(Path)
    Index = re.sub("[{} \' :]", "", str(result))
    for i in range(Count):
        Index = Index.replace('Token' + str(i), '')
    GetToken = Index.split(',')
    for i in range(int(Count)):
        Path_ID = ("MD_Token/" + GetToken[i])
        result = Database_Read_Data(Path_ID)
        result_ID = re.search(user_id, str(result))
        if result_ID is None:
            UserID_Exists = 0
            #  NotExist
        else:
            UserID_Exists = 1
            #  Exist
        return UserID_Exists


def McDonald_Get_State():
    Path = 'Check/' + user_id
    result = Database_Read_Data(Path)
    result = re.sub("[{} \' :]", "", str(result))
    result = result.replace('Token', '')
    return result


def McDonald_Get_StickerList():
    result = McDonald_Get_State()
    Account = McDonald(result)
    Sticker_List = Account.Sticker_List()
    Sticker_List = re.sub("[/'()]", "", str(Sticker_List))
    Sticker_List_result = Sticker_List.split(',')

    return Sticker_List_result


def McDonald_Get_CouponList():

    result = McDonald_Get_State()
    Account = McDonald(result)
    URLS_List = Account.Coupon_List()
    # Coupon_List = re.sub("[\s+\.\!\/_$%^*(+\"\']+|[+——！。？、~@#￥%……&*（):{}\[\] ]", "", str(Coupon_List))
    # Coupon_List = Coupon_List.replace(',', "\n")
    return URLS_List


def Manual_Coupon_Lottery():
    result = McDonald_Get_State()
    Account = McDonald(result)
    Get_Coupon, url = Account.Lottery()
    temp = url.split('/')[3]
    Filename = temp.split('.')[0]
    if not db.collection('Coupons').document(Filename).get().exists:
        doc = {'Title': Get_Coupon}
        doc_ref = db.collection("Coupons").document(Filename)
        doc_ref.set(doc)
    return Get_Coupon, url


def Auto_Coupon_Lottery():
    Token_List = Database_Get_Token()
    Count = Database_Counter_GetCount()
    print(Count)
    for i in range(Count):
        path_ID = ("MD_Token/" + Token_List[i])
        ref = db.document(path_ID)
        doc = ref.get()
        PushID = str(doc.to_dict())
        PushID = re.sub("[{} \' :]", "", str(PushID))
        PushID = PushID.replace('UserID', '')
        print(PushID)
        print(Token_List[i])
        print(int(i))
        Account = McDonald(Token_List[i])
        title, url = Account.Lottery()
        temp = url.split('/')[3]
        Filename = temp.split('.')[0]
        if not db.collection('Coupons').document(Filename).get().exists:
            doc = {'Title': title}
            doc_ref = db.collection("Coupons").document(Filename)
            doc_ref.set(doc)
        message = TemplateSendMessage(alt_text='圖片訊息', template=ImageCarouselTemplate(columns=[ImageCarouselColumn(image_url=url, action=PostbackTemplateAction(label='查看我的優惠卷', text='我的優惠卷',data='action=buy&itemid=1')), ]))
        Message2 = TextSendMessage(text='每日抽獎~恭喜你獲得~')
        line_bot_api.push_message('Uea249350320c7cd2401b3667ed9abdc3', Message2)
        line_bot_api.push_message('Uea249350320c7cd2401b3667ed9abdc3', message)


def Auto_Sticker_Lottery():
    Token_List = Database_Get_Token()
    Count = Database_Counter_GetCount()

    for i in range(Count):
        path_ID = ("MD_Token/" + Token_List[i])
        ref = db.document(path_ID)
        doc = ref.get()
        PushID = str(doc.to_dict())
        PushID = re.sub("[{} \' :]", "", str(PushID))
        PushID = PushID.replace('UserID', '')
        Account = McDonald(Token_List[i])

        result_coupon = McDonald_Get_StickerList()
        if int(result_coupon[0]) >= 6:
            title, url = Account.Sticker_lottery
            temp = url.split('/')[3]
            Filename = temp.split('.')[0]
            if not db.collection('Coupons').document(Filename).get().exists:
                doc = {'Title': title}
                doc_ref = db.collection("Coupons").document(Filename)
                doc_ref.set(doc)
            message = TemplateSendMessage(alt_text='圖片訊息', template=ImageCarouselTemplate(columns=[ImageCarouselColumn(image_url=url, action=PostbackTemplateAction(label='查看我的優惠卷', text='我的優惠卷',data='action=buy&itemid=1')), ]))
            Message2 = TextSendMessage(text='歡樂貼自動抽獎~~恭喜你獲得~')
            line_bot_api.push_message(PushID, Message2)
            line_bot_api.push_message(PushID, message)
    print("OK")

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global user_id
    global t
    user_id = event.source.user_id
    # ----------------Login-----------------------
    if db.collection('Check').document(user_id).get().exists:
        if event.message.text == '我的歡樂貼':
            result = McDonald_Get_StickerList()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text='目前擁有歡樂貼:{}\n月底即將到期歡樂貼:{}'.format(result[0], result[1])))

        elif event.message.text == '抽獎':
            url = Manual_Coupon_Lottery()[1]
            message = TemplateSendMessage(alt_text='圖片訊息', template=ImageCarouselTemplate(columns=[ ImageCarouselColumn(image_url=url, action=PostbackTemplateAction(label='查看我的優惠卷',text='我的優惠卷',data='action=buy&itemid=1')),]))
            line_bot_api.reply_message(event.reply_token, message)

        elif event.message.text == '我的優惠卷':
            URLS_List = McDonald_Get_CouponList()
            if not URLS_List:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='o_O ||\n你沒有任何優惠卷ㅇㅁㅇ'))
            else:
                URLS_Items = len(URLS_List)
                if URLS_Items == 1:
                    message = TemplateSendMessage(
                        alt_text='圖片訊息',
                        template=ImageCarouselTemplate(
                            columns=[
                                ImageCarouselColumn(
                                    image_url=URLS_List[0],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=1'
                                    )
                                )
                            ]
                        )
                    )
                    line_bot_api.reply_message(event.reply_token, message)
                elif URLS_Items == 2:
                    message = TemplateSendMessage(
                        alt_text='圖片訊息',
                        template=ImageCarouselTemplate(
                            columns=[
                                ImageCarouselColumn(
                                    image_url=URLS_List[0],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=1'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[1],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=2'
                                    )
                                )
                            ]
                        )
                    )
                    line_bot_api.reply_message(event.reply_token, message)
                elif URLS_Items == 3:
                    message = TemplateSendMessage(
                        alt_text='圖片訊息',
                        template=ImageCarouselTemplate(
                            columns=[
                                ImageCarouselColumn(
                                    image_url=URLS_List[0],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=1'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[1],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=2'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[2],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=3'
                                    )
                                )
                            ]
                        )
                    )
                    line_bot_api.reply_message(event.reply_token, message)
                elif URLS_Items == 4:
                    message = TemplateSendMessage(
                        alt_text='圖片訊息',
                        template=ImageCarouselTemplate(
                            columns=[
                                ImageCarouselColumn(
                                    image_url=URLS_List[0],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=1'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[1],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=2'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[2],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=3'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[3],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=4'
                                    )
                                )
                            ]
                        )
                    )
                    line_bot_api.reply_message(event.reply_token, message)
                elif URLS_Items == 5:
                    message = TemplateSendMessage(
                        alt_text='圖片訊息',
                        template=ImageCarouselTemplate(
                            columns=[
                                ImageCarouselColumn(
                                    image_url=URLS_List[0],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=1'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[1],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=2'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[2],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=3'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[3],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=4'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[4],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=5'
                                    )
                                )
                            ]
                        )
                    )
                    line_bot_api.reply_message(event.reply_token, message)
                elif URLS_Items == 6:
                    message = TemplateSendMessage(
                        alt_text='圖片訊息',
                        template=ImageCarouselTemplate(
                            columns=[
                                ImageCarouselColumn(
                                    image_url=URLS_List[0],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=1'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[1],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=2'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[2],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=3'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[3],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=4'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[4],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=5'
                                    )
                                ),
                                ImageCarouselColumn(
                                    image_url=URLS_List[5],
                                    action=PostbackTemplateAction(
                                        label='查看我的歡樂貼',
                                        text='我的歡樂貼',
                                        data='action=buy&itemid=6'
                                    )
                                )
                            ]
                        )
                    )
                    line_bot_api.reply_message(event.reply_token, message)

        elif event.message.text == '手動測試-1':
            Auto_Coupon_Lottery()
        elif event.message.text == '手動測試-2':
            Auto_Sticker_Lottery()
        elif event.message.text == "測試3":
            result = Database_Get_Token()
            print(result)

        else:
            Random_type = random.randint(1, 5)
            if Random_type == 1:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='你可以試試輸入【我的優惠卷】 \n(・∀・)'))
            elif Random_type == 2:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='說不定輸入【我的歡樂貼】會有事情發生呢 \n(ノ^o^)ノ'))
            elif Random_type == 3:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='【抽獎】是未知神秘指令 \nლ(｀∀´ლ) '))
            elif Random_type == 4:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='我好累，不想工作。\n罷工拉 \n(-。-;'))
            elif Random_type == 5:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='看我施展魔法 \n(∩｀-´)⊃━炎炎炎炎炎'))

    else:
        temp = event.message.text
        if temp != '登入':
            if '/' not in temp:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='注意!!少了斜線(/)  Σ( ° △ °|||)'))
            t = temp.split('/')
            if len(t) > 2:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='多打了斜線哦  Σ( ° △ °|||)'))
            Login_message = TemplateSendMessage(alt_text='Template', template=ButtonsTemplate(title='登入確認', text='帳號:{}\n密碼:{}\n請確定是否正確'.format(t[0], t[1]), actions=[PostbackTemplateAction(label='確認無誤', text='登入', data='Login')]))
            line_bot_api.reply_message(event.reply_token, Login_message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)









