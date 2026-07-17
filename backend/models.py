from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Enum, Text, Float
from sqlalchemy.orm import relationship
from database import Base
import enum


class SessionType(str, enum.Enum):
    group = "group"
    private = "private"


class PaymentStatus(str, enum.Enum):
    paid = "paid"
    pending = "pending"
    partial = "partial"


# הוספת Enum לשיטות התשלום בשרת
class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    TRANSFER = "TRANSFER"
    STANDING_ORDER = "STANDING_ORDER"


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(200), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    notes = Column(Text)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime)
    
    # סנכרון שדה שיטת התשלום מול האנגולר
    payment_method = Column(Enum(PaymentMethod), default=PaymentMethod.CASH)

    # תיקון המחיקה: הוספת cascade="all, delete-orphan"
    registrations = relationship("Registration", back_populates="client", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="client", cascade="all, delete-orphan")


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    session_type = Column(Enum(SessionType), nullable=False)
    start_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=45)
    max_capacity = Column(Integer, default=10)
    location = Column(String(200))
    notes = Column(Text)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(200))
    recurrence_group_id = Column(String(36), index=True)
    reminder_sent = Column(Boolean, default=False)
    price_per_month = Column(Float, default=0.0)

    registrations = relationship("Registration", back_populates="session", cascade="all, delete-orphan")


class Registration(Base):
    __tablename__ = "registrations"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    registered_at = Column(DateTime)
    attended = Column(Boolean, default=None)
    on_waitlist = Column(Boolean, default=False)

    client = relationship("Client", back_populates="registrations")
    session = relationship("Session", back_populates="registrations")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.pending)
    payment_method = Column(Enum(PaymentMethod), nullable=True) # תיעוד שיטת התשלום בפועל
    description = Column(String(300))
    paid_at = Column(DateTime)
    created_at = Column(DateTime)

    client = relationship("Client", back_populates="payments")