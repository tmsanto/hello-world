-- PASSO 2: remove as tabelas criadas pelo schema.sql do app de relatórios (DC-96, fotográfico, problemas).
-- Rode o 01_verificar.sql antes e faça um backup do banco (phpMyAdmin → Exportar).
--
-- Segurança: cada tabela só é apagada se tiver EXATAMENTE as colunas que o app criou.
-- Uma tabela sua com o mesmo nome (ex.: "relatorios" do sistema do TM) é mantida e
-- aparece como "mantida" no resultado.

-- Filhas primeiro, por causa das chaves estrangeiras.
SET @tab = 'dc96_pendencias', @cols = 'id,relatorio_id,ordem,problema,solucao,responsavel', @n = 6;
SET @iguais = (SELECT COALESCE(SUM(FIND_IN_SET(COLUMN_NAME, @cols) > 0), 0) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = @tab);
SET @total  = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = @tab);
SET @sql = IF(@total = 0, CONCAT('SELECT ''', @tab, ': nao existe'' AS resultado'),
           IF(@iguais = @n AND @total = @n, CONCAT('DROP TABLE `', @tab, '`'),
              CONCAT('SELECT ''', @tab, ': MANTIDA (estrutura diferente, nao e do app)'' AS resultado')));
PREPARE passo FROM @sql; EXECUTE passo; DEALLOCATE PREPARE passo;

SET @tab = 'dc96', @cols = 'relatorio_id,endereco,uso_principal,respostas,q11,checklist', @n = 6;
SET @iguais = (SELECT COALESCE(SUM(FIND_IN_SET(COLUMN_NAME, @cols) > 0), 0) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = @tab);
SET @total  = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = @tab);
SET @sql = IF(@total = 0, CONCAT('SELECT ''', @tab, ': nao existe'' AS resultado'),
           IF(@iguais = @n AND @total = @n, CONCAT('DROP TABLE `', @tab, '`'),
              CONCAT('SELECT ''', @tab, ': MANTIDA (estrutura diferente, nao e do app)'' AS resultado')));
PREPARE passo FROM @sql; EXECUTE passo; DEALLOCATE PREPARE passo;

SET @tab = 'fotos', @cols = 'id,relatorio_id,secao,ordem,legenda,arquivo', @n = 6;
SET @iguais = (SELECT COALESCE(SUM(FIND_IN_SET(COLUMN_NAME, @cols) > 0), 0) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = @tab);
SET @total  = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = @tab);
SET @sql = IF(@total = 0, CONCAT('SELECT ''', @tab, ': nao existe'' AS resultado'),
           IF(@iguais = @n AND @total = @n, CONCAT('DROP TABLE `', @tab, '`'),
              CONCAT('SELECT ''', @tab, ': MANTIDA (estrutura diferente, nao e do app)'' AS resultado')));
PREPARE passo FROM @sql; EXECUTE passo; DEALLOCATE PREPARE passo;

SET @tab = 'problemas', @cols = 'id,relatorio_id,ordem,quem,problema,localizacao,data_conclusao', @n = 7;
SET @iguais = (SELECT COALESCE(SUM(FIND_IN_SET(COLUMN_NAME, @cols) > 0), 0) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = @tab);
SET @total  = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = @tab);
SET @sql = IF(@total = 0, CONCAT('SELECT ''', @tab, ': nao existe'' AS resultado'),
           IF(@iguais = @n AND @total = @n, CONCAT('DROP TABLE `', @tab, '`'),
              CONCAT('SELECT ''', @tab, ': MANTIDA (estrutura diferente, nao e do app)'' AS resultado')));
PREPARE passo FROM @sql; EXECUTE passo; DEALLOCATE PREPARE passo;

-- Por último a tabela principal.
SET @tab = 'relatorios', @cols = 'id,tipo,bra,data_relatorio,condicao_geral,responsavel,criado_em,atualizado_em', @n = 8;
SET @iguais = (SELECT COALESCE(SUM(FIND_IN_SET(COLUMN_NAME, @cols) > 0), 0) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = @tab);
SET @total  = (SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = @tab);
SET @sql = IF(@total = 0, CONCAT('SELECT ''', @tab, ': nao existe'' AS resultado'),
           IF(@iguais = @n AND @total = @n, CONCAT('DROP TABLE `', @tab, '`'),
              CONCAT('SELECT ''', @tab, ': MANTIDA (estrutura diferente, nao e do app)'' AS resultado')));
PREPARE passo FROM @sql; EXECUTE passo; DEALLOCATE PREPARE passo;

-- Conferência final: deve listar só tabelas que NÃO são do app (ou nada).
SELECT TABLE_NAME AS ainda_existe FROM information_schema.TABLES
WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN ('dc96_pendencias', 'dc96', 'fotos', 'problemas', 'relatorios');
