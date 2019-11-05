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
        self.paramString = account + password  # Just Username + Password
        self.account = account  # Username
        self.password = password  # Password
        self.access_token = ""  # Token
        self.str1 = datetime.strftime(datetime.now(), '%Y/%m/%d %H:%M:%S')  # Device Time
        self.str2 = '2.2.0'  # App Version
        self.str3 = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S')  # Call time
        self.ModelId = 'MIX 3'  # Model ID
        self.OsVersion = '9'  # Android OS Version
        self.Platform = 'Android'  # Platform
        self.DeviceUuid = 'device_uuid'  # Device Uuid
        self.OrderNo = self.DeviceUuid + self.str3  # Order No
        self.cardNo = 'cardNo'  # Card NO

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
            "account": self.account,
            "password": self.password,
            "OrderNo": self.OrderNo,
            "mask": mask.hexdigest(),
            "source_info": {
                "app_version": self.str2,
                "device_time": self.str1,
                "device_uuid": self.DeviceUuid,
                "model_id": self.ModelId,
                "os_version": self.OsVersion,
                "platform": self.Platform,
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
        self.access_token = response['results']['member_info']['access_token']

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
            "OrderNo": self.OrderNo,
            "access_token": self.access_token,
            "callTime": self.str3,
            "cardNo": self.cardNo,
            "mask": mask.hexdigest(),
        }

        # Get the response
        response = requests.post('https://api.mcddaily.com.tw/queryBonus', json=json).text

        # Convert the string to dictionary type
        response = eval(response)

        # Return the dictionary type of response
        return response


def login_MC():
    # Login and get the information
    info = (Mask(account[0], account[1])).Login()
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
    if temp == 'Login':
        MC_Status, MC_Token = login_MC()
        if MC_Status == '登入成功' and MC_Token != '':
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=MC_Status + '\n每天準時晚上12點幫你抽\nヽ(‘ ∇‘ )ノ'))
            Database_Increase_Counter()
            Count = Database_Get_Counter()
            doc = {
                'Token' + str(Count): MC_Token
            }
            doc2 = {
                MC_Token: user_id
            }

            doc_ref = db.collection("Line_User").document('Info')
            doc2_ref = db.collection("Check").document('Token')
            doc_ref.update(doc)
            doc2_ref.update(doc2)

        else:
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=MC_Status + '\n 〒.〒 '))


def Database_Read_Data(path):
    doc_ref = db.document(path)
    Read_result = doc_ref.get().to_dict()
    return Read_result


def Database_Get_Counter():
    Path = 'Line_User/Counter'
    result = Database_Read_Data(Path)
    return int(result['Count'])


def Database_Increase_Counter():
    Count = Database_Get_Counter()
    Count = Count + 1
    doc = {
        'Count': Count
    }
    doc_ref = db.collection("Line_User").document('Counter')
    doc_ref.set(doc)


def Database_Get_TokenList():
    Path = 'Line_User/Info'
    Count = Database_Get_Counter()
    result = Database_Read_Data(Path)
    Token = []
    for i in range(Count + 1):
        Token.append(result['Token' + str(i)])
    return Token


def Database_Check_UserState(ID):
    for i in range(Database_Get_Counter()+1):
        try:
            token = list(Database_Read_Data('Check/Token').keys())[list(Database_Read_Data('Check/Token').values()).index(ID)]
            print('Line225 Token', token)
            user_exist = True
            break
        except ValueError:
            user_exist = False
            token = ''
    return user_exist, token


def McDonald_Get_CouponList():
    Account = McDonald(Database_Check_UserState(user_id)[1])
    print('Account:', Account)
    URLS_List = Account.Coupon_List()
    return URLS_List


def McDonald_Get_StickerList():
    print('Line241 UserID', user_id)
    Account = McDonald(Database_Check_UserState(user_id)[1])
    print('Line244 UserID', user_id)
    Sticker_List = Account.Sticker_List()
    return Sticker_List


def McDonald_ManualLottery_Coupon():
    Account = McDonald(Database_Check_UserState(user_id)[1])
    Get_Coupon, url = Account.Lottery()
    temp = url.split('/')[3]
    Filename = temp.split('.')[0]
    if not db.collection('Coupons').document(Filename).get().exists:
        doc = {'Title': Get_Coupon}
        doc_ref = db.collection("Coupons").document(Filename)
        doc_ref.set(doc)
    return Get_Coupon, url


def McDonald_AutoLottery_Coupon():
    Count = Database_Get_Counter()
    Token_List = Database_Get_TokenList()
    ref = db.document('Check/Token')
    doc = ref.get().to_dict()

    for i in range(Count + 1):
        userid = doc[Token_List[i]]
        token = Database_Check_UserState(userid)[1]
        Account = McDonald(token)
        title, url = Account.Lottery()
        temp = url.split('/')[3]
        Filename = temp.split('.')[0]

        if not db.collection('Coupons').document(Filename).get().exists:
            doc = {'Title': title}
            doc_ref = db.collection("Coupons").document(Filename)
            doc_ref.set(doc)

        message = TemplateSendMessage(alt_text='圖片訊息', template=ImageCarouselTemplate(columns=[ImageCarouselColumn(image_url=url, action=PostbackTemplateAction(label='查看我的優惠卷', text='我的優惠卷',data='action=buy&itemid=1')), ]))
        Message2 = TextSendMessage(text='每日抽獎~恭喜你獲得~')

        line_bot_api.push_message(userid, Message2)
        line_bot_api.push_message(userid, message)
    print('McDonald_AutoLottery_Coupon OK')


def McDonald_AutoLottery_Sticker():
    Count = Database_Get_Counter()
    Token_List = Database_Get_TokenList()
    ref = db.document('Check/Token')
    doc = ref.get().to_dict()

    for i in range(Count + 1):
        userid = doc[Token_List[i]]
        token = Database_Check_UserState(userid)[1]
        Account = McDonald(token)
        Sticker_List = Account.Sticker_List()

        if int(Sticker_List[0]) >= 6:
            title, url = Account.Sticker_lottery()
            temp = url.split('/')[3]
            Filename = temp.split('.')[0]

            if not db.collection('Coupons').document(Filename).get().exists:
                doc = {'Title': title}
                doc_ref = db.collection("Coupons").document(Filename)
                doc_ref.set(doc)

            message = TemplateSendMessage(alt_text='圖片訊息', template=ImageCarouselTemplate(columns=[ImageCarouselColumn(image_url=url, action=PostbackTemplateAction(label='查看我的優惠卷', text='我的優惠卷',data='action=buy&itemid=1')), ]))
            Message2 = TextSendMessage(text='歡樂貼自動抽獎~~恭喜你獲得~')

            line_bot_api.push_message(userid, Message2)
            line_bot_api.push_message(userid, message)
    print('McDonald_AutoLottery_Sticker OK')


# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global user_id
    global account
    user_id = event.source.user_id
    print('Line324 ID', user_id)
    # ----------------Login-----------------------
    if Database_Check_UserState(user_id)[0]:
        print('Line326 ID', user_id)
        if event.message.text == '我的歡樂貼':
            StickerList = McDonald_Get_StickerList()
            line_bot_api.reply_message(event.reply_token, TextSendMessage(
                text='目前擁有歡樂貼:{}\n月底即將到期歡樂貼:{}'.format(StickerList[0], StickerList[1])))

        elif event.message.text == '抽獎':
            url = McDonald_ManualLottery_Coupon()[1]
            message = TemplateSendMessage(alt_text='圖片訊息', template=ImageCarouselTemplate(columns=[ImageCarouselColumn(image_url=url, action=PostbackTemplateAction(label='查看我的優惠卷', text='我的優惠卷', data='action=buy&itemid=1')), ]))
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
            McDonald_AutoLottery_Coupon()
        elif event.message.text == '手動測試-2':
            McDonald_AutoLottery_Sticker()

        else:
            Random_type = random.randint(1, 5)
            if Random_type == 1:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='你可以試試輸入【我的優惠卷】 \n(・∀・)'))
            elif Random_type == 2:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='說不定輸入【我的歡樂貼】會有事情發生呢 \n(ノ^o^)ノ'))
            elif Random_type == 3:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='輸入神秘指令【抽獎】會有怪事發生呢\nლ(｀∀´ლ) '))
            elif Random_type == 4:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='我好累，不想工作。\n罷工拉 \n(-。-;'))
            elif Random_type == 5:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='看我施展魔法 \n(∩｀-´)⊃━炎炎炎炎炎'))

    else:
        temp = event.message.text
        if temp != '登入':
            if '/' not in temp:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='注意!!少了斜線(/)  Σ( ° △ °|||)'))
            else:
                account = temp.split('/')
                if len(account) > 2:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text='多打了斜線哦  Σ( ° △ °|||)'))
                else:
                    Login_message = TemplateSendMessage(alt_text='Template', template=ButtonsTemplate(title='登入確認', text='帳號:{}\n密碼:{}'.format(account[0], account[1]), actions=[PostbackTemplateAction(label='按此登入', text='登入', data='Login')]))
                    line_bot_api.reply_message(event.reply_token, Login_message)


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
