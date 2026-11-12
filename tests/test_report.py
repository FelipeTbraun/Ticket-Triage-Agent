from datetime import datetime

from triage.report import gerar_relatorio

AGORA = datetime(2026, 11, 12, 9, 0)


def _reg(id, prioridade="media", categoria="rede", titulo="t", acao="a"):
    return {
        "ticket_id": id, "titulo": titulo, "categoria": categoria, "prioridade": prioridade,
        "resumo": f"resumo {id}", "acao_sugerida": acao, "data_abertura": "2026-11-04",
    }


def test_relatorio_vazio():
    texto = gerar_relatorio([], gerado_em=AGORA)
    assert "Nenhum chamado classificado" in texto


def test_relatorio_tem_secoes_e_contagens():
    regs = [_reg(1, "critica"), _reg(2, "media"), _reg(3, "media", "hardware")]
    texto = gerar_relatorio(regs, gerado_em=AGORA)
    assert "Total de chamados classificados: 3" in texto
    assert "## Por prioridade" in texto
    assert "| media | 2 |" in texto
    assert "| rede | 2 |" in texto
    assert "Gerado em: 2026-11-12 09:00" in texto


def test_criticos_aparecem_em_atencao_imediata():
    texto = gerar_relatorio([_reg(1, "critica", titulo="Servidor caiu"), _reg(2, "baixa")], gerado_em=AGORA)
    secao = texto.split("## Atenção imediata")[1].split("## Todos")[0]
    assert "Servidor caiu" in secao
    assert "| 2 |" not in secao


def test_sem_urgentes_mostra_mensagem():
    texto = gerar_relatorio([_reg(1, "baixa")], gerado_em=AGORA)
    assert "Nenhum chamado crítico" in texto


def test_barra_vertical_no_texto_nao_quebra_a_tabela():
    texto = gerar_relatorio([_reg(1, "critica", acao="reiniciar | verificar")], gerado_em=AGORA)
    assert "reiniciar \\| verificar" in texto