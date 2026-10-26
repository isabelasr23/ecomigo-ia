from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from .config import settings
from .database import Guidance, get_db, initialize_database
from .schemas import Analysis
from .services.images import validate_image
from .services.vision import identify

@asynccontextmanager
async def lifespan(app):
    initialize_database()
    yield

app = FastAPI(title='Ecomigo', version='0.1.0', lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins.split(','),
    allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])

# Bound the entire multipart body, including chunked requests, before parsing uploads.
class BodyLimit:
    def __init__(self, app):
        self.app = app
    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        size, messages = 0, []
        while True:
            message = await receive()
            if message['type'] == 'http.disconnect':
                return
            size += len(message.get('body', b''))
            if size > 5 * 1024 * 1024 + 64 * 1024:
                from starlette.responses import JSONResponse
                return await JSONResponse({'detail': 'A imagem deve ter no máximo 5 MB.'}, 413)(scope, receive, send)
            messages.append(message)
            if not message.get('more_body', False):
                break
        async def replay():
            return messages.pop(0) if messages else await receive()
        await self.app(scope, replay, send)

app.add_middleware(BodyLimit)

@app.get('/api/health')
def health(db: Session = Depends(get_db)):
    try:
        db.execute(text('SELECT 1'))
    except SQLAlchemyError:
        raise HTTPException(503, 'Banco de dados indisponível.')
    return {'status': 'ok', 'database': 'connected', 'ai_configured': bool(settings.gemini_api_key if settings.ai_provider == 'gemini' else settings.openai_api_key)}

@app.post('/api/analises', response_model=Analysis)
async def analyze(imagem: UploadFile = File(...), db: Session = Depends(get_db)):
    try:
        clean = await validate_image(imagem)
    finally:
        await imagem.close()
    # Check DB before incurring an external API charge.
    try:
        db.execute(text('SELECT 1'))
    except SQLAlchemyError:
        raise HTTPException(503, 'Banco de dados indisponível. Tente novamente.')
    identified = await identify(clean)
    result = Analysis(**identified.model_dump())
    if not identified.identificacao_inconclusiva:
        try:
            guidance = db.scalar(select(Guidance).where(Guidance.material == identified.material))
        except SQLAlchemyError:
            raise HTTPException(503, 'Não foi possível consultar as orientações.')
        if guidance:
            result.orientacao = guidance.orientacao
            result.cuidados = guidance.cuidados
            result.fonte_orientacao = guidance.fonte
            result.data_atualizacao = guidance.data_atualizacao.isoformat()
    return result
