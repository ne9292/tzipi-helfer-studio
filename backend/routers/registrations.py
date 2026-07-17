from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import crud
import schemas
from database import get_db

router = APIRouter(prefix="/registrations", tags=["registrations"])


@router.post("/", response_model=schemas.RegistrationOut, status_code=201)
def register(reg: schemas.RegistrationCreate, db: Session = Depends(get_db)):
    result, status = crud.register_client(db, reg)
    if status == "session_not_found":
        raise HTTPException(status_code=404, detail="Session not found")
    if status == "already_registered":
        raise HTTPException(status_code=409, detail="Client already registered")
    return result


@router.patch("/{registration_id}/attendance", response_model=schemas.RegistrationOut)
def mark_attendance(
    registration_id: int, data: schemas.AttendanceUpdate, db: Session = Depends(get_db)
):
    reg = crud.update_attendance(db, registration_id, data.attended)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    return reg


@router.delete("/{registration_id}")
def cancel_registration(registration_id: int, db: Session = Depends(get_db)):
    reg = crud.cancel_registration(db, registration_id)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    return {"ok": True}
