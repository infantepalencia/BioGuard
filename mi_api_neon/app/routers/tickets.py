from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(prefix="/tickets", tags=["Soporte"])

@router.post("/", response_model=schemas.TicketResponse)
def crear_ticket(ticket: schemas.TicketCreate, db: Session = Depends(database.get_db)):
    nuevo = models.TicketSoporte(**ticket.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo