import sys
from ir_engine import TFIDFVectorSpaceModel, load_data

def main():
    print("=" * 60)
    print("SISTEM TEMU KEMBALI INFORMASI BEASISWA")
    print("Metode: TF-IDF & Vector Space Model (Cosine Similarity)")
    print("=" * 60)
    
    docs = load_data("data/scholarships.json")
    vsm = TFIDFVectorSpaceModel()
    vsm.fit(docs)
    
    print("\nMasukkan query (contoh: 'ipk 3.5 semester 3 kurang mampu')")
    print("Ketik 'exit' untuk keluar.\n")
    
    while True:
        try:
            query = input("Query > ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "q", "quit"]:
                break
                
            results = vsm.search(query, top_k=5)
            print(f"\nHasil Pencarian (Top {len(results)}):")
            if not results:
                print("Tidak ada hasil yang cocok.")
                continue
                
            for rank, r in enumerate(results, 1):
                doc = r["document"]
                terms = [f"{t[0]}:{t[1]:.2f}" for t in r["matched_terms"][:4]]
                print(f"#{rank} [Score: {r['score']:.4f}] {doc['title']}")
                print(f"   Sumber  : {doc['source']} ({doc['url']})")
                print(f"   Matched : {', '.join(terms)}")
                print(f"   Syarat  : {doc['requirements'][:160].replace(chr(10), ' ')}...")
                print("-" * 60)
            print()
        except (KeyboardInterrupt, EOFError):
            break

if __name__ == "__main__":
    main()
