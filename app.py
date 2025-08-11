
import os
import streamlit as st
from src.busca_index import search
from src.chat_llm import answer_with_fallback, try_local_llm
import subprocess

st.set_page_config(page_title="Estudo de Caso - PDFs", layout="wide")

st.title("📄 Estudo de Caso — PDFs")
st.caption("Extração • Classificação • Busca • Chat (LLM opcional)")

with st.sidebar:
    st.header("Índice")
    st.write("1) Coloque seus PDFs em `dados/`")
    if st.button("🏗️ (Re)Construir índice"):
        with st.spinner("Extraindo, classificando e indexando..."):
            code = os.system("python build_index.py")
            if code == 0:
                st.success("Índice reconstruído com sucesso!")
            else:
                st.error("Falha ao reconstruir o índice. Veja o log no terminal.")


st.subheader("🔎 Busca em linguagem natural")
query = st.text_input("Escreva sua pergunta", placeholder="Ex.: Quais são os princípios da educação da LDB?")
topk = st.slider("Top-K", 3, 12, 6)

if st.button("Buscar", type="primary") and query:
    with st.spinner("Buscando..."):
        results = search(query, k=topk, index_dir=".index")
        prompt = answer_with_fallback(query, results)
        answer = try_local_llm(prompt)
    st.markdown("### 🧠 Resposta")
    st.write(answer)
    st.markdown("### 📌 Trechos recuperados")
    for r in results:
        with st.expander(f"({r['score']:.3f}) {r['file_name']} — {r['tipo_documento']}"):
            st.write(r["text"])

st.divider()
st.caption("Dica: defina `GPT4ALL_MODEL_PATH` ou `LLAMA_MODEL_PATH` para usar um LLM local.")
