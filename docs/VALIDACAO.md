# Validação executada — 15/10/2026

- `npm run build`: aprovado (TypeScript e Vite).
- `TEST_DATABASE_URL=postgresql+psycopg://ecomigo:ecomigo@localhost:55432/ecomigo_test ../.venv/bin/python -m pytest -q`: **26 aprovados**, nenhum pulado.
- PostgreSQL 16 iniciado por `docker compose up -d --wait db`, estado saudável. Banco separado `ecomigo_test` criado para teste de integração com rollback do registro.
- Backend Uvicorn iniciou com PostgreSQL real; tabelas e quatro orientações provisórias inicializadas.
- Frontend Vite iniciou em http://127.0.0.1:5173.
- `GET /api/health` pelo proxy Vite: 200, database=connected, ai_configured=false.
- Upload PNG válido pelo proxy frontend: 503 com mensagem explícita de chave ausente, sem resultado fictício.
- Navegador: início renderizado com logo/wordmark locais; botão Começar a reciclar abriu envio, com análise desabilitada antes da seleção. Verificação visual em viewport estreito; cobertura completa desktop e acessibilidade manual ainda pendentes.

## Cobertura automatizada
JPEG/PNG válidos, arquivo vazio, tamanho excedido, MIME inválido/divergente, conteúdo falso, limite de corpo, inconclusivos conhecidos/mistos, ausência de orientação, seed idempotente, saúde, indisponibilidade, timeout, recusa, resposta incompleta/inválida e cinco envelopes malformados do provedor. Adapter testado com limite HTTP substituído explicitamente; SQLite para testes isolados e PostgreSQL real para roundtrip SQLAlchemy.

## Limites e pendências
Não há OPENAI_API_KEY configurada. Nenhuma fotografia foi analisada por modelo real e os 15 casos de avaliação permanecem não executados. Não foi validada jornada completa de resultado real no navegador. Sem deploy público. Orientações precisam de validação local. Figma: contexto de abertura 12002:5423 acessível e conferido; nó da página 10004:3711 retornou pedido de seleção no contexto de código, mas screenshot estava disponível. Não se declara fidelidade visual integral.

O sandbox restringiu inicialmente Docker, conexão PostgreSQL e portas locais. Execução autorizada fora do sandbox permitiu iniciar os serviços e concluir os testes, sem alterar esse requisito do ambiente.

## Configuração posterior da API
Credencial configurada somente em `.env` (permissões 600), backend reiniciado. Acesso ao modelo configurado: HTTP 200. Tentativa real com imagem branca de teste: aplicação retornou 502; diagnóstico direto do provedor: HTTP 429, `credit_balance_exhausted` / `insufficient_quota`. A conta está sem créditos. Nenhuma identificação real foi concluída; avaliação dos 15 casos continua pendente. A seção anterior sobre ausência de chave descreve a primeira etapa e foi superada por esta configuração.

## Migração para Google AI Studio
Adapter Gemini implementado com imagem inline, JSON Schema e validação Pydantic; credencial apenas no backend. Modelo `gemini-3.8-flash`, indicado pelo provedor após recusa de 2.5 Flash para novos usuários. Chamada real do adapter: HTTP 200, imagem branca retornou desconhecido/inconclusivo corretamente. Teste seguinte pelo proxy Vite retornou erro externo; diagnóstico do Google HTTP 503 UNAVAILABLE por alta demanda. Não foi concluída análise real de um resíduo nem os 15 casos de avaliação. Backend reiniciado com Gemini.
