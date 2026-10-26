# Revisão de requisitos — Especificação 001

Data: 15/10/2026. Documento revisto: `../spec.md`, versão 0.1. Revisão documental/técnica pelo assistente; sem aceite do PO ou do professor. Não é um checklist oficial do kit: os modelos não foram encontrados no projeto.

## Método

- **Claro:** o texto delimita comportamento e resultado verificável. Não significa aprovado nem integralmente testado.
- **Ambíguo:** há definição parcial ou decisão necessária para determinar o aceite.
- **Ausente:** a definição/evidência necessária não foi fornecida.

Os itens abaixo derivam do pedido do usuário e da implementação inspecionada; perguntas são propostas para revisão, não exigências adicionais atribuídas ao professor.

## Resultado da revisão da especificação

| Item | Classificação | Evidência e limite | Pergunta concreta, quando aplicável |
|---|---|---|---|
| Problema, objetivo e história principal | Claro | Seções 1 e 2; não atribuem pesquisa de campo inexistente | — |
| Jornada e estados de interface | Claro | Seção 4 e RF-02/RF-07/RF-08; App.tsx | — |
| Escopo e exclusões | Claro | Seção 3 distingue histórico efêmero de persistência e exclui funções inexistentes | — |
| Entrada, tamanho, MIME e conteúdo real | Claro | RF-01, CA-01 a CA-03; limite exato em bytes e validação no servidor | — |
| Substituição e captura nativa | Claro | RF-02/CA-04; captura depende do dispositivo | — |
| Análise real e formato estruturado | Claro | RF-03/CA-05; Gemini atual, OpenAI opcional; sem mock na aplicação | — |
| Regra de inconclusivo e ausência de descarte específico | Claro | RF-04/CA-06; distingue regra determinística e instrução do prompt | — |
| Orientações exclusivamente cadastradas e provisórias | Claro | RF-05/CA-07; quatro materiais presentes no PostgreSQL | — |
| Ausência de orientação | Claro | RF-06/CA-08; retorno nulo e mensagem específica | — |
| Erros, processamento e nova análise | Claro | RF-07/RF-08, CA-09 a CA-11; timeouts não tratados como SLA | — |
| Histórico e privacidade da aplicação | Claro | RF-09/RQ-01; cinco respostas na memória, sem tabela de análises | — |
| Saúde e significado de ai_configured | Claro | RF-10/CA-13; presença de chave não equivale a autenticação validada | — |
| Critérios Dado/Quando/Então e identificadores | Claro | CA-01 a CA-15 vinculados a RF/RQ | — |
| Evidências e limites dos testes | Claro | Seção 8; 33 testes aprovados e build, sem inferir acurácia/aceite | — |
| Registro de status e separação das etapas SDD | Claro | Sem aprovação registrada; plano e tarefas não produzidos | — |
| Limite exato de pixels aceito | Ambíguo | Documentos antigos dizem “até 20 milhões”; código depende de DecompressionBombWarning do Pillow, sem comparação explícita da área | O PO confirma 20 milhões como limite estrito ou aceita o comportamento atual do decodificador? |
| Aceite de fidelidade visual e responsividade | Ambíguo | Figma é referência, mas não há conjunto de telas/dispositivos aprovado; inspeção completa não registrada | Quais telas e tamanhos de dispositivo serão usados na conferência visual do MVP? |
| Aceite de acessibilidade | Ambíguo | Há recursos no código; percurso manual completo não foi validado | Qual combinação de navegador, teclado e leitor de tela será usada na conferência? |
| Necessidade de URL pública para avaliação | Ambíguo | Pedido inicial inclui deploy como P1; não há deploy registrado | A avaliação aceita execução local ou exige URL pública nesta entrega? |
| Modelo original do Kit de Autoestudo | Ausente | Nenhum modelo do professor foi encontrado nos arquivos do projeto | Há arquivos do kit que precisam ser fornecidos para conferir títulos e campos obrigatórios? |
| Validação das orientações e responsabilidade | Ausente | Fonte atual é base acadêmica provisória; não há aprovação técnica local | Quem validará as quatro orientações e para qual município/contexto de coleta? |
| Limiar de aceitação da IA | Ausente | Há protocolo de 15 casos, sem execução ou meta acordada | Como será decidido o aceite dos 15 casos, especialmente abstinência em perigosos/ambíguos? |
| Evidência de jornada real com resíduo | Ausente | Registro anterior é imagem branca; testes de adapter usam mocks | Qual fotografia sem dados pessoais será usada para demonstrar identificação e orientação reais? |

## Inspeção realizada

Foram lidos `frontend/src/App.tsx`, `api.ts`, estilos, configuração Vite e dependências; `backend/app/main.py`, `schemas.py`, `database.py`, `config.py`, serviços de imagem/visão; `backend/tests/test_api.py`, `test_gemini.py`, `test_postgres.py`; `compose.yaml`, README, SPEC-001 anterior, VALIDACAO e AVALIACAO-IA. O schema e os materiais do PostgreSQL foram consultados diretamente. Não foram lidas nem reproduzidas chaves privadas para compor os documentos.

Schema observado: somente tabela `orientacoes`, campos `id`, `material`, `descricao`, `orientacao`, `cuidados`, `fonte`, `data_atualizacao`. O modelo de dados completo será documentado apenas após autorização da etapa correspondente.

## Problemas encontrados e tratamento nesta etapa

1. **Documentação histórica desatualizada:** SPEC-001 anterior descreve OpenAI como proposta principal e o README mantém instruções antigas antes da seção Gemini. A nova especificação identifica Gemini como padrão e OpenAI como opcional. Arquivos históricos foram preservados, sem reescrever fatos anteriores.
2. **Validação não equivale a conclusão do MVP:** 33 testes aprovados não demonstram qualidade do modelo, acessibilidade integral ou jornada completa com foto real. A seção 8 explicita essa separação.
3. **Prompts não são garantias determinísticas:** não existe filtro independente de perigosos nem garantia de ressalva linguística em todo texto. A especificação registra a limitação em vez de declarar esse requisito aprovado.
4. **Limite de pixels sem contrato exato:** a proteção de decodificação está implementada, mas o valor nominal dos documentos antigos não equivale a comparação explícita da área. Pergunta registrada; nenhum ajuste de funcionalidade realizado.
5. **Retenção por provedor:** a aplicação não persiste fotos; a documentação não estende essa afirmação ao Google. O `store=false` da opção OpenAI não foi atribuído ao Gemini.
6. **Evidências faltantes:** suíte não inclui testes de navegador nem cobre especificamente câmera, histórico, dimensões extremas e indisponibilidade de banco. Tais critérios permanecem sem aceite integral.

## Execuções observadas nesta revisão

- Backend, em `backend`: `TEST_DATABASE_URL=postgresql+psycopg://ecomigo:ecomigo@localhost:55432/ecomigo_test ../.venv/bin/python -m pytest -q` → **33 aprovados em 1,45 s**, sem testes pulados.
- Frontend, em `frontend`: `npm run build` → TypeScript e Vite concluídos; saída 0.
- PostgreSQL da aplicação: inspeção somente leitura confirmou `orientacoes` e materiais `metal`, `papel`, `plastico`, `vidro`.
- Os testes externos de IA usam mocks explícitos. Não houve nova avaliação real da IA nesta revisão. Os 15 casos permanecem pendentes.

## Resumo e ponto de parada

Revisão: **15 itens claros, 4 ambíguos e 4 ausentes**. As definições ausentes não autorizam inventar metas ou aprovações. Código funcional preservado; apenas os dois documentos desta etapa foram criados.

**Aguardando conferência do usuário.** Conforme a instrução explícita de revisão entre etapas, `plan.md` e demais artefatos ainda não foram produzidos. O próximo passo depende de autorização para elaborar e revisar o plano; tarefas terão novo ponto de parada depois da revisão do plano. Aprovação do usuário para continuar o trabalho não será registrada como aprovação do PO sem declaração explícita nesse sentido.

### Atualização do ponto de parada

O usuário autorizou seguir ao plano após a entrega desta revisão. O plano e seus apoios foram produzidos e a revisão técnica está na seção 7 de `../plan.md`. Esta checklist permanece como registro da revisão de especificação (15 claros, 4 ambíguos, 4 ausentes); a autorização não resolveu as perguntas pendentes nem constituiu aprovação explícita do PO. Novo ponto de parada: aguardar conferência do plano antes de tasks.md e traceability.md.
