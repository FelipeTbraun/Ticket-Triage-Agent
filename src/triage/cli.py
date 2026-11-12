import argparse
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

from triage.classifier import ErroClassificacao, classificar
from triage.loader import carregar_chamados
from triage.providers.base import ErroProvedor, ProvedorIA
from triage.report import gerar_relatorio
from triage.storage import conectar, ids_classificados, listar, salvar

CSV_PADRAO = "data/tickets_sample.csv"
DB_PADRAO = "data/triage.db"
PAUSA_GEMINI = 4.0  # segundos entre chamadas, para respeitar o limite por minuto


def criar_provedor(nome: str) -> ProvedorIA:
    if nome == "fake":
        from triage.providers.fake import FakeProvider

        return FakeProvider()
    from triage.providers.gemini import GeminiProvider

    return GeminiProvider()


def cmd_run(args: argparse.Namespace) -> int:
    chamados, erros_csv = carregar_chamados(Path(args.csv))
    for erro in erros_csv:
        print(f"[aviso] {erro}")

    conn = conectar(args.db)
    ja_feitos = set() if args.reprocessar else ids_classificados(conn)
    pendentes = [c for c in chamados if c.id not in ja_feitos]
    if args.limite:
        pendentes = pendentes[: args.limite]

    if not pendentes:
        print("Nenhum chamado novo para classificar.")
        return 0

    try:
        provedor = criar_provedor(args.provider)
    except ErroProvedor as e:
        print(f"Erro: {e}")
        return 1

    pausa = args.pausa if args.pausa is not None else (0.0 if args.provider == "fake" else PAUSA_GEMINI)
    falhas: list[str] = []

    for i, chamado in enumerate(pendentes, start=1):
        try:
            resultado = classificar(chamado, provedor)
        except ErroClassificacao as e:
            falhas.append(f"#{chamado.id}: {e}")
            print(f"[{i}/{len(pendentes)}] #{chamado.id} FALHOU ({e})")
            continue
        salvar(conn, chamado, resultado)
        print(f"[{i}/{len(pendentes)}] #{chamado.id} {resultado.categoria.value} / {resultado.prioridade.value}")
        if i < len(pendentes) and pausa > 0:
            time.sleep(pausa)

    print(f"\nConcluído: {len(pendentes) - len(falhas)} classificados, {len(falhas)} falhas.")
    if falhas:
        print("Falhas (rode o comando de novo para tentar apenas os que faltam):")
        for f in falhas:
            print(f"  - {f}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    conn = conectar(args.db)
    texto = gerar_relatorio(listar(conn))
    saida = Path(args.saida) if args.saida else Path("reports") / f"relatorio-{datetime.now():%Y-%m-%d}.md"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(texto, encoding="utf-8")
    print(f"Relatório salvo em {saida}")
    return 0


def montar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="triage", description="Triagem de chamados de suporte com IA (projeto de estudos).")
    sub = parser.add_subparsers(dest="comando", required=True)

    run = sub.add_parser("run", help="classifica os chamados do CSV")
    run.add_argument("--csv", default=CSV_PADRAO)
    run.add_argument("--db", default=DB_PADRAO)
    run.add_argument("--provider", choices=["gemini", "fake"], default="gemini")
    run.add_argument("--pausa", type=float, default=None, help="segundos entre chamadas à IA")
    run.add_argument("--limite", type=int, default=None, help="classifica no máximo N chamados")
    run.add_argument("--reprocessar", action="store_true", help="classifica de novo os já feitos")
    run.set_defaults(func=cmd_run)

    rel = sub.add_parser("report", help="gera o relatório em Markdown")
    rel.add_argument("--db", default=DB_PADRAO)
    rel.add_argument("--saida", default=None)
    rel.set_defaults(func=cmd_report)

    return parser


def main(argv: list[str] | None = None) -> int:
    load_dotenv()
    args = montar_parser().parse_args(argv)
    return args.func(args)