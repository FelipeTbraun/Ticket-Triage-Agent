import csv
from pathlib import Path

from pydantic import ValidationError

from triage.models import Ticket


def carregar_chamados(caminho: Path) -> tuple[list[Ticket], list[str]]:
    """Retorna (chamados válidos, mensagens de erro das linhas inválidas).

    Uma linha ruim não derruba a leitura: ela é reportada em `erros`
    e as demais continuam sendo carregadas.
    """
    chamados: list[Ticket] = []
    erros: list[str] = []

    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)

       
        for numero, linha in enumerate(leitor, start=2):
            try:
                chamado = Ticket(**linha)
            except ValidationError as e:
                primeiro = e.errors()[0]
                campo = ".".join(str(parte) for parte in primeiro["loc"]) or "?"
                erros.append(f"Linha {numero}: campo '{campo}' inválido ({primeiro['msg']})")
            except TypeError:
               
                erros.append(f"Linha {numero}: número de colunas incorreto")
            else:
                chamados.append(chamado)

    return chamados, erros