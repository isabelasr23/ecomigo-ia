# SPEC-001 — Identificação visual de resíduos

Status: proposta técnica da equipe, pendente de aprovação pelo Product Owner.
Data: 15/10/2026. Versão: 0.1.

## 1. Problema e evidências
O brief acadêmico fornecido solicita apoio à identificação de resíduos por fotografia. Fotografias não comprovam composição química nem reciclabilidade. Não foram fornecidos estudos de campo, entrevistas ou validação das orientações. O protótipo Figma APaI3wRJpnE9TIij5nkdfu possui telas de início, pesquisa por imagem e detalhes; ele constitui referência visual, não evidência de eficácia da IA.

## 2. Objetivo e resultado esperado
Permitir enviar uma imagem e receber identificação visual estimada, ressalvas e orientação cadastrada quando aplicável. Priorizar papel, plástico, metal e vidro. Nenhum resultado de IA é simulado na aplicação. A conclusão exige PostgreSQL conectado, credencial válida e jornada real verificada.

## 3. História prioritária
Como pessoa que deseja descartar um objeto, quero fotografá-lo e receber uma estimativa de material e uma orientação cadastrada para decidir meu próximo passo com atenção às regras locais.

## 4. Escopo
Inclui upload/câmera pelo seletor nativo, prévia, análise real por API, orientação do banco, resultados inconclusivos, erros e nova análise. Histórico efêmero das últimas cinco análises na memória da página. Exclui autenticação, recompensas, mapa, geolocalização, confirmação química, publicação automática e dados reais de pontos de coleta.

## 5. Entradas, saídas e fluxo
Entrada: multipart/form-data, campo imagem, JPEG/PNG, até 5 MiB, imagem estática, até 20 milhões de pixels. Saída: objeto, material enumerado, indicador inconclusivo, observação, orientação/cuidados/fonte/data ou null. Erros HTTP: 400 vazio, 413 tamanho, 415 formato, 422 campo ausente, 502 resposta inválida/serviço externo, 503 banco ou chave ausente, 504 timeout.

Fluxo: selecionar → validar tamanho/tipo no navegador → prévia → POST /api/analises → limitar corpo → decodificar e verificar imagem → remover metadados e reduzir dimensões → verificar banco → API multimodal → validar Pydantic → consultar orientação apenas se conclusivo → exibir resultado. Misto/desconhecido sempre inconclusivo. Uma hipótese sobre material comum também pode ser inconclusiva.

## 6. Requisitos funcionais
- F01: aceitar JPEG/PNG com limite e validação real no servidor; substituir imagem e mostrar erros acessíveis.
- F02: usar API real configurável, saída JSON estruturada, sem porcentagem de confiança. A IA não fornece descarte.
- F03: persistir e consultar orientações por material no PostgreSQL; seed idempotente, provisório, explicitamente identificado.
- F04: histórico apenas na memória desta visita, sem salvar imagens, nomes de arquivo ou identificadores pessoais no banco.
- F05: estados de envio, carregamento, erro, resultado, inconclusivo, orientação ausente e reanálise.

## 7. Critérios de aceitação
1. Dado um JPEG/PNG válido de até 5 MiB, quando selecionado, então a prévia aparece e a análise fica disponível.
2. Dado arquivo vazio, corrompido, disfarçado ou grande, quando enviado, então o servidor rejeita sem chamar IA.
3. Dado banco disponível e credencial válida, quando enviada foto válida, então a API real é chamada com timeout e saída validada.
4. Dado material comum estimado sem ambiguidade, quando houver orientação, então a resposta inclui os dados cadastrados e seu caráter provisório.
5. Dado material misto, desconhecido ou ambíguo, quando analisado, então exibe inconclusivo sem descarte categórico.
6. Dada orientação ausente, quando retornar identificação, então a interface informa a lacuna sem inventar conteúdo.
7. Dada indisponibilidade, recusa ou resposta inválida da IA, quando processada, então mostra erro e permite tentar novamente.
8. Dado uso por teclado/leitor de tela, quando houver mudança de tela, erro ou carregamento, então controles têm rótulos, foco visível e feedback acessível.
9. Dado resultado exibido, quando solicitada nova análise, então a foto e o resultado atuais são limpos.
10. Dado histórico desta visita, quando recarregar a página, então ele desaparece; nenhuma imagem é persistida.

## 8. Qualidade, riscos e decisões
Propostas da equipe: React/TypeScript/Vite com CSS, FastAPI/Pydantic/SQLAlchemy, PostgreSQL 16, OpenAI Responses API com modelo por variável. Schema e tratamento de recusas seguem documentação oficial consultada. Sem migrações complexas no MVP: create_all e seed para banco novo; alterações futuras precisam de migração revisada.

Riscos: classificação equivocada, material perigoso confundido com comum, orientações locais divergentes, custos e latência de IA, abuso de endpoint público. Prompt instrui abstinência para perigosos, mas não garante detecção. Orientações devem ser validadas antes de uso público. Não utilizar para decisões sobre resíduos perigosos. Antes de expor publicamente: HTTPS, limite de requisições/custos no gateway, domínio/CORS e política de privacidade. Imagens seguem para o provedor externo com store=false; isso não equivale a garantia de retenção zero do provedor.

Adaptações do Figma: sem barra de status iOS fictícia, sem login, saldos, recompensas ou pontos inventados; textos de descarte substituídos pelos dados do banco. Tela inicial baseada na abertura (12002:5423), pesquisa escura (12309:3986) e detalhes (12318:564); responsividade desktop adaptada. Assets originais locais e fonte Poppins. Outros materiais têm cor e rótulo, sem reutilizar indevidamente a lixeira de plástico. Fidelidade das telas completas não é declarada.

Verificação: consultar docs/VALIDACAO.md para comandos e resultados reais. Casos manuais de IA permanecem pendentes até execução com credencial.
