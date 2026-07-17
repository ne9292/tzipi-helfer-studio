from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
# ייבוא סוגי ה-Enum המעודכנים מתוך models
from models import SessionType, PaymentStatus, PaymentMethod


# --- Client ---
class ClientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    notes: Optional[str] = None
    active: bool = True
    # הוספת שיטת תשלום כברירת מחדל
    payment_method: Optional[PaymentMethod] = PaymentMethod.CASH


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    active: Optional[bool] = None
    payment_method: Optional[PaymentMethod] = None


class ClientOut(ClientBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# --- Session ---
class SessionBase(BaseModel):
    title: str
    session_type: SessionType
    start_time: datetime
    duration_minutes: int = 45
    max_capacity: int = 10
    location: Optional[str] = None
    notes: Optional[str] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    recurrence_group_id: Optional[str] = None
    price_per_month: float = 0.0


class SessionCreate(SessionBase):
    # When is_recurring=True, pass weeks_ahead to generate N weeks
    weeks_ahead: int = 52


class SessionUpdate(BaseModel):
    title: Optional[str] = None
    session_type: Optional[SessionType] = None
    start_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    max_capacity: Optional[int] = None
    location: Optional[str] = None
    notes: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    price_per_month: Optional[float] = None


class SessionOut(SessionBase):
    id: int
    reminder_sent: bool
    registered_count: int = 0
    available_spots: int = 0

    class Config:
        from_attributes = True


# --- Registration ---
class RegistrationCreate(BaseModel):
    client_id: int
    session_id: int


class RegistrationOut(BaseModel):
    id: int
    client_id: int
    session_id: int
    registered_at: Optional[datetime] = None
    attended: Optional[bool] = None
    on_waitlist: bool

    client: Optional[ClientOut] = None
    session: Optional[SessionOut] = None

    class Config:
        from_attributes = True


class AttendanceUpdate(BaseModel):
    attended: bool


# --- Payment ---
class PaymentCreate(BaseModel):
    client_id: int
    amount: float
    description: Optional[str] = None
    status: PaymentStatus = PaymentStatus.pending
    # הוספת אפשרות להגדיר שיטת תשלום בעת יצירת תשלום חדש
    payment_method: Optional[PaymentMethod] = None


class PaymentOut(BaseModel):
    id: int
    client_id: int
    amount: float
    status: PaymentStatus
    payment_method: Optional[PaymentMethod] = None # הוספה לפלט של ה-API
    description: Optional[str] = None
    paid_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    client: Optional[ClientOut] = None

    class Config:
        from_attributes = True


# --- Dashboard ---
class DashboardStats(BaseModel):
    today_sessions: int
    today_clients: int
    total_active_clients: int
    monthly_revenue: float
    upcoming_sessions: List[SessionOut]