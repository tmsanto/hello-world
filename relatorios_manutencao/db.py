"""Acesso ao banco: MySQL/MariaDB na hospedagem (DB_HOST definido) ou SQLite local.

As consultas usam "?" como marcador; no MySQL ele é trocado por "%s".
"""
import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "instance"))
SQLITE_PATH = os.path.join(DATA_DIR, "relatorios.db")
USA_MYSQL = bool(os.environ.get("DB_HOST"))

SCHEMA_SQLITE = """
CREATE TABLE IF NOT EXISTS relatorios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tipo TEXT NOT NULL,
    bra TEXT NOT NULL DEFAULT '',
    data_relatorio TEXT NOT NULL DEFAULT '',
    condicao_geral TEXT NOT NULL DEFAULT '',
    responsavel TEXT NOT NULL DEFAULT '',
    criado_em TEXT NOT NULL,
    atualizado_em TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS fotos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relatorio_id INTEGER NOT NULL REFERENCES relatorios(id) ON DELETE CASCADE,
    secao TEXT NOT NULL,
    ordem INTEGER NOT NULL,
    legenda TEXT NOT NULL DEFAULT '',
    arquivo TEXT
);
CREATE TABLE IF NOT EXISTS problemas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relatorio_id INTEGER NOT NULL REFERENCES relatorios(id) ON DELETE CASCADE,
    ordem INTEGER NOT NULL,
    quem TEXT NOT NULL DEFAULT '',
    problema TEXT NOT NULL DEFAULT '',
    localizacao TEXT NOT NULL DEFAULT '',
    data_conclusao TEXT NOT NULL DEFAULT ''
);
CREATE TABLE IF NOT EXISTS dc96 (
    relatorio_id INTEGER PRIMARY KEY REFERENCES relatorios(id) ON DELETE CASCADE,
    endereco TEXT NOT NULL DEFAULT '',
    uso_principal TEXT NOT NULL DEFAULT '',
    respostas TEXT NOT NULL DEFAULT '{}',
    q11 TEXT NOT NULL DEFAULT '{}',
    checklist TEXT NOT NULL DEFAULT '[]'
);
CREATE TABLE IF NOT EXISTS dc96_pendencias (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    relatorio_id INTEGER NOT NULL REFERENCES relatorios(id) ON DELETE CASCADE,
    ordem INTEGER NOT NULL,
    problema TEXT NOT NULL DEFAULT '',
    solucao TEXT NOT NULL DEFAULT '',
    responsavel TEXT NOT NULL DEFAULT ''
);
"""


class Banco:
    def __init__(self):
        if USA_MYSQL:
            import pymysql
            self.conn = pymysql.connect(
                host=os.environ["DB_HOST"],
                port=int(os.environ.get("DB_PORT", "3306")),
                user=os.environ["DB_USER"],
                password=os.environ.get("DB_PASSWORD", ""),
                database=os.environ["DB_NAME"],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
        else:
            os.makedirs(DATA_DIR, exist_ok=True)
            self.conn = sqlite3.connect(SQLITE_PATH)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON")

    def execute(self, sql, params=()):
        if USA_MYSQL:
            sql = sql.replace("?", "%s")
        cur = self.conn.cursor()
        cur.execute(sql, params)
        return cur

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()


def criar_tabelas():
    """Cria as tabelas se ainda não existirem (no MySQL, a partir de schema.sql)."""
    if USA_MYSQL:
        with open(os.path.join(BASE_DIR, "schema.sql"), encoding="utf-8") as f:
            comandos = [c.strip() for c in f.read().split(";")]
        banco = Banco()
        try:
            for c in comandos:
                linhas = [l for l in c.splitlines() if not l.strip().startswith("--")]
                if "".join(linhas).strip():
                    banco.execute("\n".join(linhas))
            banco.commit()
        finally:
            banco.close()
    else:
        os.makedirs(DATA_DIR, exist_ok=True)
        with sqlite3.connect(SQLITE_PATH) as conn:
            conn.executescript(SCHEMA_SQLITE)
