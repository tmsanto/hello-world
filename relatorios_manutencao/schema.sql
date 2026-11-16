-- Relatórios de Manutenção – estrutura do banco MySQL/MariaDB
-- Importe pelo phpMyAdmin (aba Importar) no banco criado para o app.
-- O app também cria estas tabelas sozinho na primeira execução, se elas não existirem.

CREATE TABLE IF NOT EXISTS relatorios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo VARCHAR(20) NOT NULL,                 -- 'fotografico' | 'problemas' | 'dc96'
    bra VARCHAR(50) NOT NULL DEFAULT '',
    data_relatorio VARCHAR(10) NOT NULL DEFAULT '',
    condicao_geral TEXT NOT NULL,
    responsavel VARCHAR(255) NOT NULL DEFAULT '',
    criado_em VARCHAR(16) NOT NULL,
    atualizado_em VARCHAR(16) NOT NULL,
    INDEX idx_relatorios_bra (bra),
    INDEX idx_relatorios_tipo (tipo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS fotos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    relatorio_id INT NOT NULL,
    secao VARCHAR(20) NOT NULL,                -- 'comodo' | 'pendencia'
    ordem INT NOT NULL,
    legenda VARCHAR(255) NOT NULL DEFAULT '',
    arquivo VARCHAR(64) NULL,
    CONSTRAINT fk_fotos_relatorio FOREIGN KEY (relatorio_id) REFERENCES relatorios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS problemas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    relatorio_id INT NOT NULL,
    ordem INT NOT NULL,
    quem VARCHAR(255) NOT NULL DEFAULT '',
    problema TEXT NOT NULL,
    localizacao VARCHAR(255) NOT NULL DEFAULT '',
    data_conclusao VARCHAR(10) NOT NULL DEFAULT '',
    CONSTRAINT fk_problemas_relatorio FOREIGN KEY (relatorio_id) REFERENCES relatorios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- DC-96: Avaliação das condições da propriedade (um registro por avaliação de BRA).
-- BRA, data e "Avaliado por" ficam em relatorios (bra, data_relatorio, responsavel).
CREATE TABLE IF NOT EXISTS dc96 (
    relatorio_id INT PRIMARY KEY,
    endereco VARCHAR(500) NOT NULL DEFAULT '',
    uso_principal VARCHAR(255) NOT NULL DEFAULT '',
    respostas TEXT NOT NULL,                   -- JSON: {"q1": "...", ..., "q10": "..."}
    q11 TEXT NOT NULL,                         -- JSON: {"barulho": "comentário", ...} (só os marcados)
    checklist TEXT NOT NULL,                   -- JSON: ["inc_extintores", ...] (itens verificados sem irregularidade)
    CONSTRAINT fk_dc96_relatorio FOREIGN KEY (relatorio_id) REFERENCES relatorios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dc96_pendencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    relatorio_id INT NOT NULL,
    ordem INT NOT NULL,
    problema TEXT NOT NULL,
    solucao TEXT NOT NULL,
    responsavel VARCHAR(20) NOT NULL DEFAULT '', -- 'usuarios' | 'ldc'
    CONSTRAINT fk_dc96_pend_relatorio FOREIGN KEY (relatorio_id) REFERENCES relatorios(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
