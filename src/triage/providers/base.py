from typing import Protocol


class ErroProvedor(Exception):
    """Falha ao falar com o provedor de IA."""


class LimiteExcedido(ErroProvedor):
    """O provedor recusou por excesso de requisições (HTTP 429)."""


class ProvedorIA(Protocol):
    """Qualquer provedor precisa ter um método `gerar(prompt) -> str`.

    Para trocar de Gemini para outro serviço (ou para o Ollama),
    basta criar uma nova classe com este método.
    """

    def gerar(self, prompt: str) -> str: ...