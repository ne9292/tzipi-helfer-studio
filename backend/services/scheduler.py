from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import SessionLocal
import crud
from services.email_service import send_reminder_email

scheduler = BackgroundScheduler(timezone="Asia/Jerusalem")


def send_nightly_reminders():
    db = SessionLocal()
    try:
        sessions = crud.get_sessions_for_tomorrow(db)
        for session in sessions:
            registrations = crud.get_registrations_for_session(db, session.id)
            active = [r for r in registrations if not r.on_waitlist]
            for reg in active:
                if reg.client and reg.client.email:
                    send_reminder_email(
                        to_email=reg.client.email,
                        client_name=f"{reg.client.first_name} {reg.client.last_name}",
                        session_title=session.title,
                        start_time=session.start_time,
                        location=session.location or "",
                    )
            crud.mark_reminder_sent(db, session.id)
            print(f"[SCHEDULER] Reminders sent for session {session.id} ({session.title})")
    finally:
        db.close()


def start_scheduler():
    # Run every night at 20:00 Israel time
    scheduler.add_job(
        send_nightly_reminders,
        CronTrigger(hour=22, minute=43, timezone="Asia/Jerusalem"),
        id="nightly_reminders",
        replace_existing=True,
    )
    scheduler.start()
    print("[SCHEDULER] Started — nightly reminders at 22:43 IL")


def stop_scheduler():
    scheduler.shutdown()
