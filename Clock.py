from apscheduler.schedulers.blocking import BlockingScheduler
from app import Auto_Coupon_Lottery
from app import Auto_Sticker_Lottery

sched = BlockingScheduler()
@sched.scheduled_job('cron', hour=0, minute=5)
def scheduled_job():
    Auto_Coupon_Lottery()
    Auto_Sticker_Lottery()


sched.start()




