import io
import os
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy import create_engine, delete
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

# SQLite only for isolated tests; production defaults to PostgreSQL.
os.environ['DATABASE_URL'] = 'sqlite://'
from app import database, main
from app.config import settings

@pytest.fixture(autouse=True)
def use_openai_adapter(monkeypatch):
    monkeypatch.setattr(settings, 'ai_provider', 'openai')
from app.schemas import Identification
from app.services import vision

@pytest.fixture
def client(monkeypatch):
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    factory = sessionmaker(engine)
    monkeypatch.setattr(database, 'engine', engine)
    monkeypatch.setattr(database, 'SessionLocal', factory)
    def override():
        with factory() as db:
            yield db
    main.app.dependency_overrides[database.get_db] = override
    monkeypatch.setattr(main, 'identify', AsyncMock(return_value=Identification(objeto='Garrafa', material='plastico', identificacao_inconclusiva=False, observacao='Possível plástico; a aparência não confirma a composição.')))
    with TestClient(main.app) as c:
        yield c, factory
    main.app.dependency_overrides.clear()
    engine.dispose()

def photo(fmt='PNG'):
    out = io.BytesIO()
    Image.new('RGB', (20, 20), 'green').save(out, format=fmt)
    return out.getvalue()

def post(c, data=None, mime='image/png'):
    return c.post('/api/analises', files={'imagem': ('foto.png', photo() if data is None else data, mime)})

@pytest.mark.parametrize('fmt,mime', [('PNG','image/png'), ('JPEG','image/jpeg')])
def test_valid_upload_and_database(client, fmt, mime):
    c, _ = client
    response = post(c, photo(fmt), mime)
    assert response.status_code == 200
    body = response.json()
    assert body['material'] == 'plastico'
    assert body['orientacao'] and 'provisória' in body['fonte_orientacao']
    assert 'confidence' not in body

@pytest.mark.parametrize('data,mime,status', [(b'','image/png',400), (b'x'*(5*1024*1024+1),'image/png',413), (b'not an image','image/png',415), (b'text','text/plain',415)])
def test_invalid_upload(client, data, mime, status):
    c, _ = client
    assert post(c, data, mime).status_code == status
    main.identify.assert_not_called()

def test_mime_mismatch(client):
    c, _ = client
    assert post(c, photo('JPEG'), 'image/png').status_code == 415

def test_inconclusive(client):
    c, _ = client
    main.identify.return_value = Identification(objeto='Embalagem', material='misto', identificacao_inconclusiva=False, observacao='Múltiplas camadas visíveis.')
    body = post(c).json()
    assert body['identificacao_inconclusiva'] is True
    assert body['orientacao'] is None

def test_uncertain_known_material_has_no_guidance(client):
    c, _ = client
    main.identify.return_value.identificacao_inconclusiva = True
    assert post(c).json()['orientacao'] is None

def test_service_unavailable(client):
    c, _ = client
    main.identify.side_effect = HTTPException(502, 'IA indisponível')
    assert post(c).status_code == 502

def test_missing_guidance(client):
    c, factory = client
    with factory.begin() as db:
        db.execute(delete(database.Guidance))
    response = post(c)
    assert response.status_code == 200
    assert response.json()['orientacao'] is None

def test_seed_idempotent_and_health(client):
    c, factory = client
    database.initialize_database()
    with factory() as db:
        assert len(db.query(database.Guidance).all()) == 4
    assert c.get('/api/health').json()['database'] == 'connected'

def test_whole_body_limit(client):
    c, _ = client
    assert post(c, b'x'*(6*1024*1024)).status_code == 413

# Test actual adapter with a controlled HTTP boundary; no external model is invoked.
@pytest.mark.parametrize('mode,status', [('valid',200),('invalid',502),('refusal',502),('timeout',504),('http_error',502),('incomplete',502)])
def test_adapter(monkeypatch, mode, status):
    import asyncio
    monkeypatch.setattr(settings, 'openai_api_key', 'test-only')
    async def fake_post(self, url, **kwargs):
        assert url == 'https://api.openai.com/v1/responses'
        assert kwargs['json']['store'] is False
        assert kwargs['json']['text']['format']['strict'] is True
        assert kwargs['json']['input'][0]['content'][1]['image_url'].startswith('data:image/jpeg;base64,')
        if mode == 'timeout':
            raise httpx.ReadTimeout('test')
        text = '{"objeto":"Garrafa","material":"plastico","identificacao_inconclusiva":false,"observacao":"Estimativa visual"}' if mode == 'valid' else '{}'
        return httpx.Response(503 if mode == 'http_error' else 200, request=httpx.Request('POST', url), json={
            'status': 'incomplete' if mode == 'incomplete' else 'completed',
            'output': [{'type':'message','content':[{'type':'refusal','refusal':'test'}] if mode == 'refusal' else [{'type':'output_text','text':text}]}]})
    monkeypatch.setattr(httpx.AsyncClient, 'post', fake_post)
    if status == 200:
        assert asyncio.run(vision.identify(photo())).material == 'plastico'
    else:
        with pytest.raises(HTTPException) as exc:
            asyncio.run(vision.identify(photo()))
        assert exc.value.status_code == status

def test_missing_key(monkeypatch):
    import asyncio
    monkeypatch.setattr(settings, 'openai_api_key', '')
    with pytest.raises(HTTPException) as exc:
        asyncio.run(vision.identify(photo()))
    assert exc.value.status_code == 503

@pytest.mark.parametrize('payload', [[], None, {'status': 'completed', 'output': None},
    {'status': 'completed', 'output': [{'type': 'message', 'content': None}]},
    {'status': 'completed', 'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': 42}]}]}])
def test_malformed_provider_payload(monkeypatch, payload):
    import asyncio
    monkeypatch.setattr(settings, 'openai_api_key', 'test-only')
    async def fake_post(self, url, **kwargs):
        return httpx.Response(200, request=httpx.Request('POST', url), json=payload)
    monkeypatch.setattr(httpx.AsyncClient, 'post', fake_post)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(vision.identify(photo()))
    assert exc.value.status_code == 502
