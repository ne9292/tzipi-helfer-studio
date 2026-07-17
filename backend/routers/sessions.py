from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import crud
import schemas
import models
from database import get_db

router = APIRouter(prefix="/sessions", tags=["sessions"])


def _enrich(session: models.Session, db: Session) -> schemas.SessionOut:
    count = crud.session_registered_count(db, session.id)
    out = schemas.SessionOut.model_validate(session)
    out.registered_count = count
    out.available_spots = max(0, session.max_capacity - count)
    return out


@router.get("/", response_model=List[schemas.SessionOut])
def list_sessions(
    start: Optional[datetime] = Query(None),
    end: Optional[datetime] = Query(None),
    session_type: Optional[models.SessionType] = Query(None),
    db: Session = Depends(get_db),
):
    sessions = crud.get_sessions(db, start=start, end=end, session_type=session_type)
    return [_enrich(s, db) for s in sessions]


@router.get("/{session_id}", response_model=schemas.SessionOut)
def get_session(session_id: int, db: Session = Depends(get_db)):
    s = crud.get_session(db, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return _enrich(s, db)


@router.post("/", response_model=schemas.SessionOut, status_code=201)
def create_session(session: schemas.SessionCreate, db: Session = Depends(get_db)):
    s = crud.create_session(db, session)
    return _enrich(s, db)


@router.patch("/{session_id}", response_model=schemas.SessionOut)
def update_session(session_id: int, data: schemas.SessionUpdate, db: Session = Depends(get_db)):
    s = crud.update_session(db, session_id, data)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return _enrich(s, db)


@router.delete("/{session_id}")
def delete_session(session_id: int, db: Session = Depends(get_db)):
    s = crud.delete_session(db, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}


@router.delete("/{session_id}/series")
def delete_series(session_id: int, db: Session = Depends(get_db)):
    """Delete all future occurrences of a recurring series."""
    count = crud.delete_recurring_series(db, session_id)
    if count == 0:
        raise HTTPException(status_code=404, detail="No future sessions found in this series")
    return {"ok": True, "deleted": count}


@router.get("/{session_id}/registrations", response_model=List[schemas.RegistrationOut])
def session_registrations(session_id: int, db: Session = Depends(get_db)):
    return crud.get_registrations_for_session(db, session_id)


@router.post("/{session_id}/charge")
def charge_clients(session_id: int, db: Session = Depends(get_db)):
    """Create pending monthly payments for all active registrants."""
    s = crud.get_session(db, session_id)
    if not s:
        raise HTTPException(status_code=404, detail="Session not found")
    count = crud.charge_session_clients(db, session_id)
    return {"ok": True, "charged": count}
