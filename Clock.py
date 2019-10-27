from apscheduler.schedulers.blocking import BlockingScheduler
from app import Auto_Coupon_Lottery
sched = BlockingScheduler()

@sched.scheduled_job('cron', hour=0)
def scheduled_job():
    Auto_Coupon_Lottery()

sched.start()




