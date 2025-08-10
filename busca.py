import sys
from src.index_search import search
from src.chat_llm import answer_with_fallback, try_local_llm

def main():
    if len(sys.argv) < 2:
        print("Uso: python search_cli.py \"sua pergunta\"")
        sys.exit(1)
    query = sys.argv[1]
    results = search(query, k=6, index_dir=".index")
    prompt = answer_with_fallback(query, results)
    answer = try_local_llm(prompt)
    print("\n=== RESPOSTA ===\n")
    print(answer)
    print("\n=== TOP TRECHOS ===\n")
    for r in results:
        print(f"- ({r['score']:.3f}) {r['file_name']} [{r['tipo_documento']}]")
        print(r["text"][:400].replace("\n"," ") + "...")
        print()

if __name__ == "__main__":
    main()
