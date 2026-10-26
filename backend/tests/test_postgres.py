"""Opt-in integration against a dedicated PostgreSQL test database."""
import os
import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from app.database import Base, Guidance
from datetime import date

def test_postgres_roundtrip():
    url = os.getenv('TEST_DATABASE_URL')
    if not url:
        pytest.skip('Configure TEST_DATABASE_URL para executar contra PostgreSQL real.')
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        # Rollback test data; use a separate test database, never production.
        db.add(Guidance(material='teste_integracao', descricao='teste', orientacao='teste', cuidados='teste', fonte='teste', data_atualizacao=date.today()))
        db.flush()
        assert db.scalar(select(Guidance).where(Guidance.material == 'teste_integracao')).fonte == 'teste'
        db.rollback()
    engine.dispose()
