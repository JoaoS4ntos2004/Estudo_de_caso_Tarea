import os
from typing import List, Dict

TEMPLATE = (
    "Você é um assistente que responde de forma objetiva com base exclusivamente no CONTEXTO.\n"
    "Se não houver informação suficiente no contexto, admita claramente e peça para refinar.\n\n"
    "Pergunta: {query}\n\n"
    "CONTEXTOS (trechos relevantes):\n"
    "{contexts}\n\n"
    "Responda de forma clara e cite o(s) arquivo(s) quando útil.\n"
)

def _format_context(results: List[Dict], max_chars: int = 2000) -> str:
    ctxs, total = [], 0
    for r in results:
        frag = f"[{r['file_name']} | {r['tipo_documento']}] {r['text']}"
        if total + len(frag) > max_chars:
            break
        ctxs.append(frag)
        total += len(frag)
    return "\n---\n".join(ctxs) if ctxs else "(sem trechos relevantes)"

def answer_with_fallback(query: str, results: List[Dict]) -> str:
    contexts = _format_context(results)
    return TEMPLATE.format(query=query, contexts=contexts)

def try_local_llm(prompt: str) -> str:
    gpt4all_path = os.getenv("GPT4ALL_MODEL_PATH")
    if gpt4all_path:
        try:
            from gpt4all import GPT4All
            model = GPT4All(gpt4all_path)
            with model.chat_session():
                return model.generate(prompt, max_tokens=400)
        except Exception as e:
            return f"[Aviso] GPT4All falhou: {e}\n\n{prompt}"
    llama_path = os.getenv("LLAMA_MODEL_PATH")
    if llama_path:
        try:
            from llama_cpp import Llama
            llm = Llama(model_path=llama_path, n_ctx=4096)
            out = llm(prompt=prompt, max_tokens=400)
            return out.get("choices", [{}])[0].get("text", "").strip() or prompt
        except Exception as e:
            return f"[Aviso] llama-cpp falhou: {e}\n\n{prompt}"
    # Sem LLM local → devolve o prompt (resposta extrativa/sintética)
    return prompt
