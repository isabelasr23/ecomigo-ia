# Modelo de dados existente — 001

15/10/2026. Fonte: `backend/app/database.py` e inspeção PostgreSQL registrada na revisão de especificação. Modelo técnico implementado; sem aprovação de negócio presumida.

## Persistência

Somente tabela `orientacoes`; entidade ORM `Guidance`.

| Coluna | Tipo PostgreSQL | Nulo | Restrições / semântica |
|---|---|---|---|
| id | INTEGER | Não | Chave primária, gerada pelo mecanismo de autoincremento do banco |
| material | VARCHAR(30) | Não | UNIQUE; chave de consulta, sem enum ou CHECK de domínio no banco |
| descricao | TEXT | Não | Descrição do material; não retornada pelo endpoint de análise |
| orientacao | TEXT | Não | Orientação geral cadastrada |
| cuidados | TEXT | Não | Ressalvas cadastradas |
| fonte | TEXT | Não | Fonte da orientação; retornada como fonte_orientacao |
| data_atualizacao | DATE | Não | Data fornecida pelo cadastro/seed; não é timestamp automático |

Não há chaves estrangeiras ou relacionamentos persistidos. Não há coluna de confiança, município, usuário, fotografia, histórico ou booleano provisório. `orientacao_provisoria=true` pertence ao schema de resposta, não à tabela.

## Dados iniciais e ciclo de vida

Seed existente para `papel`, `plastico`, `metal`, `vidro`; descrição e instruções em `SEEDS`. Fonte: “Base acadêmica Ecomigo — orientação geral provisória, pendente de validação local”. Data fixa do seed: 2026-10-15; não deve ser interpretada como validação por terceiro.

Startup executa create_all e insere cada material ausente em transação. Registros presentes não são atualizados. Não há endpoints de cadastro/edição/exclusão; nenhuma trilha de auditoria ou migração versionada está implementada. UNIQUE limita duplicatas por material; não há garantia de seed concorrente sem erro.

## Objetos transitórios

`Identification`: objeto (1–160 caracteres), material enumerado, identificacao_inconclusiva (booleano estrito), observacao (1–800 caracteres), sem campos extras. Misto/desconhecido forçam inconclusivo. `Analysis` acrescenta orientação/cuidados/fonte/data nullable e indicador provisório padrão true. Data de resposta é string ISO produzida pelo backend, sem format=date declarado no schema Pydantic.

O histórico é array de até cinco respostas em React, apagado ao recarregar a página. Arquivo e prévia existem durante a interação; não são registros SQL. O servidor processa bytes em memória e não grava fotografias pelo código da aplicação. Parser multipart pode usar arquivo temporário; “não persistir fotos” não significa ausência de qualquer buffer/temporário de infraestrutura.

## Pendências

Validar conteúdo local das orientações e eventual evolução de schema apenas após decisão. Não incluir tabelas novas para fazer o documento parecer completo. Qualquer alteração futura deverá considerar migração, integridade e validação; nenhuma realizada nesta etapa.
