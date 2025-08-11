import re
import json

def heuristic_classify(title_or_firstpage: str) -> str:
    t = title_or_firstpage.lower()
    if re.search(r"\b(lei|lei nº|lei n°)\b", t):
        return "Lei"
    if re.search(r"\b(portaria|portaria nº|portaria n°)\b", t):
        return "Portaria"
    if re.search(r"\b(resolução|resolucao|resolução nº|resolução n°)\b", t):
        return "Resolução"
    return "Outros"

def add_classification(in_jsonl: str, out_jsonl: str):
    with open(in_jsonl, "r", encoding="utf-8") as fin, \
         open(out_jsonl, "w", encoding="utf-8") as fout:
        for line in fin:
            rec = json.loads(line)
            label = heuristic_classify((rec.get("head") or rec.get("text",""))[:4000])
            rec["tipo_documento"] = label
            fout.write(json.dumps(rec, ensure_ascii=False) + "\n")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--in_jsonl", default=".index/raw_text.jsonl")
    ap.add_argument("--out_jsonl", default=".index/with_labels.jsonl")
    args = ap.parse_args()
    add_classification(args.in_jsonl, args.out_jsonl)
