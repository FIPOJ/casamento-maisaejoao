from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GuestGroup, GuestMember, Recommendation, SiteContent
from app.schemas import (
    RecommendationRead,
    RsvpConfirmRequest,
    RsvpGroupRead,
    RsvpLookupRequest,
    RsvpSearchResult,
    RsvpValidateRequest,
    SiteContentRead,
)


router = APIRouter()


@router.get("/site", response_model=SiteContentRead)
def get_site_content(db: Session = Depends(get_db)):
    return db.query(SiteContent).filter(SiteContent.id == 1).first()


@router.get("/recommendations", response_model=list[RecommendationRead])
def list_recommendations(db: Session = Depends(get_db)):
    return (
        db.query(Recommendation)
        .filter(Recommendation.is_active == True)
        .order_by(Recommendation.sort_order.asc(), Recommendation.id.asc())
        .all()
    )


@router.post("/rsvp/search", response_model=list[RsvpSearchResult])
def lookup_rsvp(payload: RsvpLookupRequest, db: Session = Depends(get_db)):
    query = payload.responsible_name.strip()
    groups = (
        db.query(GuestGroup)
        .filter(
            (GuestGroup.responsible_name.ilike(f"%{query}%"))
            | (GuestGroup.group_name.ilike(f"%{query}%"))
            | (GuestGroup.members.any(GuestMember.name.ilike(f"%{query}%")))
        )
        .order_by(GuestGroup.group_name.asc())
        .limit(8)
        .all()
    )

    return [
        {
            "id": item.id,
            "group_name": item.group_name,
            "responsible_name": item.responsible_name,
            "masked_phone": _mask_phone(item.phone_number or item.phone_last_digits),
        }
        for item in groups
    ]


@router.post("/guests/search")
def search_gift_guests(payload: RsvpLookupRequest, db: Session = Depends(get_db)):
    query = payload.responsible_name.strip()
    groups = (
        db.query(GuestGroup)
        .filter(
            (GuestGroup.responsible_name.ilike(f"%{query}%"))
            | (GuestGroup.group_name.ilike(f"%{query}%"))
            | (GuestGroup.members.any(GuestMember.name.ilike(f"%{query}%")))
        )
        .order_by(GuestGroup.group_name.asc())
        .limit(8)
        .all()
    )

    return [
        {
            "id": group.id,
            "group_name": group.group_name,
            "responsible_name": group.responsible_name,
            "members": [
                {"id": member.id, "name": member.name}
                for member in group.members
            ],
        }
        for group in groups
    ]


@router.post("/rsvp/validate", response_model=RsvpGroupRead)
def validate_rsvp(payload: RsvpValidateRequest, db: Session = Depends(get_db)):
    group = db.query(GuestGroup).filter(GuestGroup.id == payload.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grupo nao encontrado")

    if not _phone_matches(group, payload.phone_digits):
        raise HTTPException(status_code=403, detail="Telefone nao confere")

    return group


@router.post("/rsvp/confirm", response_model=RsvpGroupRead)
def confirm_rsvp(payload: RsvpConfirmRequest, db: Session = Depends(get_db)):
    group = db.query(GuestGroup).filter(GuestGroup.id == payload.group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Grupo nao encontrado")

    if not _phone_matches(group, payload.phone_digits):
        raise HTTPException(status_code=403, detail="Validacao do telefone falhou")

    updates = {member.id: member for member in payload.members}
    members = db.query(GuestMember).filter(GuestMember.group_id == group.id).all()
    for member in members:
        if member.id in updates:
            member.will_attend = updates[member.id].will_attend
            member.note = updates[member.id].note

    db.commit()
    db.refresh(group)
    return group


def _only_digits(value: str) -> str:
    return "".join(char for char in value if char.isdigit())


def _phone_matches(group: GuestGroup, value: str) -> bool:
    typed = _only_digits(value)
    full_phone = _only_digits(group.phone_number or "")
    last_digits = _only_digits(group.phone_last_digits)

    if full_phone and typed == full_phone:
        return True
    return len(typed) >= 4 and last_digits and typed.endswith(last_digits)


def _mask_phone(value: str) -> str:
    digits = _only_digits(value)
    if len(digits) >= 10:
        visible = digits[:-4]
        hidden = "*" * 4
        if len(digits) == 11:
            return f"({visible[:2]}) {visible[2:7]}-{hidden}"
        if len(digits) == 10:
            return f"({visible[:2]}) {visible[2:6]}-{hidden}"
        return f"{visible}{hidden}"
    if len(digits) >= 4:
        return "*****-****"
    return "Telefone cadastrado"
