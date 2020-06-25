from flask import Flask, request, render_template, abort
from linebot.exceptions import (InvalidSignatureError)
from linebot import (LineBotApi, WebhookHandler)
from linebot.models import *
from random import choice

from datetime import datetime


from module.db import DB_Firebase
from module.mcd import mcd
from module.line import flex


import hashlib
import requests
import os
import json
from flask import jsonify


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


app = Flask(__name__)

# Channel Access Token
line_bot_api = LineBotApi('i3MY/ddSyAqnc9JG/Sbce2EH7N1A48HRWE1NCokvL3w00hNGZPVud1buRLuwkSL9rP8860UKkQTo3h2flGoSijgeZ/LvaepXs/t4x/T/X39BZuJ/wBrS9O43luJDHSa4Tl7OMcuy4TYBuo2nLbiv4AdB04t89/1O/w1cDnyilFU=')

# Channel Secret
handler = WebhookHandler('22a4d312cd87888ee4ae3e8c79b989ea')

app.debug = True

db = DB_Firebase.DBHelper()




#From web


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/api/appRegister', methods=['POST'])
def appRegister():
    db = DB_Firebase.DBHelper()
    data =json.loads(request.get_data())# 接收所有DATA
    if data['username'] != '' and data['password'] != '':
        result = login_MC(data['username'], data['password'])
        if(result[0]=='登入成功'):
            db.set_create_user(data['UID'],result[1])
            return jsonify({"success": '操作成功', "msg": "success"})
        else:
            return jsonify({"success": '操作成功', "msg": "error", "data": "帳號或密碼錯誤，請重新輸入"})
    else:
        return jsonify({"success": '操作成功', "msg": "error", "data": "帳號或密碼錯誤，請重新輸入"})

#Line
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
    ret = db.get_check_exists(event.source.user_id)
    res = flex.Line()
    if ret:
        md = mcd.MCDHelper()

        if event.message.text == '歡樂貼':
            stickers , exprice_stickers = md.get_sircketlist(ret['mc_token'])
            print(stickers,exprice_stickers)

            message = res.flex_message_sticker(stickers,exprice_stickers)
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='訊息', contents=message))

        elif event.message.text == '優惠券':
            url, title, datetime = md.get_couponlist(ret['mc_token'])
            if not url:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='o_O ||\n你沒有任何優惠卷ㅇㅁㅇ'))
            else:
                message = res.flex_message_coupon(url,title,datetime)
                line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='訊息',contents=message))

        elif event.message.text == '抽獎':
            _, url = md.get_lottery(ret['mc_token'])
            message = res.flex_message_lottery(url, type='手動抽')
            line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='訊息', contents=message))

        elif event.message.text == '換好禮':
            check = md.get_stickers_lottery(ret['mc_token'])
            if(check):
                message = res.flex_message_lottery(check[1], type='換好禮')
                line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='訊息', contents=message))
            else:
                message = TextSendMessage(text='歡樂貼不足')
                line_bot_api.reply_message(event.reply_token,message)

        elif event.message.text == '帳號設定':
            message = TextSendMessage(text='目前僅開放給初次登入用，暫無相關設定功能，預計之後更新加入')
            line_bot_api.reply_message(event.reply_token, message)

        else:
            text_list = ['你可以試試輸入【優惠券】 \n(・∀・)','說不定輸入【歡樂貼】會有事情發生呢 \n(ノ^o^)ノ','輸入神秘指令【抽獎】會有怪事發生呢\nლ(｀∀´ლ) ','我好累，不想工作。\n罷工拉 \n(-。-;','看我施展魔法 \n(∩｀-´)⊃━炎炎炎炎炎']
            message = TextSendMessage(text=choice(text_list))
            line_bot_api.reply_message(event.reply_token, message)
    else:
        message = res.flex_message_account()
        line_bot_api.reply_message(event.reply_token, FlexSendMessage(alt_text='訊息',contents=message))


def login_MC(username,password):
    # Login and get the information
    info = (Mask(username, password)).Login()
    MC_Status = (info['rm'])
    MC_Token = (info['results']['member_info']['access_token'])
    return MC_Status, MC_Token


def auto_lottery():
    print('Start Auto Lottery')
    md = mcd.MCDHelper()
    res = flex.Line()
    docs = db.get_allusers()
    for doc in docs:
        id = doc.id
        token = doc.to_dict()['mc_token']
        print(f'User:{id} Token{token}')
        _, url = md.get_lottery(token)
        if(url.split('/')[3] == 'ccrotbJmNrxfvvc7iYXZ.jpg'):
            message = res.flex_message_lottery(url, type='自動抽')
            line_bot_api.push_message(id,FlexSendMessage(alt_text='訊息', contents=message))



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
