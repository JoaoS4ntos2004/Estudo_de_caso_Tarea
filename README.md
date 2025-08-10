# Estudo de Caso Tarea — Extração, Classificação, Busca e Chat sobre PDFs

Aplicação **local** para:
1) Ler e extrair texto de PDFs  
2) Classificar automaticamente por tipo de documento (Lei, Portaria, Resolução, Outros)  
3) Realizar **busca semântica** em linguagem natural  
4) Interagir com um **LLM local** para dúvidas/resumos usando o contexto dos PDFs


## 🧩 Stack
- **Extração**: [PyMuPDF]
- **Classificação**: regras + (opcional) modelo TF-IDF `scikit-learn`
- **Busca**: `sentence-transformers` (**all-MiniLM-L6-v2**) + `FAISS`
- **UI**: `Streamlit`
- **LLM**: `gpt4all` **OU** `llama-cpp-python` (se instalado)

> Se você não tiver um LLM local, o chat ainda funciona em **modo extrativo** (concatena trechos recuperados e gera uma resposta objetiva).


## 📦 Instalação

> Requer Python 3.10+

```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requerimentos.txt
```

### Modelos
- O modelo de embeddings **all-MiniLM-L6-v2** será baixado automaticamente
  (se preferir, baixe antes e aponte via variável `SENTENCE_TRANSFORMERS_HOME`).

### LLM local (opcional)
Escolha **um**:
- `pip install gpt4all`
  - Baixe um modelo `.gguf` pelo app do gpt4all e aponte `GPT4ALL_MODEL_PATH=/caminho/modelo.gguf`
- `pip install llama-cpp-python`
  - Aponte `LLAMA_MODEL_PATH=/caminho/modelo.gguf`

## 📁 Estrutura

```
case_estudo_pdf_app/
  src/
    extract_text.py
    classify.py
    index_search.py
    chat_llm.py
  data/
    pdfs/  # coloque aqui seus PDFs (Lei_*, Portaria_*, Resolução_* ...)
  app.py       # UI Streamlit
  build_index.py
  search_cli.py
  requirements.txt
  README.md
```

## ▶️ Como usar

1. **Coloque os PDFs** em `dados/`
2. **Crie/atualize o índice** (texto, classificação, embeddings):
```bash
python build_index.py
```
3. **Rodar a UI**:
```bash
streamlit run app.py
```
4. **Buscar pelo CLI (opcional)**:
```bash
python search_cli.py "Quais são os princípios da educação segundo a LDB?"
```

## ⚙️ Variáveis de ambiente (opcional)
- `EMBEDDING_MODEL_NAME` (default: `sentence-transformers/all-MiniLM-L6-v2`)
- `GPT4ALL_MODEL_PATH` (se usar gpt4all)
- `LLAMA_MODEL_PATH` (se usar llama-cpp)
- `INDEX_DIR` (default: `.index`)

## 🧪 Notas
- A classificação inicial usa **regras simples** (rápidas e transparentes). Se quiser, ative o modo ML no `classify.py`.
- O chat sempre tenta recuperar trechos relevantes primeiro (**RAG**). Se não houver LLM, a resposta é **sintética extrativa**.

## 📚 Referências (dos arquivos enviados)
- Roteiro: “Estudo de Caso”【19†source】
- Exemplo de PDF: “Lei 9.394/1996 (LDB)”【20†source】