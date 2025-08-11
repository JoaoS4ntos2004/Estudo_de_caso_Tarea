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
    for page in doc:
        pages_text.append(page.get_text("text"))
    full_text = clean_text("\n".join(pages_text))
    head = full_text[:1200]
    return {
        "path": str(Path(pdf_path)),
        "file_name": Path(pdf_path).name,
        "text": full_text,
        "head": head,
    }

def run_extract(input_dir: str, output_jsonl: str) -> None:
    out_dir = Path(output_jsonl).parent
    out_dir.mkdir(parents=True, exist_ok=True)
    pdfs = sorted([str(p) for p in Path(input_dir).glob("*.pdf")])
    with open(output_jsonl, "w", encoding="utf-8") as out:
        for f in pdfs:
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
