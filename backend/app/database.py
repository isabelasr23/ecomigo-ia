from datetime import date
from sqlalchemy import Date, String, Text, create_engine, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from .config import settings

class Base(DeclarativeBase):
    pass

class Guidance(Base):
    __tablename__ = 'orientacoes'
    id: Mapped[int] = mapped_column(primary_key=True)
    material: Mapped[str] = mapped_column(String(30), unique=True)
    descricao: Mapped[str] = mapped_column(Text)
    orientacao: Mapped[str] = mapped_column(Text)
    cuidados: Mapped[str] = mapped_column(Text)
    fonte: Mapped[str] = mapped_column(Text)
    data_atualizacao: Mapped[date] = mapped_column(Date)

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(engine)

SEEDS = [
    ('papel', 'Papel e papelão', 'Separe papel e papelão secos e consulte a coleta seletiva local.', 'Papéis engordurados, revestidos ou contaminados exigem avaliação específica.'),
    ('plastico', 'Plástico', 'Separe embalagens plásticas sem resíduos e verifique os tipos aceitos na coleta local.', 'A aparência não confirma a resina nem a reciclabilidade. Embalagens de produtos perigosos exigem destinação específica.'),
    ('metal', 'Metal', 'Separe embalagens metálicas vazias e consulte a coleta seletiva local.', 'Não perfure aerossóis nem manipule embalagens pressurizadas. Pilhas e eletrônicos exigem coleta específica.'),
    ('vidro', 'Vidro', 'Consulte a coleta local sobre o recebimento de garrafas e potes de vidro.', 'Não manuseie cacos diretamente. Espelhos, lâmpadas, cerâmica e vidros especiais exigem orientação específica.'),
]

def initialize_database():
    Base.metadata.create_all(engine)
    with SessionLocal.begin() as db:
        for material, descricao, orientacao, cuidados in SEEDS:
            if not db.scalar(select(Guidance).where(Guidance.material == material)):
                db.add(Guidance(material=material, descricao=descricao, orientacao=orientacao, cuidados=cuidados,
                    fonte='Base acadêmica Ecomigo — orientação geral provisória, pendente de validação local',
                    data_atualizacao=date(2026, 10, 15)))

def get_db():
    with SessionLocal() as db:
        yield db
