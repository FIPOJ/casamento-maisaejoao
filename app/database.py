from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings


connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models import Gift, GuestGroup, GuestMember, Recommendation, SiteContent

    Base.metadata.create_all(bind=engine)
    _ensure_sqlite_columns()

    db = SessionLocal()
    try:
        if db.query(SiteContent).count() == 0:
            db.add(
                SiteContent(
                    id=1,
                    couple_names="Maisa & João",
                    brand_name="M & B",
                    logo_url=None,
                    wedding_date="31 de outubro de 2026",
                    save_the_date_text="Save the date",
                    hero_image_url="https://images.unsplash.com/photo-1523438885200-e635ba2c371e?auto=format&fit=crop&w=1800&q=84",
                    welcome_title="Bem-vindos ao nosso casamento",
                    welcome_text="",
                    couple_title="Maisa & João",
                    couple_text="Há histórias que começam com grandes aventuras. A nossa começou com a descoberta de que era muito mais divertido enfrentar o mundo lado a lado.\n\nAgora chegou a hora de começar um dos capítulos mais importantes: o nosso casamento.\n\nE nenhuma boa aventura se faz sozinha. Por isso, será uma alegria ter você ao nosso lado nessa celebração.",
                    couple_image_url="https://images.unsplash.com/photo-1520854221256-17451cc331bf?auto=format&fit=crop&w=1200&q=84",
                    couple_image_urls="https://images.unsplash.com/photo-1520854221256-17451cc331bf?auto=format&fit=crop&w=1200&q=84",
                    ceremony_title="Cerimônia & Baile",
                    ceremony_text="Nossa cerimônia será celebrada a céu aberto no Castelo Mondini, com aquele clima de uma pequena vila saída de um conto.\n\nDepois da cerimônia, as portas do salão de festas estarão abertas para o jantar e o baile. É lá que a celebração continua, com boa comida, música, brindes e, esperamos, algumas histórias que mereçam ser contadas no dia seguinte.",
                    ceremony_address="Via Vêneto, 1500 - Guaricanas, Ascurra - SC, 89138-000",
                    ceremony_maps_url="https://maps.app.goo.gl/KmrKT1cq5PyvpFim6",
                    ceremony_image_url="https://images.unsplash.com/photo-1519225421980-715cb0215aed?auto=format&fit=crop&w=1200&q=84",
                    gifts_title="Lista de presentes",
                    gifts_text="Sua presença já é um presente. Mas, para aqueles que quiserem nos ajudar com as próximas aventuras, preparamos algumas opções. Toda contribuição será muito bem-vinda.",
                    rsvp_title="Confirme sua presença!",
                    rsvp_text="Pesquise pelo nome do responsável e valide com os últimos dígitos do telefone para confirmar quem irá participar.",
                    show_rsvp=False,
                    dress_code_title="Dress code",
                    dress_code_text="Traje social leve. Sugerimos tons suaves e elegantes para acompanhar o clima da celebração.",
                )
            )
        else:
            site = db.query(SiteContent).filter(SiteContent.id == 1).first()
            if site and site.couple_names in {"Julia & Fabio", "Casamento Bovi", "Maisa & Bovi"}:
                site.couple_names = "Maisa & João"
            if site and site.wedding_date == "20 de setembro de 2026":
                site.wedding_date = "31 de outubro de 2026"
            if site and (not site.welcome_text or "Criamos este espaco" in site.welcome_text):
                site.welcome_text = ""
            if site and site.couple_title == "O casal":
                site.couple_title = "Maisa & João"
            if site and (not site.couple_text or "Entre encontros" in site.couple_text):
                site.couple_text = "Há histórias que começam com grandes aventuras. A nossa começou com a descoberta de que era muito mais divertido enfrentar o mundo lado a lado.\n\nAgora chegou a hora de começar um dos capítulos mais importantes: o nosso casamento.\n\nE nenhuma boa aventura se faz sozinha. Por isso, será uma alegria ter você ao nosso lado nessa celebração."
            if site and site.ceremony_title == "Cerimonia":
                site.ceremony_title = "Cerimônia & Baile"
            if site and (not site.ceremony_text or "A cerimonia sera" in site.ceremony_text):
                site.ceremony_text = "Nossa cerimônia será celebrada a céu aberto no Castelo Mondini, com aquele clima de uma pequena vila saída de um conto.\n\nDepois da cerimônia, as portas do salão de festas estarão abertas para o jantar e o baile. É lá que a celebração continua, com boa comida, música, brindes e, esperamos, algumas histórias que mereçam ser contadas no dia seguinte."
            if site and site.ceremony_address == "Endereco da cerimonia, cidade - UF":
                site.ceremony_address = "Via Vêneto, 1500 - Guaricanas, Ascurra - SC, 89138-000"
            if site and site.ceremony_maps_url == "https://maps.google.com":
                site.ceremony_maps_url = "https://maps.app.goo.gl/KmrKT1cq5PyvpFim6"
            if site and (not site.gifts_text or "Sua presenca ja" in site.gifts_text):
                site.gifts_text = "Sua presença já é um presente. Mas, para aqueles que quiserem nos ajudar com as próximas aventuras, preparamos algumas opções. Toda contribuição será muito bem-vinda."
            if site and site.rsvp_title == "Confirmar presenca":
                site.rsvp_title = "Confirme sua presença!"
            if site and "responsavel e valide com os ultimos digitos" in (site.rsvp_text or ""):
                site.rsvp_text = "Pesquise pelo nome do responsável e valide com os últimos dígitos do telefone para confirmar quem irá participar."
            if site and "clima da celebracao" in (site.dress_code_text or ""):
                site.dress_code_text = "Traje social leve. Sugerimos tons suaves e elegantes para acompanhar o clima da celebração."
            if site and not site.brand_name:
                site.brand_name = "M & B"

        if db.query(Gift).count() == 0:
            db.add_all(
                [
                    Gift(
                        title="Jogo de panelas",
                        subtitle="Para o novo lar",
                        description="Ajude os noivos a equipar a cozinha para os primeiros almocos em casa.",
                        image_url="https://images.unsplash.com/photo-1556911220-bff31c812dba?auto=format&fit=crop&w=900&q=80",
                        price=250.00,
                        is_variable_amount=False,
                        sort_order=1,
                    ),
                    Gift(
                        title="Cota lua de mel",
                        subtitle="Contribuição livre",
                        description="Contribua com qualquer valor para uma viagem cheia de boas lembranças.",
                        image_url="https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=900&q=80",
                        price=None,
                        is_variable_amount=True,
                        sort_order=2,
                    ),
                    Gift(
                        title="Jantar romantico",
                        subtitle="Depois do grande dia",
                        description="Uma noite especial para celebrar depois da festa.",
                        image_url="https://images.unsplash.com/photo-1414235077428-338989a2e8c0?auto=format&fit=crop&w=900&q=80",
                        price=180.00,
                        is_variable_amount=False,
                        sort_order=3,
                    ),
                ]
            )

        if db.query(Recommendation).count() == 0:
            db.add_all(
                [
                    Recommendation(
                        title="Hotel Gran Santa Catarina - Indaial",
                        subtitle="Com café da manhã incluso e estacionamento no local, fica a 30 minutos (27Km) do Castelo Mondini. Ao fazer a reserva, mencione que são convidados(as) da Maisa e do João, casal que se casará no dia 31/10",
                        category="Hospedagem",
                        image_url="https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=900&q=80",
                        link_url="https://maps.google.com",
                        sort_order=1,
                    ),
                ]
            )
        else:
            for gift in db.query(Gift).all():
                if gift.subtitle == "Contribuicao livre":
                    gift.subtitle = "Contribuição livre"
                if gift.description == "Ajude os noivos a equipar a cozinha para os primeiros almocos em casa.":
                    gift.description = "Ajude os noivos a equipar a cozinha para os primeiros almoços em casa."
                if gift.description == "Contribua com qualquer valor para uma viagem cheia de boas lembrancas.":
                    gift.description = "Contribua com qualquer valor para uma viagem cheia de boas lembranças."
                if gift.title == "Jantar romantico":
                    gift.title = "Jantar romântico"
            db.query(Recommendation).filter(Recommendation.title == "Transporte e chegada").delete(synchronize_session=False)
            hotel = db.query(Recommendation).filter(Recommendation.title.in_(["Hotel recomendado", "Hotel Gran Santa Catarina - Indaial"])).first()
            if hotel:
                hotel.title = "Hotel Gran Santa Catarina - Indaial"
                hotel.subtitle = "Com café da manhã incluso e estacionamento no local, fica a 30 minutos (27Km) do Castelo Mondini. Ao fazer a reserva, mencione que são convidados(as) da Maisa e do João, casal que se casará no dia 31/10"

        if db.query(GuestGroup).count() == 0:
            group = GuestGroup(
                group_name="Familia Exemplo",
                responsible_name="Fabio Exemplo",
                phone_number="47999991234",
                phone_last_digits="1234",
                notes="Grupo inicial para demonstracao.",
            )
            group.members = [
                GuestMember(name="Fabio Exemplo"),
                GuestMember(name="Juliana Exemplo"),
            ]
            db.add(group)
        else:
            demo_group = db.query(GuestGroup).filter(GuestGroup.group_name == "Familia Exemplo").first()
            if demo_group and _digits(demo_group.phone_number or "") in {"", "1234"}:
                demo_group.phone_number = "47999991234"
                demo_group.phone_last_digits = "1234"

        db.commit()
    finally:
        db.close()


def _ensure_sqlite_columns():
    if not settings.database_url.startswith("sqlite"):
        return

    with engine.begin() as conn:
        gift_columns = {row[1] for row in conn.execute(text("PRAGMA table_info(gifts)"))}
        if "subtitle" not in gift_columns:
            conn.execute(text("ALTER TABLE gifts ADD COLUMN subtitle VARCHAR(220)"))
        if "sort_order" not in gift_columns:
            conn.execute(text("ALTER TABLE gifts ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0"))

        group_columns = {row[1] for row in conn.execute(text("PRAGMA table_info(guest_groups)"))}
        if "phone_number" not in group_columns:
            conn.execute(text("ALTER TABLE guest_groups ADD COLUMN phone_number VARCHAR(40)"))
            conn.execute(text("UPDATE guest_groups SET phone_number = phone_last_digits WHERE phone_number IS NULL"))

        site_columns = {row[1] for row in conn.execute(text("PRAGMA table_info(site_content)"))}
        if "brand_name" not in site_columns:
            conn.execute(text("ALTER TABLE site_content ADD COLUMN brand_name VARCHAR(120) NOT NULL DEFAULT 'M & B'"))
        if "logo_url" not in site_columns:
            conn.execute(text("ALTER TABLE site_content ADD COLUMN logo_url VARCHAR(500)"))
        if "couple_image_urls" not in site_columns:
            conn.execute(text("ALTER TABLE site_content ADD COLUMN couple_image_urls TEXT"))
            conn.execute(text("UPDATE site_content SET couple_image_urls = couple_image_url WHERE couple_image_urls IS NULL"))
        if "show_rsvp" not in site_columns:
            conn.execute(text("ALTER TABLE site_content ADD COLUMN show_rsvp BOOLEAN NOT NULL DEFAULT 0"))


def _digits(value: str) -> str:
    return "".join(char for char in value if char.isdigit())
