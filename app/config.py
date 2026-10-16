import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    mercado_pago_access_token: str | None = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")
    mercado_pago_public_key: str | None = os.getenv("MERCADO_PAGO_PUBLIC_KEY")
    backend_url: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./wedding.db")
    use_sandbox_checkout: bool = os.getenv("USE_SANDBOX_CHECKOUT", "true").lower() == "true"
    admin_password: str = os.getenv("ADMIN_PASSWORD", "admin123")


settings = Settings()
