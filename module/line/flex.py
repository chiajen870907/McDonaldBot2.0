from linebot.exceptions import (InvalidSignatureError)
from linebot import (LineBotApi, WebhookHandler)
from linebot.models import *

class Line:
    def __init__(self):
        self.modle = {"type": "carousel", "contents": []}
        self.content_list = []

    def flex_message_coupon(self,url,title,datetime):
        for index in range(len(url)):
            content = {
                "type": "bubble",
                "hero": {
                    "type": "image",
                    "url": f"{url[index]}",
                    "size": "full",
                    # "aspectRatio": "20:13",
                    "aspectMode": "cover",
                },
                "body": {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        # {
                        #     "type": "text",
                        #     "text": f"{header}",
                        #     "weight": "bold",
                        #     "size": "xl"
                        # },
                        {
                            "type": "separator"
                        },
                        {
                            "type": "box",
                            "layout": "vertical",
                            "margin": "lg",
                            "spacing": "sm",
                            "contents": [
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "優惠券",
                                            "size": "sm",
                                            "flex": 5,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{title[index]}",
                                            "color": "#228B22",
                                            "size": "sm",
                                            "flex": 5,
                                            "align": "start"
                                        }
                                    ]
                                },
                                {
                                    "type": "separator"
                                },
                                {
                                    "type": "box",
                                    "layout": "vertical",
                                    "spacing": "sm",
                                    "contents": [
                                        {
                                            "type": "text",
                                            "text": "使用期限",
                                            "size": "sm",
                                            "flex": 5,
                                            "weight": "bold"
                                        },
                                        {
                                            "type": "text",
                                            "text": f"{datetime[index]}",
                                            "color": "#B22222",
                                            "size": "sm",
                                            "flex": 5,
                                            "align": "start"
                                        }
                                    ]
                                }
                            ]
                        },
                        {
                            "type": "separator"
                        }
                    ]
                },
                "footer": {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "spacer",
                            "size": "sm"
                        }
                    ],
                    "flex": 0
                }
            }
            self.content_list.append(content)
        self.modle['contents'] = self.content_list
        return self.modle

    def flex_message_sticker(self, stickers, expire_stickers):
        content = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": "https://mcdapp1.azureedge.net/sticker_01.png",
                "size": "full",
                "aspectMode": "cover",
                "action": {
                    "type": "uri",
                    "uri": "http://linecorp.com/"
                }
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "separator"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "margin": "lg",
                        "spacing": "sm",
                        "contents": [
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "您目前擁有的歡樂貼:",
                                        "size": "sm",
                                        "weight": "bold",
                                        "flex": 5
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{stickers}",
                                        "color": "#228B22"
                                    }
                                ]
                            },
                            {
                                "type": "separator"
                            },
                            {
                                "type": "box",
                                "layout": "baseline",
                                "spacing": "sm",
                                "contents": [
                                    {
                                        "type": "text",
                                        "text": "月底即將到期歡樂貼:",
                                        "size": "sm",
                                        "flex": 5,
                                        "weight": "bold"
                                    },
                                    {
                                        "type": "text",
                                        "text": f"{expire_stickers}",
                                        "color": "#B22222"
                                    }
                                ]
                            }
                        ]
                    },
                    {
                        "type": "separator"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "spacer",
                        "size": "sm"
                    }
                ],
                "flex": 0
            }
        }
        return content

    def flex_message_lottery(self,url,type):
        content = {
            "type": "bubble",
            "hero": {
                "type": "image",
                "url": f"{url}",
                "size": "full",
                "aspectMode": "cover"
            },
            "body": {
                "type": "box",
                "layout": "baseline",
                "contents": [
                    {
                        "type": "text",
                        "text": f"抽獎方式：{type}",
                        "size": "sm",
                        "weight": "bold",
                        "align": "center"
                    }
                ]
            }
        }
        return content

    def flex_message_account(self):
        content = {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "text",
                        "text": "新增帳號",
                        "weight": "bold",
                        "size": "xl"
                    }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "點此登入帳號",
                            "uri": "https://liff.line.me/1654329237-W78QE7qk"
                        }
                    },
                    {
                        "type": "spacer",
                        "size": "sm"
                    }
                ],
                "flex": 0
            }
        }
        return content

