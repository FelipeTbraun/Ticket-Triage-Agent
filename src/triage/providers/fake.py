import json
import re

from triage.classifier import MARCADOR

# (palavras-chave, categoria, prioridade, ação). A primeira regra que casar vence.
# É uma heurística simples, só para testes e demonstração. Não é IA.
_REGRAS = [
    (("pedindo dinheiro", "extensão estranha", "ameaça"), "software", "critica",
     "Isolar o computador da rede e acionar a equipe de segurança."),
    (("banco de dados", "erro 500", "fora do ar"), "sistemas", "critica",
     "Verificar o serviço e o banco de dados imediatamente."),
    (("servidores", "backup"), "sistemas", "alta",
     "Verificar a sala e o estado dos servidores."),
    (("wi-fi", "wifi", "internet", "vpn", "ponto de rede", "rede"), "rede", "media",
     "Verificar o equipamento de rede da área afetada."),
    (("senha", "conta", "bloqueada", "acesso", "permissão", "e-mail"), "acesso", "media",
     "Verificar e ajustar a conta do usuário."),
    (("impressora", "imprimir"), "impressora", "baixa",
     "Verificar a fila de impressão e o equipamento."),
    (("computador", "notebook", "monitor", "mouse", "teclado", "tela", "projetor"), "hardware", "media",
     "Testar o equipamento e, se preciso, substituir."),
    (("instalar", "instalação", "programa", "office", "windows", "antivírus"), "software", "baixa",
     "Instalar ou corrigir o software solicitado."),
    (("sistema", "planilha"), "sistemas", "media",
     "Reproduzir o problema e verificar o sistema."),
]


class FakeProvider:
    """Provedor falso para testes e demonstração, sem chave e sem internet.

    Sem argumentos, classifica por palavras-chave. Com `respostas`, devolve
    (ou lança, se for uma exceção) cada item em sequência. Isso permite
    testar retry e tratamento de erro.
    """

    def __init__(self, respostas: list | None = None):
        self._respostas = list(respostas) if respostas is not None else None
        self.chamadas = 0

    def gerar(self, prompt: str) -> str:
        self.chamadas += 1
        if self._respostas is not None:
            item = self._respostas.pop(0)
            if isinstance(item, Exception):
                raise item
            return item
        return json.dumps(self._classificar_por_palavras(prompt), ensure_ascii=False)

    @staticmethod
    def _classificar_por_palavras(prompt: str) -> dict:
        texto = prompt.split(MARCADOR, 1)[-1]
        titulo = texto.split("Título:", 1)[-1].split("\n", 1)[0].strip()
        minusculo = texto.lower()
        for palavras, categoria, prioridade, acao in _REGRAS:
            if any(re.search(rf"\b{re.escape(p)}\b", minusculo) for p in palavras):
                return {"categoria": categoria, "prioridade": prioridade,
                        "resumo": titulo, "acao_sugerida": acao}
        return {"categoria": "outros", "prioridade": "baixa", "resumo": titulo,
                "acao_sugerida": "Entrar em contato com o usuário para entender o problema."}