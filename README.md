# Ecomigo

MVP acadêmico de identificação visual de resíduos. React/TypeScript/Vite, FastAPI/Pydantic/SQLAlchemy, PostgreSQL e Gemini API (Google AI Studio). Não há resultados fictícios na aplicação.

## Iniciar

Requisitos: Node 20.19+ ou 22.12+, Python 3.9+ (recomendado 3.11+), Docker Desktop iniciado ou PostgreSQL próprio e chave de API com acesso ao modelo multimodal escolhido.

A partir desta pasta:

```sh
cp .env.example .env
# Edite .env: AI_PROVIDER=gemini e preencha GEMINI_API_KEY no backend.
docker compose up -d db
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
cd backend
../.venv/bin/python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Em outro terminal:

```sh
cd frontend
npm ci
npm run dev
```

Abra [Ecomigo](http://localhost:5173). [Swagger](http://127.0.0.1:8000/docs) e [saúde da API](http://127.0.0.1:8000/api/health).

O backend lê `.env` da raiz do projeto, cria a tabela e insere quatro orientações ausentes na inicialização. Banco indisponível impede o startup. Sem chave, inicia normalmente, mas análise retorna 503 explícito. Não há fallback fictício.

## PostgreSQL e variáveis

`DATABASE_URL=postgresql+psycopg://ecomigo:ecomigo@localhost:55432/ecomigo`. Compose usa PostgreSQL 16 com volume persistente e porta 55432 restrita ao localhost. Para banco próprio, crie o banco e atualize a URL. Credenciais `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` devem corresponder à URL. Escape caracteres especiais de senha na URL. Os valores do exemplo são apenas de desenvolvimento. Alterar variáveis não muda credenciais de volume já inicializado. Para parar sem perder dados: `docker compose stop db`.

`OPENAI_API_KEY` fica somente no backend; nunca inclua em código, frontend ou commit. `OPENAI_MODEL` é configurável, inicialmente `gpt-4.1-mini`, sujeito ao acesso da conta; exige imagens, Responses API e JSON Schema. `AI_TIMEOUT_SECONDS=45`. `CORS_ORIGINS` recebe origens exatas separadas por vírgula, sem espaços. Reinicie o backend após alterar `.env`.

A integração segue [imagens e visão](https://developers.openai.com/api/docs/guides/images-vision) e [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs). Envia `store=false`; isso não garante retenção zero pelo provedor. Não envie pessoas/dados sensíveis. Chave e saldo precisam ser fornecidos pelo responsável pelo projeto.

## Fluxo e API

`POST /api/analises`, multipart com campo `imagem`. JPEG/PNG estático até 5 MiB e 20 milhões de pixels. O servidor valida conteúdo, MIME e decodificação, aplica EXIF, remove metadados e reduz para 1600×1600 antes da IA. Limite global de corpo: 5 MiB + 64 KiB de envelope multipart. Arquivo: 5 MiB.

Retorna objeto/material estimados, indicador inconclusivo, observação e orientação/cuidados/fonte/data cadastrados ou `null`. A IA não fornece descarte nem probabilidades inventadas. Misto, desconhecido e casos inconclusivos não recebem descarte comum. Sem orientação cadastrada, a interface informa a lacuna. Timeout, recusa, JSON inválido, banco indisponível e chave ausente geram erros legíveis.

O seletor permite upload e câmera nativa quando suportada pelo dispositivo. Histórico das últimas cinco respostas existe somente na memória da página e desaparece ao recarregar. Fotos não são armazenadas no servidor nem no histórico. Nenhuma autenticação, recompensa ou ponto de coleta fictício foi implementado.

## Testar

```sh
cd backend
../.venv/bin/python -m pytest -q
cd ../frontend
npm run build
```

Testes isolados usam SQLite em memória e mocks explícitos da IA, sem avaliar a visão do modelo. Para PostgreSQL real, crie um banco separado e execute:

```sh
docker compose exec db createdb -U ecomigo ecomigo_test
cd backend
TEST_DATABASE_URL=postgresql+psycopg://ecomigo:ecomigo@localhost:55432/ecomigo_test ../.venv/bin/python -m pytest -q
```

O teste de PostgreSQL cria a tabela de teste e reverte seu registro. Sem essa variável, é pulado. Resultados efetivos: [VALIDACAO](docs/VALIDACAO.md). Os [15 casos de avaliação da IA](docs/AVALIACAO-IA.md) estão pendentes de execução real. Dependências resolvidas: `frontend/package-lock.json` e `backend/requirements.lock.txt` (Python 3.9/macOS desta execução); requisitos portáveis estão em `backend/requirements.txt`.

## Design e especificação

[Figma](https://www.figma.com/design/APaI3wRJpnE9TIij5nkdfu/Ecomigo?node-id=10004-3711): abertura 12002:5423, pesquisa 12309:3986 e detalhes 12318:564. Assets originais exportados estão em `frontend/public/assets`; Poppins é local. Telas adaptadas a móvel/desktop e ao escopo sem login, pontos ou recompensas. Sem barra iOS fictícia. Textos de descarte vêm do banco; não reproduzem afirmações categóricas do protótipo. Fidelidade integral não foi declarada. [SPEC-001](docs/specs/SPEC-001.md) registra decisões como propostas pendentes do Product Owner.

## Publicação e pendências

Ainda sem URL pública. `npm run build` gera `frontend/dist`; servir por HTTPS e encaminhar `/api` para FastAPI no servidor. O proxy de Vite funciona apenas no desenvolvimento. Configure origem/CORS, banco, chave, limites de requisições e orçamento antes de expor endpoint público. Não exponha `.env` nem PostgreSQL. Não há migrações de schema: `create_all` é suficiente para banco novo; mudanças futuras exigem migração revisada.

Orientações iniciais são gerais e provisórias, pendentes de validação local. A aparência não comprova composição ou reciclabilidade. O prompt solicita abstinência para itens perigosos, mas não garante detecção. Sem chave válida e análise real ponta a ponta verificada, a conclusão integral do MVP continua pendente. Não foram inventadas entrevistas, avaliações ou aprovações.

## Provedor atual: Google AI Studio

Configure `AI_PROVIDER=gemini`, `GEMINI_API_KEY` e `GEMINI_MODEL=gemini-3.8-flash` no `.env` e reinicie o backend. A chave fica somente no servidor e é enviada no header `x-goog-api-key`. A integração usa `generateContent`, imagem inline e JSON Schema validado pelo Pydantic. Referência: [saída estruturada Gemini](https://ai.google.dev/gemini-api/docs/structured-output).

O nível gratuito está sujeito às cotas e condições da conta; não garante uso ilimitado. Erros de cota e credencial têm mensagens próprias. As imagens passam a ser enviadas ao Google; o parâmetro OpenAI `store=false` não se aplica ao Gemini. Confira os termos do AI Studio antes de enviar dados sensíveis. O adapter OpenAI permanece opcional usando `AI_PROVIDER=openai`; as instruções OpenAI anteriores só se aplicam a essa opção.
