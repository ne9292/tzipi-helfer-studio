"""Seed demo data for testing."""
import sys
sys.path.insert(0, ".")

from database import SessionLocal, Base, engine
from models import Client, Session as Sess, Registration, Payment, SessionType, PaymentStatus
from datetime import datetime, timedelta

Base.metadata.create_all(bind=engine)

db = SessionLocal()

clients_data = [
    Client(first_name="שרה", last_name="כהן", email="sara@example.com", phone="050-1111111", active=True, created_at=datetime.utcnow()),
    Client(first_name="רחל", last_name="לוי", email="rachel@example.com", phone="052-2222222", active=True, created_at=datetime.utcnow()),
    Client(first_name="מרים", last_name="אברהם", email="miriam@example.com", phone="054-3333333", active=True, created_at=datetime.utcnow()),
    Client(first_name="דינה", last_name="פרץ", email="dina@example.com", phone="053-4444444", active=True, created_at=datetime.utcnow()),
    Client(first_name="תמר", last_name="גולן", email="tamar@example.com", phone="058-5555555", active=True, created_at=datetime.utcnow()),
]

for c in clients_data:
    db.add(c)
db.commit()
for c in clients_data:
    db.refresh(c)

now = datetime.utcnow()
today_morning = now.replace(hour=8, minute=0, second=0, microsecond=0)

sessions_data = [
    Sess(title="פילאטיס בוקר", session_type=SessionType.group, start_time=today_morning + timedelta(hours=0), duration_minutes=45, max_capacity=8, location="אולם א׳"),
    Sess(title="יוגה", session_type=SessionType.group, start_time=today_morning + timedelta(hours=2), duration_minutes=45, max_capacity=10, location="אולם ב׳"),
    Sess(title="אימון אישי — שרה", session_type=SessionType.private, start_time=today_morning + timedelta(hours=4), duration_minutes=45, max_capacity=1),
    Sess(title="זומבה", session_type=SessionType.group, start_time=today_morning + timedelta(days=1, hours=1), duration_minutes=45, max_capacity=15, location="אולם גדול"),
    Sess(title="פילאטיס ערב", session_type=SessionType.group, start_time=today_morning + timedelta(days=1, hours=10), duration_minutes=45, max_capacity=8, location="אולם א׳"),
    Sess(title="אימון אישי — רחל", session_type=SessionType.private, start_time=today_morning + timedelta(days=2, hours=3), duration_minutes=45, max_capacity=1),
    Sess(title="קיקבוקסינג", session_type=SessionType.group, start_time=today_morning + timedelta(days=3, hours=2), duration_minutes=45, max_capacity=12, location="אולם ב׳"),
    Sess(title="TRX", session_type=SessionType.group, start_time=today_morning + timedelta(days=4, hours=1), duration_minutes=45, max_capacity=10),
]

for s in sessions_data:
    db.add(s)
db.commit()
for s in sessions_data:
    db.refresh(s)

# Register clients
regs = [
    Registration(client_id=clients_data[0].id, session_id=sessions_data[0].id, registered_at=datetime.utcnow()),
    Registration(client_id=clients_data[1].id, session_id=sessions_data[0].id, registered_at=datetime.utcnow()),
    Registration(client_id=clients_data[2].id, session_id=sessions_data[0].id, registered_at=datetime.utcnow()),
    Registration(client_id=clients_data[0].id, session_id=sessions_data[2].id, registered_at=datetime.utcnow()),
    Registration(client_id=clients_data[3].id, session_id=sessions_data[1].id, registered_at=datetime.utcnow()),
    Registration(client_id=clients_data[4].id, session_id=sessions_data[1].id, registered_at=datetime.utcnow()),
    Registration(client_id=clients_data[1].id, session_id=sessions_data[5].id, registered_at=datetime.utcnow()),
]
for r in regs:
    db.add(r)

# Payments
payments = [
    Payment(client_id=clients_data[0].id, amount=350, description="מנוי חודשי", status=PaymentStatus.paid, paid_at=datetime.utcnow(), created_at=datetime.utcnow()),
    Payment(client_id=clients_data[1].id, amount=350, description="מנוי חודשי", status=PaymentStatus.pending, created_at=datetime.utcnow()),
    Payment(client_id=clients_data[2].id, amount=200, description="10 כניסות", status=PaymentStatus.paid, paid_at=datetime.utcnow(), created_at=datetime.utcnow()),
    Payment(client_id=clients_data[0].id, amount=150, description="אימון אישי", status=PaymentStatus.paid, paid_at=datetime.utcnow(), created_at=datetime.utcnow()),
]
for p in payments:
    db.add(p)

db.commit()
db.close()
print("✓ Demo data seeded successfully!")
