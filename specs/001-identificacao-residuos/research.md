# Registro de decisões técnicas — 001

15/10/2026. Registro retrospectivo baseado em código e documentos; não é pesquisa com usuários nem aprovação do professor. Justificativas abaixo são análise técnica da implementação existente, não atas de decisões da equipe que não foram fornecidas.

| ID | Decisão e estado | Justificativa técnica | Alternativa e situação |
|---|---|---|---|
| D-01 | React/TS/Vite e CSS — implementada | Corresponde ao stack solicitado e ao frontend existente; layout/estado concentrados em App | Router/Tailwind: não usados; sem necessidade de migração para documentar |
| D-02 | FastAPI/Pydantic/SQLAlchemy — implementada | API multipart, saída validada e acesso modular ao banco | Microserviços/fila: não implementados, não necessários ao escopo demonstrado |
| D-03 | PostgreSQL 16, tabela orientacoes — implementada | Orientações persistidas independentemente da resposta da IA | SQLite: usado somente em testes isolados; não substitui PostgreSQL de execução |
| D-04 | Gemini padrão, modelo por ambiente — implementada | Migração solicitada pelo usuário para Google AI Studio; adapter real existente | OpenAI: adapter opcional existente; sem fallback automático; registros anteriores relatam falta de créditos |
| D-05 | Imagem inline e saída JSON validada — implementada | Evita URL pública de foto e permite rejeitar resposta estruturalmente inválida | Upload remoto persistente: não implementado; não necessário à jornada atual |
| D-06 | Orientação exclusivamente da base — implementada | Separa identificação probabilística do conteúdo cadastrado e permite fonte/data | Descarte gerado pela IA: excluído pelo requisito |
| D-07 | Inconclusivo determinístico para misto/desconhecido — implementada | Evita orientação específica nesses resultados | Filtro independente de perigosos: não implementado; prompt não garante reconhecimento |
| D-08 | Histórico efêmero de cinco respostas — implementada | Sem contas, fotos ou dados pessoais persistidos no servidor | Histórico persistente/localStorage: não implementado nem necessário no escopo atual |
| D-09 | Pillow valida e reencoda antes do envio — implementada | Verifica conteúdo e reduz bytes/metadados enviados | Enviar arquivo bruto sem validação: não adotado; limite exato de pixels permanece questão de revisão |
| D-10 | create_all e seed de ausentes — implementada | Suficiente para inicialização simples do banco novo | Migrations versionadas: pendentes apenas se houver evolução de schema; sem implementação fictícia |
| D-11 | Mocks de provedor + integração PostgreSQL separada — implementada | Reprodutibilidade sem consumir cota em testes; banco real complementa SQLite | Avaliação real dos 15 casos: pendente, não substituída por mocks |
| D-12 | Limiares de IA, responsável por orientações, aceite visual e deploy — pendentes | Não há decisão registrada; não inferir a partir do código | Escolha deve ser confirmada; não inventar precisão mínima ou SLA |

## Evidências e fontes

Fontes primárias locais: `backend/app/services/vision.py`, `images.py`, `schemas.py`, `database.py`, `config.py`, `frontend/src/App.tsx`, `frontend/src/api.ts`, `compose.yaml`, suíte `backend/tests`, README e `docs/VALIDACAO.md`. O histórico relata sucesso com imagem branca e indisponibilidade externa posterior; não é avaliação de qualidade para resíduos.

Referência técnica já usada pelo projeto: [Structured Outputs Gemini](https://ai.google.dev/gemini-api/docs/structured-output). Este documento não afirma novo levantamento de preço, cotas, termos ou disponibilidade de modelos; valores/modelo descrevem a configuração existente, não garantia comercial atual. Não houve entrevistas, benchmark, estudo comparativo executado ou aprovação do PO nesta fase.
