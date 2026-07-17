from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import crud
import schemas
from database import get_db

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/", response_model=List[schemas.PaymentOut])
def list_payments(client_id: Optional[int] = None, db: Session = Depends(get_db)):
    return crud.get_payments(db, client_id=client_id)


@router.post("/", response_model=schemas.PaymentOut, status_code=201)
def create_payment(payment: schemas.PaymentCreate, db: Session = Depends(get_db)):
    return crud.create_payment(db, payment)


@router.patch("/{payment_id}/pay", response_model=schemas.PaymentOut)
def mark_paid(payment_id: int, db: Session = Depends(get_db)):
    p = crud.mark_payment_paid(db, payment_id)
    if not p:
        raise HTTPException(status_code=404, detail="Payment not found")
    return p
