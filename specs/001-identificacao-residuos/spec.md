# Especificação 001 — Identificação de resíduos por fotografia

Versão: 0.1 — 15/10/2026. Estado: proposta para conferência; sem aprovação registrada do Product Owner (PO) ou do professor. Etapa: especificação, anterior ao plano.

## 1. Problema e evidências disponíveis

O Ecomigo é um MVP acadêmico de Sistemas Inteligentes Aplicados para auxiliar uma pessoa a reconhecer um resíduo e buscar orientação de descarte. A aparência de um objeto não comprova sua composição nem sua reciclabilidade; a aplicação deve apresentar estimativas e admitir incerteza.

As evidências disponíveis são o pedido do projeto, o código existente, o PostgreSQL local, os testes, o README e os registros em `docs/VALIDACAO.md`. Não foram fornecidos entrevistas, pesquisa de campo ou validação das orientações por autoridade local. Não foram encontrados modelos do professor no projeto, excluindo dependências instaladas. Este documento segue as instruções fornecidas pelo usuário, sem afirmar conformidade com um modelo não disponibilizado.

A especificação adapta `docs/specs/SPEC-001.md` ao estado atual. O documento anterior permanece preservado como registro histórico. Em divergências, esta proposta usa o código inspecionado como evidência do comportamento atual; isso não equivale a aprovação de negócio.

## 2. Objetivo e história prioritária

Permitir que uma pessoa envie uma fotografia de um objeto e receba uma identificação visual estimada, uma hipótese de material e, quando aplicável, orientação recuperada da base cadastrada, com ressalvas e indicação de conteúdo provisório.

**História principal:** como pessoa que deseja descartar um objeto, quero enviar ou tirar uma fotografia e consultar a estimativa de material e a orientação disponível, para decidir meu próximo passo considerando as regras locais.

O resultado esperado é a jornada início → envio → processamento → resultado ou erro → nova análise. Sua disponibilidade depende do banco e do provedor externo. A especificação não define meta numérica de acurácia, latência ou disponibilidade porque não existe decisão registrada para esses valores.

## 3. Escopo

Incluído no MVP existente:

- JPEG e PNG estáticos, seleção de arquivo e captura pelo seletor nativo quando o dispositivo permitir, prévia e substituição.
- Estimativa de papel, plástico, metal e vidro; categorias misto e desconhecido; indicador de identificação inconclusiva.
- Processamento real por IA, resultado estruturado, orientação cadastrada, erros e reanálise.
- Histórico das últimas cinco respostas exclusivamente na memória da página, acessível pela tela inicial.
- Interface em português com referência visual Ecomigo, adaptação móvel/desktop e recursos de acessibilidade presentes no código.
- Consulta de saúde técnica da API e do banco.

Fora do escopo atual: contas e autenticação, histórico persistente ou compartilhado, armazenamento de fotos pela aplicação, recompensas, pontos de coleta, mapa/geolocalização, confirmação química, confirmação manual de material e administração de orientações pela interface. Não existe deploy público registrado. Publicação permanece uma pendência do projeto, não um resultado desta etapa documental.

## 4. Jornada, entradas e saídas

1. A pessoa abre o início e seleciona “Começar a reciclar”.
2. Escolhe uma foto ou usa “Tirar foto”, conforme suporte do dispositivo.
3. O navegador verifica tipo declarado, tamanho e arquivo não vazio e mostra prévia. A confirmação do conteúdo real ocorre no servidor.
4. Ao acionar “Analisar imagem”, a interface informa processamento e bloqueia novo envio simultâneo.
5. O servidor valida e prepara a imagem, verifica acesso ao banco, solicita identificação ao provedor configurado e valida a resposta.
6. Para identificação não inconclusiva, consulta a orientação por material; para inconclusiva, não oferece orientação específica da base.
7. A interface apresenta resultado, lacuna de orientação ou erro e permite nova tentativa/análise.

Entrada técnica observada: `POST /api/analises`, multipart, campo obrigatório `imagem`. Limite do arquivo: 5 MiB (5.242.880 bytes), exibido como “5 MB” na interface; corpo HTTP limitado a 5 MiB + 64 KiB. JPEG/PNG devem ter MIME correspondente ao conteúdo e um único quadro. O código usa proteção Pillow com `MAX_IMAGE_PIXELS=20_000_000`; o tratamento do limite exato de pixels exige verificação adicional, pois depende de avisos do decodificador e arredondamentos. Não se declara garantia de rejeição de todo arquivo acima desse número.

Saída: `objeto`, `material`, `identificacao_inconclusiva`, `observacao`, `orientacao`, `cuidados`, `fonte_orientacao`, `data_atualizacao` e `orientacao_provisoria`. Valores de material: `papel`, `plastico`, `metal`, `vidro`, `misto`, `desconhecido`. Campos da orientação podem ser nulos. O indicador provisório é atualmente sempre verdadeiro.

## 5. Requisitos funcionais

| ID | Requisito verificável | Critérios |
|---|---|---|
| RF-01 | Aceitar JPEG/PNG estáticos não vazios até 5 MiB, validar conteúdo/MIME no servidor e rejeitar entradas inválidas antes de chamar IA. | CA-01 a CA-03 |
| RF-02 | Exibir prévia, permitir substituição e disponibilizar captura nativa onde suportada. | CA-01, CA-04 |
| RF-03 | Executar análise real com provedor configurado, validar campos estruturados e apresentar objeto/material como estimativas, sem porcentagem de confiança inventada. | CA-05 |
| RF-04 | Marcar misto/desconhecido como inconclusivos; respeitar inconclusivo também para materiais comuns; não recuperar orientação específica nesses casos. | CA-06 |
| RF-05 | Recuperar orientação, cuidados, fonte e data da base cadastrada para material não inconclusivo e indicar caráter provisório. Não gerar descarte pela IA. | CA-07 |
| RF-06 | Informar ausência de orientação sem preencher conteúdo fictício. | CA-08 |
| RF-07 | Exibir processamento, impedir submissões simultâneas e apresentar erros de validação, conexão e provedor com possibilidade de tentar novamente. | CA-02, CA-03, CA-09, CA-10 |
| RF-08 | Permitir nova análise limpando foto e resultado atuais. | CA-11 |
| RF-09 | Manter até cinco respostas na memória da página, sem persistir fotografias ou criar histórico no banco. | CA-12 |
| RF-10 | Disponibilizar consulta de saúde que verifica banco e indica presença da chave do provedor selecionado, sem afirmar que a credencial foi validada. | CA-13 |

## 6. Qualidade, privacidade e limitações

| ID | Requisito/limite | Critérios |
|---|---|---|
| RQ-01 | Manter credenciais no backend, não persistir fotos na aplicação e informar envio ao serviço externo. Política de uso/retenção do provedor não é garantia da aplicação. | CA-14 |
| RQ-02 | Fornecer controles identificáveis por teclado, foco visível e mensagens acessíveis de erro/carregamento; adaptar a interface a móvel e desktop preservando identidade Ecomigo. A validação manual completa está pendente. | CA-15 |
| RQ-03 | Tratar falhas externas e tempo de espera sem substituir IA por respostas fictícias. | CA-09, CA-10 |

O prompt instrui abstinência para objetos perigosos, múltiplos objetos, baixa visibilidade e instruções adversariais na imagem. Apenas misto/desconhecido são forçados a inconclusivo por regra determinística. Não há garantia implementada de reconhecimento de todo objeto perigoso nem de linguagem de incerteza em toda saída textual. Essas propriedades precisam de avaliação real.

Configuração atual observada no código: Gemini como padrão, modelo configurável; adapter OpenAI opcional. O limite configurado da chamada externa é 45 segundos por timeout do cliente HTTP; o navegador cancela sua espera em 65 segundos. Esses valores não constituem SLA nem orçamento total garantido de execução.

## 7. Critérios de aceitação

- **CA-01 (RF-01, RF-02):** Dado um JPEG/PNG não vazio de até 5 MiB, quando selecionado no navegador, então a prévia aparece e o botão de análise fica disponível; a seleção não substitui a validação real do servidor.
- **CA-02 (RF-01, RF-07):** Dado arquivo vazio, conteúdo inválido ou MIME divergente, quando enviado ao servidor, então recebe erro 400 para vazio ou 415 para formato/conteúdo inválido, sem chamada à IA; campo obrigatório ausente recebe 422.
- **CA-03 (RF-01, RF-07):** Dado arquivo maior que 5 MiB ou corpo maior que 5 MiB + 64 KiB, quando enviado, então o servidor retorna 413 sem chamar a IA.
- **CA-04 (RF-02):** Dada a tela de envio com imagem escolhida, quando outra imagem válida é selecionada, então a prévia muda; se a nova seleção falhar na validação do navegador, a análise fica desabilitada e o erro é informado. Dado dispositivo compatível, quando acionado “Tirar foto”, então o seletor nativo oferece captura; em outros dispositivos, não se exige câmera embutida na página.
- **CA-05 (RF-03):** Dada imagem validada, banco disponível e provedor operacional com credencial válida, quando solicitada análise, então a API chama IA real e valida objeto, material, indicador inconclusivo e observação antes de retornar; saída inválida não é exibida como resultado. Não há campo de probabilidade de confiança.
- **CA-06 (RF-04):** Dado material misto/desconhecido ou indicador inconclusivo verdadeiro, quando o resultado é processado, então a resposta é inconclusiva, sem orientação específica da base, e a interface orienta tentar foto melhor ou consultar serviço local.
- **CA-07 (RF-05):** Dado resultado não inconclusivo com orientação cadastrada, quando consultado, então o usuário recebe orientação, cuidados, fonte e data provenientes do banco e aviso de orientação geral provisória.
- **CA-08 (RF-06):** Dado resultado não inconclusivo sem registro correspondente, quando retornado, então os campos de orientação permanecem nulos e a interface informa “Orientação não cadastrada”.
- **CA-09 (RF-07, RQ-03):** Dado erro de provedor ou configuração, quando solicitada análise, então o usuário recebe mensagem de erro e pode tentar novamente, sem resultado fictício. No Gemini, chave ausente/recusada, cota e alta demanda tratadas retornam 503; resposta inválida/bloqueada ou outros erros HTTP tratados retornam 502. A verificação prévia do banco pode retornar 503, e a inicialização falha se o banco estiver inacessível.
- **CA-10 (RF-07, RQ-03):** Dada análise em andamento, quando o usuário aguarda, então há mensagem de processamento e o envio permanece desabilitado; timeout externo tratado retorna 504, e cancelamento da espera pelo navegador informa demora.
- **CA-11 (RF-08):** Dado resultado exibido, quando acionada nova análise, então a tela de envio é aberta com foto e resultado atuais limpos.
- **CA-12 (RF-09):** Dadas análises concluídas nesta visita, quando o usuário abre o início, então pode consultar as cinco respostas mais recentes; quando recarrega a página, então o histórico é perdido e nenhuma foto integra esse histórico.
- **CA-13 (RF-10):** Dado banco acessível, quando consultado `GET /api/health`, então retorna 200 com `status=ok`, `database=connected` e indicador de presença de chave; isso não implica disponibilidade do modelo nem saldo/cota.
- **CA-14 (RQ-01):** Dado uso da aplicação, quando a foto é enviada para análise, então o aviso de envio externo está disponível, credenciais não integram o frontend e a foto não é persistida pelo código da aplicação. Isso não promete retenção zero no provedor externo.
- **CA-15 (RQ-02):** Dado uso em viewport móvel/desktop ou por teclado/leitor de tela, quando o usuário percorre envio, processamento, erro e resultado, então controles têm rótulos e foco visível, a mudança de tela leva foco ao título e mensagens usam mecanismos acessíveis. A aprovação visual e de acessibilidade depende de verificação manual ainda não concluída.

## 8. Evidências de verificação e estado de aceitação

Execução nesta revisão, em 15/10/2026, no ambiente local:

| Verificação | Comando a partir da pasta indicada | Resultado observado |
|---|---|---|
| Backend, incluindo roundtrip PostgreSQL | Em `backend`: `TEST_DATABASE_URL=postgresql+psycopg://ecomigo:ecomigo@localhost:55432/ecomigo_test ../.venv/bin/python -m pytest -q` | 33 aprovados em 1,45 s; nenhum pulado |
| Build frontend | Em `frontend`: `npm run build` | TypeScript e Vite concluídos, código de saída 0 |
| Banco da aplicação, leitura de schema/material | Inspeção SQLAlchemy de `orientacoes` e SELECT de material | Uma tabela: `orientacoes`; quatro materiais: metal, papel, plastico, vidro |

As credenciais de banco acima são as de desenvolvimento fornecidas no exemplo do projeto. Nenhuma chave de IA foi copiada para esta documentação.

A suíte usa SQLite isolado para testes de API, mocks explícitos na fronteira dos provedores e um teste de leitura/escrita com rollback no PostgreSQL dedicado. Não é teste de qualidade do modelo nem teste completo de navegador. Não foi feita nova chamada paga/gratuita ao modelo nesta revisão documental.

Registros anteriores em `docs/VALIDACAO.md` relatam chamada Gemini válida com imagem branca e indisponibilidade posterior por alta demanda. Não comprovam classificação real de um resíduo. Os 15 casos em `docs/AVALIACAO-IA.md` permanecem pendentes. Faltam testes automatizados específicos para parte dos critérios, incluindo câmera, histórico, teclado, dimensões extremas e banco indisponível. Build e testes aprovados não significam aceite de todos os critérios.

## 9. Pendências e revisão

A revisão está em `checklists/requirements.md`. Permanecem abertas a adequação ao modelo original do kit, a autoridade de validação das orientações, o limiar de qualidade da IA, o aceite visual/acessível e a necessidade de deploy para avaliação acadêmica. Não há aprovação do PO registrada.

Por instrução do usuário, a produção de `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/openapi.yaml`, `tasks.md` e `traceability.md` está suspensa até as respectivas autorizações. Nenhum requisito futuro é considerado implementado apenas por estar documentado.

### Atualização de andamento — após conferência da etapa inicial

Em 15/10/2026, o usuário autorizou elaborar e revisar o plano. Foram preparados `plan.md` e os documentos de apoio `research.md`, `data-model.md`, `quickstart.md` e `contracts/openapi.yaml`. A suspensão registrada acima descreve o ponto de parada anterior; agora permanece apenas para a etapa de tarefas/rastreabilidade até nova autorização. As perguntas abertas não receberam respostas específicas, e não foi declarada aprovação do PO.
