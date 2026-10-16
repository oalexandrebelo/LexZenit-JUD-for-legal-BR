"""SaaS B2B sintético: busca vetorial sobre documentos do cliente e resposta com LLM."""
from anthropic import Anthropic

client = Anthropic()


def responder(pergunta: str, trechos: list[str]) -> str:
    # similarity_search no pgvector devolve os trechos; o modelo responde com base neles
    msg = client.messages.create(model="modelo-exemplo", max_tokens=512,
                                 messages=[{"role": "user", "content": pergunta + "\n" + "\n".join(trechos)}])
    return msg.content[0].text


CAMPOS_USUARIO = ["email", "full_name"]
