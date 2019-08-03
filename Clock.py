from apscheduler.schedulers.blocking import BlockingScheduler
from app import McDonald_Lottery

sched = BlockingScheduler()
@sched.Lottery('cron', hour=0)
def Lottery():
    McDonald_Lottery()
sched.start()




