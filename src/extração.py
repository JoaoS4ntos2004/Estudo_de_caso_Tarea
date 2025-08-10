import os
import re
import json
from typing import Dict, Any, List
import fitz  # PyMuPDF
from pathlib import Path

def clean_text(s: str) -> str:
    s = s.replace("\x0c", " ").replace("\r", " ")
    s = re.sub(r"[ \t]+", " ", s)
    s = re.sub(r"\n{2,}", "\n", s)
    return s.strip()

def extract_pdf_text(pdf_path: str) -> Dict[str, Any]:
    doc = fitz.open(pdf_path)
    pages_text: List[str] = []
    for i in range(len(doc)):
        page = doc[i]
        text = page.get_text("text")
        pages_text.append(text or "")
    full_text = clean_text("\n".join(pages_text))
    meta = doc.metadata or {}
    return {
        "file_name": os.path.basename(pdf_path),
        "path": str(Path(pdf_path).resolve()),
        "n_pages": len(doc),
        "metadata": meta,
        "text": full_text,
        "head": pages_text[0] if pages_text else ""
    }

def run_extract(input_dir: str, output_jsonl: str):
    files = [str(p) for p in Path(input_dir).glob("**/*.pdf")]
    os.makedirs(os.path.dirname(output_jsonl), exist_ok=True)
    with open(output_jsonl, "w", encoding="utf-8") as out:
        for f in files:
            try:
                rec = extract_pdf_text(f)
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")
                print(f"[OK] {f}")
            except Exception as e:
                print(f"[ERR] {f}: {e}")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--input_dir", default="dados", help="Pasta com PDFs")
    ap.add_argument("--output_jsonl", default=".index/raw_text.jsonl")
    args = ap.parse_args()
    run_extract(args.input_dir, args.output_jsonl)
