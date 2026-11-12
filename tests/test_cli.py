import shutil
from pathlib import Path

from triage.cli import main
from triage.storage import conectar, listar

CSV_EXEMPLO = Path(__file__).parent.parent / "data" / "tickets_sample.csv"


def test_run_com_provedor_falso_classifica_tudo(tmp_path, capsys):
    db = tmp_path / "t.db"
    codigo = main(["run", "--provider", "fake", "--csv", str(CSV_EXEMPLO), "--db", str(db)])
    assert codigo == 0
    assert len(listar(conectar(db))) == 50
    assert "50 classificados, 0 falhas" in capsys.readouterr().out


def test_run_de_novo_nao_reprocessa(tmp_path, capsys):
    db = tmp_path / "t.db"
    args = ["run", "--provider", "fake", "--csv", str(CSV_EXEMPLO), "--db", str(db)]
    main(args)
    capsys.readouterr()
    main(args)
    assert "Nenhum chamado novo" in capsys.readouterr().out


def test_limite_restringe_a_quantidade(tmp_path):
    db = tmp_path / "t.db"
    main(["run", "--provider", "fake", "--limite", "3", "--csv", str(CSV_EXEMPLO), "--db", str(db)])
    assert len(listar(conectar(db))) == 3


def test_report_gera_arquivo(tmp_path):
    db = tmp_path / "t.db"
    saida = tmp_path / "r" / "rel.md"
    main(["run", "--provider", "fake", "--csv", str(CSV_EXEMPLO), "--db", str(db)])
    assert main(["report", "--db", str(db), "--saida", str(saida)]) == 0
    assert "# Relatório de triagem" in saida.read_text(encoding="utf-8")


def test_gemini_sem_chave_da_erro_claro(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setattr("triage.cli.load_dotenv", lambda: None)
    codigo = main(["run", "--provider", "gemini", "--csv", str(CSV_EXEMPLO), "--db", str(tmp_path / "t.db")])
    assert codigo == 1
    assert "GEMINI_API_KEY" in capsys.readouterr().out