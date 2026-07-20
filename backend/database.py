import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# אם קיים משתנה סביבה DATABASE_URL (בענן), נשתמש בו. אחרת, נישאר עם SQLite המקומי לפיתוח.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./fitness_studio.db")

# תיקון תאימות נפוץ לכתובות של Supabase ב-SQLAlchemy
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# יצירת מנוע החיבור (בגלל שזה PostgreSQL, לא צריך connect_args של sqlite)
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()