import csv
from pathlib import Path

from pydantic import ValidationError

from triage.models import Ticket


def carregar_chamados(caminho:Path) -> tuple[list[Ticket], list[str]]:
    "Retorna (chamados válidos, mensagens de erro das linhas inválidas)."""
    chamados =[]
    erros = []
    with open(caminho, encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        for numero, linha in enumerate(leitor, start=2):
            try:
                chamado = Ticket(**linha)
            except ValidationError as e:
                ...
            else:
                ...

    return chamados,erros