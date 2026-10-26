# Plano técnico — 001 Identificação de resíduos

Versão 0.1, 15/10/2026. Estado: elaborado e revisado tecnicamente para conferência. O usuário autorizou avançar da especificação ao plano; isso não registra aprovação do PO nem resolve as perguntas da revisão de requisitos. Modelos oficiais do professor não encontrados. Código funcional preservado.

## 1. Base e objetivo

Este plano documenta a arquitetura já implementada para os RF-01 a RF-10 e RQ-01 a RQ-03 de [spec.md](spec.md). Não propõe reimplementar o MVP. Os documentos de apoio são [research.md](research.md), [data-model.md](data-model.md), [quickstart.md](quickstart.md) e [contrato OpenAPI](contracts/openapi.yaml). A identificação de tarefas e a matriz de rastreabilidade ficam para a próxima etapa autorizada.

## 2. Arquitetura real

Aplicação modular com frontend separado do backend e uma instância PostgreSQL. Não há microserviços, fila, autenticação, worker ou armazenamento persistente de imagens.

| Parte | Tecnologia observada | Responsabilidade e arquivos |
|---|---|---|
| Interface | React 19, TypeScript 5.7, Vite 6, CSS e Poppins local | `frontend/src/App.tsx`: estados início/envio/resultado e histórico; `styles.css`: apresentação; `api.ts`: multipart e espera cancelável |
| API | Python, FastAPI, Pydantic 2 via pydantic-settings, Uvicorn | `backend/app/main.py`: lifespan, middleware, health e análise; `schemas.py`: validação de saída |
| Persistência | SQLAlchemy 2, psycopg 3, PostgreSQL 16 no Compose | `database.py`: tabela orientacoes, sessões e seed; `compose.yaml`: banco local e volume |
| Imagem | Pillow | `services/images.py`: limite, conteúdo/MIME, quadro único, EXIF, conversão e redução |
| IA externa | httpx assíncrono, Gemini generateContent; OpenAI Responses opcional | `services/vision.py`: prompt, schema, parsing, tratamento de falhas; `config.py`: variáveis |

Não há React Router: navegação controlada pelo estado de App. Em desenvolvimento, Vite encaminha `/api` para `127.0.0.1:8000`. O build estático não possui proxy próprio. As versões exatas resolvidas estão nos arquivos de lock; os intervalos Python constam em `backend/requirements.txt`. Não se afirma portabilidade integral do lock Python gerado em macOS/Python 3.9.

## 3. Fluxo de execução

1. Startup cria tabelas inexistentes e insere quatro materiais ausentes. Banco inacessível impede startup; o seed não atualiza linhas existentes.
2. Navegador valida tipo declarado/tamanho e gera object URL para prévia; não confirma composição nem conteúdo real.
3. `POST /api/analises` passa pelo limitador de corpo (5 MiB + 64 KiB), parser multipart e validação do arquivo (5 MiB).
4. Pillow verifica formato real, decodifica, aplica orientação EXIF, converte RGB, reduz preservando proporção para até 1600×1600 e reencoda JPEG sem copiar EXIF.
5. Backend verifica banco antes da chamada de IA. A sessão SQLAlchemy é síncrona; a rota de análise é assíncrona. Isso é adequado ao protótipo local, sem evidência de capacidade sob concorrência.
6. O adapter selecionado envia imagem em base64, pede identificação estruturada e valida com Identification. Prompt não solicita descarte. Misto/desconhecido passam por regra determinística de inconclusivo.
7. Apenas para resultado não inconclusivo, backend consulta Guidance por material e preenche orientação/cuidados/fonte/data. Ausência gera campos nulos.
8. Interface mostra resultado, inconclusivo, lacuna ou erro. Histórico guarda até cinco respostas em RAM da página; nova análise limpa foto/resultado atuais.

## 4. Integrações, contrato e privacidade

Provedor padrão configurado no código: Gemini, modelo `gemini-3.8-flash`, ambos selecionáveis no ambiente. Autenticação externa pelo header `x-goog-api-key`; endpoint generateContent com JSON Schema. OpenAI é alternativa explícita via `AI_PROVIDER=openai`, sem fallback automático. `store=false` aplica-se somente ao adapter OpenAI. Não há chave pública no frontend nem garantia sobre retenção por terceiros.

Contrato da aplicação: `POST /api/analises` e `GET /api/health`. Swagger e `/openapi.json` são rotas de documentação automáticas, não operações de produto novas. O YAML deriva do OpenAPI da API local, com erros existentes no código acrescentados documentalmente porque os decorators não os declaram. Não foram adicionados endpoints de histórico ou CRUD de orientações.

A resposta de health não possui response_model: seu schema gerado é aberto, embora o código retorne status/database/ai_configured. ai_configured indica presença de chave, não validação nem cota. Falhas não tratadas podem gerar 500 sem envelope garantido.

CORS permite GET/POST e Content-Type nas origens configuradas. O limitador de corpo é externo ao CORS: rejeições antecipadas podem não conter cabeçalhos CORS em acesso direto entre origens. O proxy local usa mesma origem. Não há rate limiting, autenticação ou controle de orçamento implementados.

## 5. Persistência e inicialização

Há apenas a tabela `orientacoes`, detalhada em data-model.md. Não há tabela de usuários, imagens ou análises. Compose publica o banco apenas em localhost:55432 e mantém volume. `create_all` cria schema novo, não migra schema existente. Seed consulta por material e insere ausentes; duas inicializações concorrentes podem disputar a restrição UNIQUE. Não foi testado startup concorrente.

## 6. Estratégia de verificação

| Camada | Verificação existente | Alcance e lacunas |
|---|---|---|
| API/imagens/base | `test_api.py`, TestClient, SQLite em memória e AsyncMock | upload válido/inválido, limites, MIME, inconclusivo, seed, orientação ausente e falhas; não mede IA real |
| Adapter OpenAI | testes em `test_api.py`, substituição explícita do HTTP | schema enviado, resposta válida/malformada, recusa, timeout e erros |
| Adapter Gemini | `test_gemini.py`, substituição explícita do HTTP | resposta válida, quota, autenticação, alta demanda, bloqueio, JSON inválido, timeout |
| PostgreSQL | `test_postgres.py`, banco dedicado | cria tabela, insere, consulta e reverte registro; não cobre concorrência nem migrações |
| Frontend | `npm run build` | valida TypeScript/bundle; não equivale a teste de navegação ou acessibilidade |
| Contrato | comparação do YAML com OpenAPI em execução, schemas e amostras controladas | descrita no registro abaixo; não avalia disponibilidade/qualidade do provedor |
| IA real | protocolo em `docs/AVALIACAO-IA.md` | 15 casos pendentes; sem limiar de aprovação acordado |

Não criar novos critérios quantitativos sem decisão do responsável. Após definição, a futura etapa de tarefas deve prever demonstração com foto real, avaliação adversarial, teclado/leitor de tela, móvel/desktop e teste dos pontos sem cobertura. Sem evidência de carga, não há SLA prometido. Timeouts configurados não são garantia de duração total.

## 7. Revisão do plano antes das tarefas

Revisão técnica em 15/10/2026. Problemas identificados; nenhum alterado em código nesta etapa:

| ID | Problema observado | Consequência / encaminhamento para conferência |
|---|---|---|
| RP-01 | Schema 200 de health aberto; erros explícitos ausentes no OpenAPI automático | YAML preserva schema original e acrescenta erros do código; decidir depois se a API deve tipar/documentar decorators |
| RP-02 | Proteção de pixels depende do Pillow; documentos antigos resumem valor como limite estrito | Conferir o limite desejado antes de qualquer mudança; não declarar validação de fronteira executada |
| RP-03 | Descarte provisório sem validação local e nenhuma meta acordada para IA | Não há aceite de eficácia/segurança; depende de responsável/contexto e revisão dos 15 casos |
| RP-04 | Recursos acessíveis e responsivos sem percurso completo testado | Conferência manual continua pendente; build não comprova CA-15 |
| RP-05 | CORS não envolve rejeição do limitador; corpo integral armazenado em memória | Avaliar no contexto de publicação/concorrência; não alterar arquitetura para a documentação |
| RP-06 | SQL síncrono em rota async e transação aberta durante chamada externa | Sem conclusão de desempenho; avaliar apenas se houver requisito/carga definidos |
| RP-07 | Sem migrations e possível disputa de seed concorrente | Não planejar múltiplas instâncias como capacidade já validada |
| RP-08 | README e SPEC anterior contêm trechos anteriores à migração Gemini | Documentos atuais descrevem estado real; atualização histórica não foi feita silenciosamente |
| RP-09 | Nível gratuito sujeito a cota/alta demanda; sem fallback automático | Falha deve continuar explícita; demonstração real depende de serviço disponível |
| RP-10 | Deploy sem definição de exigência acadêmica e sem infraestrutura validada | Publicação não realizada; confirmar aceitação local ou necessidade de URL |

A ausência do modelo original do kit e as perguntas da revisão de requisitos permanecem abertas. Autorização para escrever o plano não foi interpretada como resposta a essas perguntas.

## 8. Registro das verificações desta etapa

Resultados registrados após execução: ver seção final deste documento. O código de produto e os testes existentes foram preservados. Não houve nova chamada ao provedor de IA nesta etapa documental.

## 9. Ponto de parada

Plano e apoios preparados para conferência; sem aprovação do PO registrada. **Não produzir tasks.md nem traceability.md antes da autorização do usuário para a próxima etapa.** A revisão de requisitos anterior permanece como registro da fase de especificação.

### Resultados observados na revisão do plano

Em 15/10/2026:

- Em `backend`, `TEST_DATABASE_URL=postgresql+psycopg://ecomigo:ecomigo@localhost:55432/ecomigo_test ../.venv/bin/python -m pytest -q`: **33 aprovados em 1,97 s**, nenhum pulado.
- Em `frontend`, `npm run build`: TypeScript e Vite concluídos, saída 0. Não reexecutada instalação limpa.
- `contracts/openapi.yaml`: parseado com PyYAML; 12 referências locais resolvidas. Rotas, métodos, operationId, parâmetros, corpo multipart, schemas originais e respostas originalmente declaradas comparados ao `/openapi.json` da API em execução, sem divergências.
- Amostras na API em execução: health 200 com banco conectado; POST sem campo 422; POST com arquivo vazio 400 e detail textual. Essas chamadas não acionam o modelo.
- Erros adicionais 400/413/415/502/503/504 da análise e 413/503 de health documentados por inspeção do código; suíte existente complementa vários desses comportamentos. Não foi utilizado validador formal integral OpenAPI nem exercitado cada erro na API real. Não se declara cobertura exaustiva do contrato.

Nenhum resultado novo de avaliação visual de IA, deploy ou aprovação do PO foi produzido. Os pontos RP-01 a RP-10 permanecem registrados para conferência, sem transformar pendências em implementação concluída.
