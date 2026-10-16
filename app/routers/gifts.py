from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Gift
from app.schemas import GiftCreate, GiftRead


router = APIRouter()


@router.get("", response_model=list[GiftRead])
def list_gifts(db: Session = Depends(get_db)):
    return (
        db.query(Gift)
        .filter(Gift.status != "disabled")
        .order_by(Gift.sort_order.asc(), Gift.id.asc())
        .all()
    )


@router.post("", response_model=GiftRead, status_code=201)
def create_gift(payload: GiftCreate, db: Session = Depends(get_db)):
    if payload.is_variable_amount:
        price = None
    elif payload.price is None or payload.price <= 0:
        raise HTTPException(status_code=400, detail="Preco obrigatorio para presente de valor fixo")
    else:
        price = payload.price

    gift = Gift(
        title=payload.title,
        subtitle=payload.subtitle,
        description=payload.description,
        image_url=payload.image_url,
        price=price,
        is_variable_amount=payload.is_variable_amount,
        sort_order=payload.sort_order,
    )
    db.add(gift)
    db.commit()
    db.refresh(gift)
    return gift
