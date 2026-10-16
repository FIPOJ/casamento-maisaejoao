from fastapi import APIRouter, Depends, HTTPException, Request
from urllib.parse import urlparse
import ipaddress
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Gift, GiftPayment
from app.schemas import CreatePreferenceRequest, CreatePreferenceResponse
from app.services.mercado_pago_service import create_checkout_preference, get_payment


router = APIRouter()

PAYMENT_STATUS_MAP = {
    "approved": "approved",
    "pending": "pending",
    "in_process": "pending",
    "rejected": "rejected",
    "cancelled": "cancelled",
    "refunded": "refunded",
    "charged_back": "refunded",
}


@router.post("/create-preference", response_model=CreatePreferenceResponse)
def create_preference(payload: CreatePreferenceRequest, db: Session = Depends(get_db)):
    gift = db.query(Gift).filter(Gift.id == payload.gift_id, Gift.status != "disabled").first()
    if not gift:
        raise HTTPException(status_code=404, detail="Presente nao encontrado")

    if gift.is_variable_amount:
        if payload.amount is None:
            raise HTTPException(status_code=400, detail="Valor obrigatorio para presente de valor livre")
        amount = round(float(payload.amount), 2)
        if amount < 1:
            raise HTTPException(status_code=400, detail="Valor minimo e R$ 1")
    else:
        amount = round(float(gift.price or 0), 2)
        if amount <= 0:
            raise HTTPException(status_code=400, detail="Presente sem preco valido")

    payment = GiftPayment(
        gift_id=gift.id,
        guest_name=payload.guest_name,
        guest_email=str(payload.guest_email or "Não informado"),
        guest_phone=payload.guest_phone,
        guest_message=payload.guest_message,
        amount=amount,
        status="created",
        external_reference="pending",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)

    payment.external_reference = f"gift_payment_{payment.id}"
    db.commit()
    db.refresh(payment)

    preference_data = {
        "items": [
            {
                "title": f"Presente de casamento - {gift.title}",
                "quantity": 1,
                "unit_price": amount,
                "currency_id": "BRL",
            }
        ],
        "metadata": {
            "gift_id": gift.id,
            "gift_payment_id": payment.id,
            "guest_name": payload.guest_name,
            "guest_message": payload.guest_message,
        },
        "external_reference": payment.external_reference,
    }

    if payload.guest_email:
        preference_data["payer"] = {
            "name": payload.guest_name,
            "email": str(payload.guest_email),
        }

    if not _is_local_url(settings.backend_url):
        preference_data["notification_url"] = f"{settings.backend_url}/api/payments/webhook"

    if not _is_local_url(settings.frontend_url):
        preference_data["back_urls"] = {
            "success": f"{settings.frontend_url}/pagamento/sucesso",
            "failure": f"{settings.frontend_url}/pagamento/falha",
            "pending": f"{settings.frontend_url}/pagamento/pendente",
        }
        preference_data["auto_return"] = "approved"

    preference = create_checkout_preference(preference_data)

    payment.mercado_pago_preference_id = preference.get("id")
    payment.status = "pending"
    db.commit()
    db.refresh(payment)

    init_point = preference.get("init_point")
    sandbox_init_point = preference.get("sandbox_init_point")
    checkout_url = sandbox_init_point if settings.use_sandbox_checkout else init_point

    return {
        "payment_attempt_id": payment.id,
        "preference_id": payment.mercado_pago_preference_id,
        "init_point": init_point,
        "sandbox_init_point": sandbox_init_point,
        "checkout_url": checkout_url,
        "external_reference": payment.external_reference,
    }


@router.post("/webhook")
async def mercado_pago_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    payment_id = _extract_payment_id(payload, dict(request.query_params))

    if not payment_id:
        return {"status": "received"}

    mercado_pago_payment = get_payment(str(payment_id))
    if not mercado_pago_payment:
        return {"status": "received"}

    external_reference = mercado_pago_payment.get("external_reference")
    payment = (
        db.query(GiftPayment)
        .filter(GiftPayment.external_reference == external_reference)
        .first()
    )
    if not payment:
        return {"status": "received"}

    mp_status = mercado_pago_payment.get("status")
    payment.status = PAYMENT_STATUS_MAP.get(mp_status, "unknown")
    payment.mercado_pago_payment_id = str(mercado_pago_payment.get("id") or payment_id)

    payer = mercado_pago_payment.get("payer") or {}
    payer_email = payer.get("email")
    payer_name = " ".join(
        part for part in [payer.get("first_name"), payer.get("last_name")] if part
    ).strip()
    if payer_email:
        payment.guest_email = payer_email
    if payer_name:
        payment.guest_name = payer_name

    gift = db.query(Gift).filter(Gift.id == payment.gift_id).first()
    if gift and payment.status == "approved":
        gift.status = "paid"
    elif gift and gift.status == "payment_started" and payment.status in ["rejected", "cancelled"]:
        gift.status = "available"

    db.commit()
    return {"status": "received"}


def _extract_payment_id(payload: dict, query_params: dict) -> str | None:
    if query_params.get("type") == "payment" and query_params.get("data.id"):
        return query_params["data.id"]

    if query_params.get("topic") == "payment" and query_params.get("id"):
        return query_params["id"]

    data = payload.get("data")
    if isinstance(data, dict) and data.get("id"):
        return str(data["id"])

    if payload.get("type") == "payment" and payload.get("id"):
        return str(payload["id"])

    resource = payload.get("resource")
    if isinstance(resource, str) and "/" in resource:
        return resource.rstrip("/").split("/")[-1]

    return None


def _is_local_url(url: str) -> bool:
    parsed = urlparse(url)
    hostname = parsed.hostname or ""
    if hostname in {"localhost", "127.0.0.1", "0.0.0.0"}:
        return True

    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        return False

    return address.is_private or address.is_loopback or address.is_link_local
