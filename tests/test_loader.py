from pathlib import Path

from triage.loader import carregar_chamados

CSV_EXEMPLO = Path(__file__).parent.parent / "data" / "tickets_sample.csv"
CABECALHO = "id,titulo,descricao,data_abertura\n"


def test_carrega_csv_de_exemplo_sem_erros():
    chamados, erros = carregar_chamados(CSV_EXEMPLO)
    assert len(chamados) == 50
    assert erros == []


def test_linha_com_data_invalida_e_reportada_sem_derrubar(tmp_path):
    arquivo = tmp_path / "t.csv"
    arquivo.write_text(
        CABECALHO
        + '1,Ok,"descrição boa",2026-11-04\n'
        + '2,Ruim,"data errada",04/11/2026\n'
        + '3,Ok de novo,"outra boa",2026-11-05\n',
        encoding="utf-8",
    )
    chamados, erros = carregar_chamados(arquivo)
    assert [c.id for c in chamados] == [1, 3]
    assert len(erros) == 1
    assert "Linha 3" in erros[0]
    assert "data_abertura" in erros[0]


def test_linha_com_colunas_a_mais_e_reportada(tmp_path):
    arquivo = tmp_path / "t.csv"
    arquivo.write_text(
        CABECALHO + "1,Ok,descrição, com vírgula sem aspas,2026-11-04\n",
        encoding="utf-8",
    )
    chamados, erros = carregar_chamados(arquivo)
    assert chamados == []
    assert "colunas" in erros[0]


def test_preserva_acentos(tmp_path):
    arquivo = tmp_path / "t.csv"
    arquivo.write_text(CABECALHO + '1,Não liga,"descrição",2026-11-04\n', encoding="utf-8")
    chamados, _ = carregar_chamados(arquivo)
    assert chamados[0].titulo == "Não liga"