from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
import crud
import schemas
from database import get_db

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/", response_model=List[schemas.ClientOut])
def list_clients(active_only: bool = False, db: Session = Depends(get_db)):
    return crud.get_clients(db, active_only=active_only)


@router.get("/{client_id}", response_model=schemas.ClientOut)
def get_client(client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


# FIX 1: תופס IntegrityError (לקוח כפול) ומחזיר 409 במקום 500
@router.post("/", response_model=schemas.ClientOut, status_code=201)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_client(db, client)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Client already exists")


@router.patch("/{client_id}", response_model=schemas.ClientOut)
def update_client(client_id: int, data: schemas.ClientUpdate, db: Session = Depends(get_db)):
    client = crud.update_client(db, client_id, data)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


# FIX 2: מחזיר 204 No Content במקום 200
@router.delete("/{client_id}", status_code=204)
def delete_client(client_id: int, db: Session = Depends(get_db)):
    client = crud.delete_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")


# FIX 3: בודק שהלקוח קיים לפני שליפת registrations
@router.get("/{client_id}/registrations", response_model=List[schemas.RegistrationOut])
def client_registrations(client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return crud.get_registrations_for_client(db, client_id)


# FIX 3 (המשך): בודק שהלקוח קיים לפני שליפת payments
@router.get("/{client_id}/payments", response_model=List[schemas.PaymentOut])
def client_payments(client_id: int, db: Session = Depends(get_db)):
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return crud.get_payments(db, client_id=client_id)