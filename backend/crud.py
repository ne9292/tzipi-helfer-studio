from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_
from datetime import datetime, date, timedelta
from typing import Optional, List
import uuid
import models
import schemas


# --- Clients ---
def get_clients(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False):
    q = db.query(models.Client)
    if active_only:
        q = q.filter(models.Client.active == True)
    return q.offset(skip).limit(limit).all()


def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()


def create_client(db: Session, client: schemas.ClientCreate):
    db_client = models.Client(**client.model_dump(), created_at=datetime.utcnow())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def update_client(db: Session, client_id: int, data: schemas.ClientUpdate):
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_client, field, value)
    db.commit()
    db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int):
    db_client = get_client(db, client_id)
    if db_client:
        db.delete(db_client)
        db.commit()
    return db_client


# --- Sessions ---
def get_sessions(
    db: Session,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    session_type: Optional[models.SessionType] = None,
):
    q = db.query(models.Session)
    if start:
        q = q.filter(models.Session.start_time >= start)
    if end:
        q = q.filter(models.Session.start_time <= end)
    if session_type:
        q = q.filter(models.Session.session_type == session_type)
    return q.order_by(models.Session.start_time).all()


def get_session(db: Session, session_id: int):
    return db.query(models.Session).filter(models.Session.id == session_id).first()


def create_session(db: Session, session: schemas.SessionCreate) -> models.Session:
    data = session.model_dump(exclude={"weeks_ahead"})

    if session.is_recurring:
        group_id = str(uuid.uuid4())
        data["recurrence_group_id"] = group_id
        first = models.Session(**data)
        db.add(first)
        for w in range(1, session.weeks_ahead):
            occurrence = models.Session(
                **{**data, "start_time": session.start_time + timedelta(weeks=w), "reminder_sent": False}
            )
            db.add(occurrence)
        db.commit()
        db.refresh(first)
        return first

    db_session = models.Session(**data)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def update_session(db: Session, session_id: int, data: schemas.SessionUpdate):
    db_session = get_session(db, session_id)
    if not db_session:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(db_session, field, value)
    db.commit()
    db.refresh(db_session)
    return db_session


def delete_session(db: Session, session_id: int):
    db_session = get_session(db, session_id)
    if db_session:
        db.delete(db_session)
        db.commit()
    return db_session


def delete_recurring_series(db: Session, session_id: int):
    """Delete all future sessions in the same recurrence group."""
    s = get_session(db, session_id)
    if not s or not s.recurrence_group_id:
        return 0
    future = db.query(models.Session).filter(
        and_(
            models.Session.recurrence_group_id == s.recurrence_group_id,
            models.Session.start_time >= datetime.utcnow(),
        )
    ).all()
    count = len(future)
    for sess in future:
        db.delete(sess)
    db.commit()
    return count


# --- Registrations ---
def get_registrations_for_session(db: Session, session_id: int):
    return (
        db.query(models.Registration)
        .options(joinedload(models.Registration.client))
        .filter(models.Registration.session_id == session_id)
        .all()
    )


def get_registrations_for_client(db: Session, client_id: int):
    return (
        db.query(models.Registration)
        .options(joinedload(models.Registration.session))
        .filter(models.Registration.client_id == client_id)
        .all()
    )


def register_client(db: Session, reg: schemas.RegistrationCreate):
    session = get_session(db, reg.session_id)
    if not session:
        return None, "session_not_found"

    existing = db.query(models.Registration).filter(
        and_(
            models.Registration.client_id == reg.client_id,
            models.Registration.session_id == reg.session_id,
        )
    ).first()
    if existing:
        return None, "already_registered"

    active_count = db.query(func.count(models.Registration.id)).filter(
        and_(
            models.Registration.session_id == reg.session_id,
            models.Registration.on_waitlist == False,
        )
    ).scalar()

    on_waitlist = active_count >= session.max_capacity

    db_reg = models.Registration(
        client_id=reg.client_id,
        session_id=reg.session_id,
        registered_at=datetime.utcnow(),
        on_waitlist=on_waitlist,
    )
    db.add(db_reg)
    db.flush()

    # שינוי כאן: שליפת הלקוח כדי לקבל את שיטת התשלום המועדפת שלו
    client = get_client(db, reg.client_id)
    preferred_method = client.payment_method if client else None

    # Auto-create pending payment if session has a monthly price
    if not on_waitlist and session.price_per_month and session.price_per_month > 0:
        month_str = datetime.utcnow().strftime('%m/%Y')
        payment = models.Payment(
            client_id=reg.client_id,
            amount=session.price_per_month,
            description=f"מנוי חודשי – {session.title} ({month_str})",
            status=models.PaymentStatus.pending,
            payment_method=preferred_method,  # שיוך שיטת התשלום המועדפת
            created_at=datetime.utcnow(),
        )
        db.add(payment)

    db.commit()
    db.refresh(db_reg)
    return db_reg, "waitlist" if on_waitlist else "ok"


def update_attendance(db: Session, registration_id: int, attended: bool):
    reg = db.query(models.Registration).filter(models.Registration.id == registration_id).first()
    if reg:
        reg.attended = attended
        db.commit()
        db.refresh(reg)
    return reg


def cancel_registration(db: Session, registration_id: int):
    reg = db.query(models.Registration).filter(models.Registration.id == registration_id).first()
    if reg:
        session_id = reg.session_id
        db.delete(reg)
        db.commit()
        _promote_from_waitlist(db, session_id)
    return reg


def _promote_from_waitlist(db: Session, session_id: int):
    session = get_session(db, session_id)
    if not session:
        return
    active_count = db.query(func.count(models.Registration.id)).filter(
        and_(
            models.Registration.session_id == session_id,
            models.Registration.on_waitlist == False,
        )
    ).scalar()

    if active_count < session.max_capacity:
        next_in_line = (
            db.query(models.Registration)
            .filter(
                and_(
                    models.Registration.session_id == session_id,
                    models.Registration.on_waitlist == True,
                )
            )
            .order_by(models.Registration.registered_at)
            .first()
        )
        if next_in_line:
            next_in_line.on_waitlist = False
            db.commit()


# --- Payments ---
def create_payment(db: Session, payment: schemas.PaymentCreate):
    db_payment = models.Payment(**payment.model_dump(), created_at=datetime.utcnow())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


def get_payments(db: Session, client_id: Optional[int] = None):
    q = db.query(models.Payment).options(joinedload(models.Payment.client))
    if client_id:
        q = q.filter(models.Payment.client_id == client_id)
    return q.order_by(models.Payment.created_at.desc()).all()


def charge_session_clients(db: Session, session_id: int) -> int:
    """Create a pending monthly payment for every active registrant of a session."""
    session = get_session(db, session_id)
    if not session or not session.price_per_month or session.price_per_month <= 0:
        return 0
    regs = db.query(models.Registration).filter(
        and_(
            models.Registration.session_id == session_id,
            models.Registration.on_waitlist == False,
        )
    ).all()
    month_str = datetime.utcnow().strftime('%m/%Y')
    count = 0
    for reg in regs:
        # שליפת הלקוח כדי לקבל את שיטת התשלום המועדפת שלו
        client = get_client(db, reg.client_id)
        preferred_method = client.payment_method if client else None

        payment = models.Payment(
            client_id=reg.client_id,
            amount=session.price_per_month,
            description=f"מנוי חודשי – {session.title} ({month_str})",
            status=models.PaymentStatus.pending,
            payment_method=preferred_method,  # שיוך שיטת התשלום המועדפת
            created_at=datetime.utcnow(),
        )
        db.add(payment)
        count += 1
    db.commit()
    return count


def mark_payment_paid(db: Session, payment_id: int):
    p = db.query(models.Payment).filter(models.Payment.id == payment_id).first()
    if p:
        p.status = models.PaymentStatus.paid
        p.paid_at = datetime.utcnow()
        db.commit()
        db.refresh(p)
    return p


# --- Dashboard ---
def get_dashboard_stats(db: Session):
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = today_start.replace(hour=23, minute=59, second=59)

    today_sessions = db.query(func.count(models.Session.id)).filter(
        and_(models.Session.start_time >= today_start, models.Session.start_time <= today_end)
    ).scalar()

    today_clients = (
        db.query(func.count(models.Registration.id))
        .join(models.Session)
        .filter(
            and_(
                models.Session.start_time >= today_start,
                models.Session.start_time <= today_end,
                models.Registration.on_waitlist == False,
            )
        )
        .scalar()
    )

    total_active_clients = db.query(func.count(models.Client.id)).filter(
        models.Client.active == True
    ).scalar()

    month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly_revenue = db.query(func.sum(models.Payment.amount)).filter(
        and_(
            models.Payment.status == models.PaymentStatus.paid,
            models.Payment.paid_at >= month_start,
        )
    ).scalar() or 0.0

    upcoming = (
        db.query(models.Session)
        .filter(models.Session.start_time >= datetime.utcnow())
        .order_by(models.Session.start_time)
        .limit(5)
        .all()
    )

    return {
        "today_sessions": today_sessions,
        "today_clients": today_clients,
        "total_active_clients": total_active_clients,
        "monthly_revenue": monthly_revenue,
        "upcoming_sessions": upcoming,
    }


# --- Reminder helpers ---
def get_sessions_for_tomorrow(db: Session):
    from datetime import timedelta
    tomorrow = datetime.utcnow().date() + timedelta(days=1)
    start = datetime.combine(tomorrow, datetime.min.time())
    end = datetime.combine(tomorrow, datetime.max.time())
    return (
        db.query(models.Session)
        .filter(
            and_(
                models.Session.start_time >= start,
                models.Session.start_time <= end,
                models.Session.reminder_sent == False,
            )
        )
        .all()
    )


def mark_reminder_sent(db: Session, session_id: int):
    s = get_session(db, session_id)
    if s:
        s.reminder_sent = True
        db.commit()


def session_registered_count(db: Session, session_id: int) -> int:
    return db.query(func.count(models.Registration.id)).filter(
        and_(
            models.Registration.session_id == session_id,
            models.Registration.on_waitlist == False,
        )
    ).scalar()
