from collections import Counter
from datetime import datetime

_ORDEM_PRIORIDADE = ["critica", "alta", "media", "baixa"]


def _celula(texto: str) -> str:
    """Deixa o texto seguro para uma célula de tabela Markdown."""
    return str(texto).replace("\n", " ").replace("|", "\\|")


def gerar_relatorio(registros, gerado_em: datetime | None = None) -> str:
    """Monta o relatório em Markdown a partir das linhas do banco."""
    gerado_em = gerado_em or datetime.now()
    registros = list(registros)

    linhas = [
        "# Relatório de triagem de chamados",
        "",
        f"Gerado em: {gerado_em.strftime('%Y-%m-%d %H:%M')}",
        f"Total de chamados classificados: {len(registros)}",
        "",
    ]

    if not registros:
        linhas.append("Nenhum chamado classificado ainda.")
        return "\n".join(linhas) + "\n"

    por_prioridade = Counter(r["prioridade"] for r in registros)
    linhas += ["## Por prioridade", "", "| Prioridade | Quantidade |", "|---|---|"]
    for p in _ORDEM_PRIORIDADE:
        linhas.append(f"| {p} | {por_prioridade.get(p, 0)} |")

    por_categoria = Counter(r["categoria"] for r in registros)
    linhas += ["", "## Por categoria", "", "| Categoria | Quantidade |", "|---|---|"]
    for categoria, qtd in sorted(por_categoria.items(), key=lambda x: (-x[1], x[0])):
        linhas.append(f"| {categoria} | {qtd} |")

    urgentes = sorted(
        (r for r in registros if r["prioridade"] in ("critica", "alta")),
        key=lambda r: (_ORDEM_PRIORIDADE.index(r["prioridade"]), r["ticket_id"]),
    )
    linhas += ["", "## Atenção imediata (críticos e altos)", ""]
    if urgentes:
        linhas += ["| ID | Prioridade | Categoria | Chamado | Ação sugerida |", "|---|---|---|---|---|"]
        for r in urgentes:
            linhas.append(
                f"| {r['ticket_id']} | {r['prioridade']} | {r['categoria']} | "
                f"{_celula(r['titulo'])} | {_celula(r['acao_sugerida'])} |"
            )
    else:
        linhas.append("Nenhum chamado crítico ou de prioridade alta.")

    linhas += ["", "## Todos os chamados", "", "| ID | Data | Categoria | Prioridade | Resumo |", "|---|---|---|---|---|"]
    for r in registros:
        linhas.append(
            f"| {r['ticket_id']} | {r['data_abertura']} | {r['categoria']} | "
            f"{r['prioridade']} | {_celula(r['resumo'])} |"
        )

    return "\n".join(linhas) + "\n"