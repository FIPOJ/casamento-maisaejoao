from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Gift(Base):
    __tablename__ = "gifts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), nullable=False)
    subtitle = Column(String(220), nullable=True)
    description = Column(Text, nullable=False)
    image_url = Column(String(500), nullable=False)
    price = Column(Float, nullable=True)
    is_variable_amount = Column(Boolean, default=False, nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    status = Column(String(40), default="available", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    payments = relationship("GiftPayment", back_populates="gift")


class GiftPayment(Base):
    __tablename__ = "gift_payments"

    id = Column(Integer, primary_key=True, index=True)
    gift_id = Column(Integer, ForeignKey("gifts.id"), nullable=False, index=True)
    guest_name = Column(String(160), nullable=False)
    guest_email = Column(String(220), nullable=False)
    guest_phone = Column(String(40), nullable=True)
    guest_message = Column(Text, nullable=True)
    amount = Column(Float, nullable=False)
    status = Column(String(40), default="created", nullable=False)
    mercado_pago_preference_id = Column(String(160), nullable=True, index=True)
    mercado_pago_payment_id = Column(String(160), nullable=True, index=True)
    external_reference = Column(String(160), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    gift = relationship("Gift", back_populates="payments")


class SiteContent(Base):
    __tablename__ = "site_content"

    id = Column(Integer, primary_key=True, default=1)
    couple_names = Column(String(180), default="Casamento Bovi", nullable=False)
    brand_name = Column(String(120), default="M & B", nullable=False)
    logo_url = Column(String(500), nullable=True)
    wedding_date = Column(String(80), default="Save the date", nullable=False)
    save_the_date_text = Column(String(220), default="Celebre esse dia com a gente", nullable=False)
    hero_image_url = Column(String(500), nullable=False)
    welcome_title = Column(String(160), default="Bem-vindos", nullable=False)
    welcome_text = Column(Text, nullable=False)
    couple_title = Column(String(160), default="O casal", nullable=False)
    couple_text = Column(Text, nullable=False)
    couple_image_url = Column(String(500), nullable=False)
    couple_image_urls = Column(Text, nullable=True)
    ceremony_title = Column(String(160), default="Cerimonia", nullable=False)
    ceremony_text = Column(Text, nullable=False)
    ceremony_address = Column(String(260), nullable=False)
    ceremony_maps_url = Column(String(700), nullable=False)
    ceremony_image_url = Column(String(500), nullable=False)
    gifts_title = Column(String(160), default="Lista de presentes", nullable=False)
    gifts_text = Column(Text, nullable=False)
    rsvp_title = Column(String(160), default="Confirmar presenca", nullable=False)
    rsvp_text = Column(Text, nullable=False)
    show_rsvp = Column(Boolean, default=False, nullable=False)
    dress_code_title = Column(String(160), default="Dress code", nullable=False)
    dress_code_text = Column(Text, nullable=False)
    require_email = Column(Boolean, default=True, nullable=False)
    require_phone = Column(Boolean, default=False, nullable=False)
    require_message = Column(Boolean, default=False, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(160), nullable=False)
    subtitle = Column(String(260), nullable=True)
    image_url = Column(String(500), nullable=False)
    link_url = Column(String(700), nullable=True)
    category = Column(String(80), default="Sugestao", nullable=False)
    sort_order = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class GuestGroup(Base):
    __tablename__ = "guest_groups"

    id = Column(Integer, primary_key=True, index=True)
    group_name = Column(String(180), nullable=False)
    responsible_name = Column(String(160), nullable=False)
    phone_number = Column(String(40), nullable=True)
    phone_last_digits = Column(String(8), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    members = relationship("GuestMember", back_populates="group", cascade="all, delete-orphan")


class GuestMember(Base):
    __tablename__ = "guest_members"

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("guest_groups.id"), nullable=False, index=True)
    name = Column(String(160), nullable=False)
    will_attend = Column(Boolean, nullable=True)
    note = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    group = relationship("GuestGroup", back_populates="members")
