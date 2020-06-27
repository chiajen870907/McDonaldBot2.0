from apscheduler.schedulers.blocking import BlockingScheduler
from app import auto_lottery

sched = BlockingScheduler()

@sched.scheduled_job('cron', hour=0, minute=5)
def scheduled_job():
    auto_lottery()

sched.start()




