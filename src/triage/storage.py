import sqlite3
from datetime import datetime
from pathlib import Path

from triage.models import Classificacao, Ticket

_SCHEMA = """
CREATE TABLE IF NOT EXISTS classificacoes (
    ticket_id       INTEGER PRIMARY KEY,
    titulo          TEXT NOT NULL,
    descricao       TEXT NOT NULL,
    data_abertura   TEXT NOT NULL,
    categoria       TEXT NOT NULL,
    prioridade      TEXT NOT NULL,
    resumo          TEXT NOT NULL,
    acao_sugerida   TEXT NOT NULL,
    classificado_em TEXT NOT NULL
)
"""


def conectar(caminho: str | Path) -> sqlite3.Connection:
    if str(caminho) != ":memory:":
        Path(caminho).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute(_SCHEMA)
    conn.commit()
    return conn


def salvar(conn: sqlite3.Connection, ticket: Ticket, c: Classificacao) -> None:
    """Grava (ou substitui) a classificação de um chamado."""
    conn.execute(
        """
        INSERT OR REPLACE INTO classificacoes
            (ticket_id, titulo, descricao, data_abertura, categoria, prioridade,
             resumo, acao_sugerida, classificado_em)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            ticket.id,
            ticket.titulo,
            ticket.descricao,
            ticket.data_abertura.isoformat(),
            c.categoria.value,
            c.prioridade.value,
            c.resumo,
            c.acao_sugerida,
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()


def ids_classificados(conn: sqlite3.Connection) -> set[int]:
    linhas = conn.execute("SELECT ticket_id FROM classificacoes").fetchall()
    return {linha["ticket_id"] for linha in linhas}


def listar(conn: sqlite3.Connection) -> list[sqlite3.Row]:
    return conn.execute("SELECT * FROM classificacoes ORDER BY ticket_id").fetchall()