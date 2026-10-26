import asyncio
import json
import httpx
import pytest
from fastapi import HTTPException
from app.config import settings
from app.services.vision import identify

@pytest.mark.parametrize('mode,status', [('valid',200),('quota',503),('auth',503),('busy',503),('invalid',502),('blocked',502),('timeout',504)])
def test_gemini(monkeypatch, mode, status):
    monkeypatch.setattr(settings, 'ai_provider', 'gemini')
    monkeypatch.setattr(settings, 'gemini_api_key', 'test-only')
    async def fake(self, url, **kwargs):
        assert url.endswith(':generateContent')
        assert kwargs['headers']['x-goog-api-key'] == 'test-only'
        assert kwargs['json']['contents'][0]['parts'][1]['inlineData']['mimeType'] == 'image/jpeg'
        assert 'responseJsonSchema' in kwargs['json']['generationConfig']
        if mode == 'timeout':
            raise httpx.ReadTimeout('test')
        answer = dict(objeto='Sem objeto', material='desconhecido', identificacao_inconclusiva=True, observacao='Não há resíduo visível.')
        payload = {'candidates':[{'finishReason':'SAFETY' if mode == 'blocked' else 'STOP','content':{'parts':[{'text':json.dumps(answer)}]}}]}
        return httpx.Response(503 if mode == 'busy' else 429 if mode == 'quota' else 403 if mode == 'auth' else 200, request=httpx.Request('POST',url), json=None if mode == 'invalid' else payload)
    monkeypatch.setattr(httpx.AsyncClient, 'post', fake)
    if status == 200:
        assert asyncio.run(identify(b'test')).identificacao_inconclusiva
    else:
        with pytest.raises(HTTPException) as exc:
            asyncio.run(identify(b'test'))
        assert exc.value.status_code == status
