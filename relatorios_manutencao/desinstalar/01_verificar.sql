-- PASSO 1 (só leitura): mostra o que existe no banco antes de remover qualquer coisa.
-- phpMyAdmin → selecione o banco → aba SQL → cole e execute. Nada é alterado.
--
-- Coluna "situacao":
--   'DO APP DE RELATORIOS'  → tabela criada pelo schema.sql; o passo 2 vai removê-la.
--   'ESTRUTURA DIFERENTE'   → tabela com o mesmo nome, mas não é a do app; o passo 2 NÃO mexe nela.

SELECT t.nome AS tabela,
       COALESCE(c.colunas_iguais, 0) AS colunas_iguais,
       COALESCE(c.colunas_total, 0)  AS colunas_total,
       COALESCE(i.TABLE_ROWS, 0)     AS linhas_aprox,
       CASE
         WHEN c.colunas_total IS NULL THEN 'NAO EXISTE'
         WHEN c.colunas_iguais = t.esperado AND c.colunas_total = t.esperado THEN 'DO APP DE RELATORIOS'
         ELSE 'ESTRUTURA DIFERENTE - NAO SERA REMOVIDA'
       END AS situacao
FROM (
  SELECT 'dc96_pendencias' AS nome, 6 AS esperado, 'id,relatorio_id,ordem,problema,solucao,responsavel' AS cols
  UNION ALL SELECT 'dc96', 6, 'relatorio_id,endereco,uso_principal,respostas,q11,checklist'
  UNION ALL SELECT 'fotos', 6, 'id,relatorio_id,secao,ordem,legenda,arquivo'
  UNION ALL SELECT 'problemas', 7, 'id,relatorio_id,ordem,quem,problema,localizacao,data_conclusao'
  UNION ALL SELECT 'relatorios', 8, 'id,tipo,bra,data_relatorio,condicao_geral,responsavel,criado_em,atualizado_em'
) t
LEFT JOIN (
  SELECT TABLE_NAME, COUNT(*) AS colunas_total,
         SUM(FIND_IN_SET(COLUMN_NAME, CASE TABLE_NAME
           WHEN 'dc96_pendencias' THEN 'id,relatorio_id,ordem,problema,solucao,responsavel'
           WHEN 'dc96' THEN 'relatorio_id,endereco,uso_principal,respostas,q11,checklist'
           WHEN 'fotos' THEN 'id,relatorio_id,secao,ordem,legenda,arquivo'
           WHEN 'problemas' THEN 'id,relatorio_id,ordem,quem,problema,localizacao,data_conclusao'
           WHEN 'relatorios' THEN 'id,tipo,bra,data_relatorio,condicao_geral,responsavel,criado_em,atualizado_em'
         END) > 0) AS colunas_iguais
  FROM information_schema.COLUMNS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME IN ('dc96_pendencias', 'dc96', 'fotos', 'problemas', 'relatorios')
  GROUP BY TABLE_NAME
) c ON c.TABLE_NAME = t.nome
LEFT JOIN information_schema.TABLES i ON i.TABLE_SCHEMA = DATABASE() AND i.TABLE_NAME = t.nome;

-- Tabelas de OUTROS sistemas que apontam (chave estrangeira) para as tabelas acima.
-- Se aparecer alguma linha aqui, NÃO rode o passo 2 e me avise.
SELECT TABLE_NAME AS tabela_que_depende, CONSTRAINT_NAME, REFERENCED_TABLE_NAME AS aponta_para
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = DATABASE()
  AND REFERENCED_TABLE_NAME IN ('dc96_pendencias', 'dc96', 'fotos', 'problemas', 'relatorios')
  AND TABLE_NAME NOT IN ('dc96_pendencias', 'dc96', 'fotos', 'problemas', 'relatorios');
