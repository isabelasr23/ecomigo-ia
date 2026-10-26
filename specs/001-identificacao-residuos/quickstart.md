# Execução local — 001

Comandos relativos à raiz `ecomigo`. Não execute comandos dentro da pasta `specs`. Pré-requisitos documentados no projeto: Node 20.19+ ou 22.12+, Python 3.9+ (recomendado 3.11+), Docker Desktop funcionando ou PostgreSQL próprio. Dependências frontend em package-lock.json; backend portável em requirements.txt, com lock anterior específico do ambiente em requirements.lock.txt.

## 1. Ambiente e PostgreSQL

Se `.env` ainda não existir, copie o exemplo. Não sobrescreva a credencial já configurada:

```sh
test -f .env || cp .env.example .env
docker compose up -d --wait db
```

Edite `.env` localmente, sem publicar as chaves:

| Variável | Valor de desenvolvimento / finalidade |
|---|---|
| DATABASE_URL | postgresql+psycopg://ecomigo:ecomigo@localhost:55432/ecomigo |
| POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB | ecomigo / ecomigo / ecomigo; apenas desenvolvimento |
| AI_PROVIDER | gemini (padrão); openai para adapter alternativo |
| GEMINI_API_KEY | Chave privada Google AI Studio; não colocar no frontend |
| GEMINI_MODEL | gemini-3.8-flash na configuração existente; depende do acesso da conta |
| OPENAI_API_KEY / OPENAI_MODEL | Somente alternativa OpenAI; modelo padrão gpt-4.1-mini |
| AI_TIMEOUT_SECONDS | 45; timeout httpx, não SLA total |
| CORS_ORIGINS | http://localhost:5173,http://127.0.0.1:5173; origens exatas separadas por vírgula |

Banco próprio: criar banco e usuário correspondentes e ajustar DATABASE_URL. Credenciais do Compose não alteram volume já inicializado. Não remover volume para tentar corrigir conexão. O backend lê `.env` na raiz automaticamente; reinicie após editar. Não é necessário exportar a chave no terminal.

## 2. Backend

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r backend/requirements.txt
.venv/bin/python -m uvicorn app.main:app --app-dir backend --reload --host 127.0.0.1 --port 8000
```

O startup cria tabela e sementes ausentes. Erro no banco impede iniciar. Chave ausente permite iniciar, mas análise retorna erro explícito. Nenhum resultado fictício substitui o modelo.

## 3. Frontend em outro terminal

```sh
cd frontend
npm ci
npm run dev -- --port 5173 --strictPort
```

Acesso: [aplicação](http://127.0.0.1:5173), [Swagger](http://127.0.0.1:8000/docs), [saúde](http://127.0.0.1:8000/api/health). Vite encaminha `/api` ao backend. Se já houver servidores ativos, reutilize-os ou encerre os seus processos antes de reiniciar; não inicie cópias em portas alternativas sem ajustar CORS/proxy.

## 4. Verificações

Na raiz:

```sh
curl --fail http://127.0.0.1:8000/api/health
cd backend
../.venv/bin/python -m pytest -q
```

Sem TEST_DATABASE_URL, o teste PostgreSQL é pulado. Para integração real, use banco separado. Criar apenas se ainda não existir:

```sh
docker compose exec -T db createdb -U ecomigo ecomigo_test
```

Se retornar “already exists”, reutilize esse banco dedicado. Em `backend`:

```sh
TEST_DATABASE_URL=postgresql+psycopg://ecomigo:ecomigo@localhost:55432/ecomigo_test ../.venv/bin/python -m pytest -q
```

Em `frontend`:

```sh
npm run build
```

Esses testes usam mocks explícitos de IA e não consomem cota do modelo. Para demonstração real, selecionar foto sem pessoas/dados sensíveis, conferir prévia e analisar; depende de cota e disponibilidade externa. Os 15 casos de `docs/AVALIACAO-IA.md` não estão automaticamente executados por pytest.

## 5. Diagnóstico e encerramento

- 413/415: tamanho ou conteúdo/MIME/quadro inválido; escolher JPEG/PNG estático válido.
- 503 Gemini: chave ausente/recusada, cota ou alta demanda conforme mensagem; não significa sempre problema de banco.
- 502: resposta externa inválida/bloqueada ou erro HTTP tratado; 504: timeout externo.
- Saúde com ai_configured=true confirma apenas presença de chave.
- Parar servidores: Ctrl+C em seus terminais. Parar banco preservando volume: `docker compose stop db`.

Build gera frontend/dist; `npm run preview` não configura proxy /api de produção. Sem deploy implementado. Publicação exige encaminhar /api para FastAPI e configurar origens/credenciais/infraestrutura; não há URL pública registrada. Comandos de instalação e inicialização acima são o procedimento real documentado; não se afirma instalação limpa novamente executada nesta revisão.
