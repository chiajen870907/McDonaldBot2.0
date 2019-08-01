from flask import Flask, request, abort
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *
import firebase_admin
import os
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
#print(os.getcwd())

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
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)
    user_id = event.source.user_id

    if event.message.text == "Login":
        print('Login')
        # ----------------Login-----------------------
        path = ("Line_User/" + user_id)
        print(path)
        doc_ref = db.document(path)
        try:
            doc = doc_ref.get()
            print("文件內容為：{}".format(doc.to_dict()))
            check = True
        except:
            print("指定文件的路徑{}不存在，請檢查路徑是否正確".format(path))
            check = False


        if check == False:
            temp = event.message.text
            if '/' not in temp:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='注意!!少了斜線(/)'))
            t = temp.split('/')
            if len(t) > 2:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請重新輸入-多打了斜線了'))
            buttons_template = TemplateSendMessage(
                alt_text='Template',
                template=ButtonsTemplate(
                    title='登入確認',
                    text='帳號:{}\n密碼:{}\n請確定是否正確'.format(t[0], t[1]),
                    actions=[
                        MessageTemplateAction(
                            label='確認無誤',
                            text='MENU'
                        ),
                        PostbackTemplateAction(
                            label='重新輸入',
                            text='請再輸入一次，帳號與密買以斜線(/)區隔',
                            data='revise'
                        )
                    ]
                )
            )
        #line_bot_api.reply_message(event.reply_token,buttons_template)

    # t = fb.get('/{}/num'.format(user_id), None)
    # number = fb.get('/{}/temp'.format(user_id), None)


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












