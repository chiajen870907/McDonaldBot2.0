from apscheduler.schedulers.blocking import BlockingScheduler
from app import McDonald_Lottery

def Lottery():
    McDonald_Lottery()

sched = BlockingScheduler()
sched.add_job(Lottery, 'interval', seconds=5)
sched.start()



