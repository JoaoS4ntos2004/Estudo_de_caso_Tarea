import os
import json
from typing import List, Dict, Any, Tuple
from pathlib import Path
import numpy as np
import pandas as pd
from tqdm import tqdm
from sentence_transformers import SentenceTransformer
import faiss

DEFAULT_MODEL = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")

def chunk_text(text: str, max_chars: int = 900, overlap: int = 150) -> List[str]:
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + max_chars, n)
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap
        if start < 0: start = 0
        if start >= n: break
    return [c for c in chunks if c]

def build_index(in_jsonl: str, index_dir: str = ".index") -> None:
    os.makedirs(index_dir, exist_ok=True)
    rows = []
    with open(in_jsonl, "r", encoding="utf-8") as fin:
        for line in fin:
            rec = json.loads(line)
            doc_id = rec["path"]
            label = rec.get("tipo_documento", "Outros")
            text = rec["text"]
            chunks = chunk_text(text)
            for i, c in enumerate(chunks):
                rows.append({
                    "doc_id": doc_id,
                    "file_name": rec["file_name"],
                    "tipo_documento": label,
                    "chunk_id": f"{doc_id}::chunk_{i}",
                    "text": c
                })
    df = pd.DataFrame(rows)
    df_path = os.path.join(index_dir, "passages.parquet")
    df.to_parquet(df_path, index=False)

    model = SentenceTransformer(DEFAULT_MODEL)
    embs = model.encode(df["text"].tolist(), batch_size=64, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=True)
    dim = embs.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embs.astype(np.float32))
    faiss.write_index(index, os.path.join(index_dir, "index.faiss"))
    print(f"Index criado com {len(df)} chunks.")

def load_index(index_dir: str = ".index") -> Tuple[faiss.Index, pd.DataFrame]:
    index = faiss.read_index(os.path.join(index_dir, "index.faiss"))
    df = pd.read_parquet(os.path.join(index_dir, "passages.parquet"))
    return index, df

def search(query: str, k: int = 5, index_dir: str = ".index") -> List[Dict[str, Any]]:
    model = SentenceTransformer(os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2"))
    qv = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)
    index, df = load_index(index_dir)
    D, I = index.search(qv.astype(np.float32), k)
    results = []
    for rank, idx in enumerate(I[0]):
        row = df.iloc[idx]
        results.append({
            "rank": rank + 1,
            "score": float(D[0][rank]),
            "file_name": row["file_name"],
            "tipo_documento": row["tipo_documento"],
            "doc_id": row["doc_id"],
            "chunk_id": row["chunk_id"],
            "text": row["text"]
        })
    return results

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_jsonl", default=".index/with_labels.jsonl")
    ap.add_argument("--index_dir", default=".index")
    args = ap.parse_args()
    build_index(args.in_jsonl, args.index_dir)
