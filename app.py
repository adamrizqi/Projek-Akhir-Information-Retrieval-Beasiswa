import os
from flask import Flask, render_template, request, jsonify
from ir_engine import TFIDFVectorSpaceModel, load_data

app = Flask(__name__)

# inisialisasi data dan model vsm
docs = load_data("data/scholarships.json")
vsm = TFIDFVectorSpaceModel()
vsm.fit(docs)

@app.route("/")
def index():
    return render_template("index.html", total_docs=len(docs))

@app.route("/api/search", methods=["GET"])
def api_search():
    query = request.args.get("q", "").strip()
    jenjang = request.args.get("jenjang", "all").strip().lower()
    status_filter = request.args.get("status", "all").strip().lower()
    top_k = int(request.args.get("k", 15))

    if not query:
        return jsonify({"results": [], "query": "", "count": 0})

    raw_results = vsm.search(query, top_k=50)
    filtered = []

    for r in raw_results:
        doc = r["document"]

        # filter status pendaftaran
        if status_filter != "all":
            doc_status = doc.get("status", "").lower()
            if status_filter == "dibuka" and doc_status != "dibuka":
                continue
            if status_filter == "ditutup" and doc_status != "ditutup":
                continue

        # filter jenjang pendidikan
        if jenjang != "all":
            content_lower = (doc["title"] + " " + doc["requirements"]).lower()
            if jenjang == "d4":
                if "d4" not in content_lower and "diploma 4" not in content_lower:
                    continue
            elif jenjang not in content_lower:
                continue

        filtered.append({
            "id": doc["id"],
            "title": doc["title"],
            "source": doc["source"],
            "url": doc["url"],
            "status": doc.get("status", "Tidak Diketahui"),
            "deadline": doc.get("deadline", "-"),
            "score": r["score"],
            "matched_terms": [t[0] for t in r["matched_terms"][:5]],
            "requirements": doc.get("requirements", "")[:350] + ("..." if len(doc.get("requirements", "")) > 350 else ""),
            "full_requirements": doc.get("requirements", ""),
            "documents": doc.get("documents", ""),
            "coverage": doc.get("coverage", "")
        })

        if len(filtered) >= top_k:
            break

    return jsonify({
        "results": filtered,
        "query": query,
        "count": len(filtered),
        "query_tokens": vsm.preprocessor.tokenize(query)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
