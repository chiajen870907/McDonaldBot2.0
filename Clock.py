# from apscheduler.schedulers.blocking import BlockingScheduler
# from app import McDonald_Lottery
#
# sched = BlockingScheduler()
#
# @sched.scheduled_job('cron', hour=0)
# def scheduled_job():
#     McDonald_Lottery()
# sched.start()

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate('C:/Users\HsiehCJ/Desktop/Project/PyCharm/McDonaldBot/service-account.json')
# 初始化firebase，注意不能重複初始化
firebase_admin.initialize_app(cred)
# 初始化firestore
db = firestore.client()

Count_path = ('Line_User/Counter')
doc_ref = db.document(Count_path)
doc = doc_ref.get()
Count_result = doc.to_dict()

def test(Count_path):
    doc_ref = db.document(Count_path)
    doc = doc_ref.get()
    Count_result = doc.to_dict()
    return Count_result

def test2():
    a = 'Line_User/Counter'
    b = test(a)
    print(b)
test2()






