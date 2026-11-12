import os

from google import genai
from google.genai import errors, types

from triage.providers.base import ErroProvedor, LimiteExcedido

# Os nomes de modelo mudam com frequência. Confira o atual no Google AI Studio
# e, se precisar, defina GEMINI_MODEL no arquivo .env.
MODELO_PADRAO = "gemini-flash-latest"


class GeminiProvider:
    def __init__(self, api_key: str | None = None, modelo: str | None = None):
        api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ErroProvedor(
                "GEMINI_API_KEY não encontrada. Crie o arquivo .env a partir do .env.example."
            )
        self.modelo = modelo or os.getenv("GEMINI_MODEL") or MODELO_PADRAO
        self._client = genai.Client(api_key=api_key)

    def gerar(self, prompt: str) -> str:
        try:
            resposta = self._client.models.generate_content(
                model=self.modelo,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                ),
            )
        except errors.APIError as e:
            if getattr(e, "code", None) == 429:
                raise LimiteExcedido(str(e)) from e
            raise ErroProvedor(str(e)) from e

        texto = resposta.text
        if not texto:
            raise ErroProvedor("O modelo devolveu uma resposta vazia.")
        return texto