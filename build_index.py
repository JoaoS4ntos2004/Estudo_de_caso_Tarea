from src.extracao import run_extract
from src.classificacao import add_classification
from src.busca_index import build_index

if __name__ == "__main__":
    run_extract("dados/", ".index/raw_text.jsonl")
    add_classification(".index/raw_text.jsonl", ".index/with_labels.jsonl")
    build_index(".index/with_labels.jsonl", ".index")
    print("✅ Pipeline concluído.")
