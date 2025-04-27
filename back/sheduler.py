from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import sessionmaker
from back.db.db import engine
from back.db.db import User

Session = sessionmaker(bind=engine)

def reset_energy():
    session = Session()
    try:
        session.query(User).update({User.energy: 100})
        session.commit()
    finally:
        session.close()

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(reset_energy, 'cron', hour=0, minute=0)
    scheduler.start()
