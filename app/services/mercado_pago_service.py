from fastapi import HTTPException
import mercadopago

from app.config import settings


def get_sdk():
    if not settings.mercado_pago_access_token:
        raise HTTPException(status_code=500, detail="MERCADO_PAGO_ACCESS_TOKEN nao configurado")
    return mercadopago.SDK(settings.mercado_pago_access_token)


def create_checkout_preference(preference_data: dict) -> dict:
    result = get_sdk().preference().create(preference_data)
    if result.get("status") not in [200, 201]:
        raise HTTPException(
            status_code=502,
            detail={
                "message": "Erro ao criar preferencia no Mercado Pago",
                "mercado_pago_status": result.get("status"),
                "mercado_pago_response": result.get("response"),
            },
        )
    return result["response"]


def get_payment(payment_id: str) -> dict | None:
    result = get_sdk().payment().get(payment_id)
    if result.get("status") != 200:
        return None
    return result.get("response")

