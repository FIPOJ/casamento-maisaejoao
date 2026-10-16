from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class GiftBase(BaseModel):
    title: str = Field(min_length=2, max_length=160)
    subtitle: str | None = Field(default=None, max_length=220)
    description: str = Field(min_length=2)
    image_url: str = Field(min_length=5, max_length=500)
    price: float | None = Field(default=None, ge=0)
    is_variable_amount: bool = False
    sort_order: int = 0


class GiftCreate(GiftBase):
    pass


class GiftRead(GiftBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CreatePreferenceRequest(BaseModel):
    gift_id: int
    guest_name: str = Field(min_length=2, max_length=160)
    guest_email: EmailStr | None = None
    guest_phone: str | None = Field(default=None, max_length=40)
    guest_message: str | None = Field(default=None, max_length=1000)
    amount: float | None = Field(default=None, gt=0)


class CreatePreferenceResponse(BaseModel):
    payment_attempt_id: int
    preference_id: str
    init_point: str | None
    sandbox_init_point: str | None
    checkout_url: str | None
    external_reference: str


class SiteContentRead(BaseModel):
    couple_names: str
    brand_name: str
    logo_url: str | None
    wedding_date: str
    save_the_date_text: str
    hero_image_url: str
    welcome_title: str
    welcome_text: str
    couple_title: str
    couple_text: str
    couple_image_url: str
    couple_image_urls: str | None
    ceremony_title: str
    ceremony_text: str
    ceremony_address: str
    ceremony_maps_url: str
    ceremony_image_url: str
    gifts_title: str
    gifts_text: str
    rsvp_title: str
    rsvp_text: str
    show_rsvp: bool
    dress_code_title: str
    dress_code_text: str
    require_email: bool
    require_phone: bool
    require_message: bool

    class Config:
        from_attributes = True


class RecommendationRead(BaseModel):
    id: int
    title: str
    subtitle: str | None
    image_url: str
    link_url: str | None
    category: str
    sort_order: int
    is_active: bool

    class Config:
        from_attributes = True


class RsvpLookupRequest(BaseModel):
    responsible_name: str = Field(min_length=2, max_length=160)


class RsvpSearchResult(BaseModel):
    id: int
    group_name: str
    responsible_name: str
    masked_phone: str


class RsvpMemberRead(BaseModel):
    id: int
    name: str
    will_attend: bool | None
    note: str | None

    class Config:
        from_attributes = True


class RsvpGroupRead(BaseModel):
    id: int
    group_name: str
    responsible_name: str
    members: list[RsvpMemberRead]

    class Config:
        from_attributes = True


class RsvpValidateRequest(BaseModel):
    group_id: int
    phone_digits: str = Field(min_length=4, max_length=20)


class RsvpMemberUpdate(BaseModel):
    id: int
    will_attend: bool | None = None
    note: str | None = Field(default=None, max_length=500)


class RsvpConfirmRequest(BaseModel):
    group_id: int
    phone_digits: str = Field(min_length=4, max_length=20)
    members: list[RsvpMemberUpdate]
