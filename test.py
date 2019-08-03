# import re
# PushID = " { 'UserID' : 'UEAXSSID USERID1 UserID11'} "
# PushID = re.sub("[{} \' :]", "", str(PushID))
# PushID = PushID.replace('UserID','')
# print(PushID)
def McDonald_Lottery():
    print('f')
from apscheduler.schedulers.blocking import BlockingScheduler
scheduler = BlockingScheduler()
# 添加任务并设置触发方式为3s一次
scheduler.add_job(McDonald_Lottery, 'interval', minutes=1)
# 开始运行调度器
scheduler.start()