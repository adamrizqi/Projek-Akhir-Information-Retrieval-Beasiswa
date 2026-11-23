import re
import math
import json
from collections import Counter, defaultdict

STOPWORDS = {
    "yang", "untuk", "pada", "ke", "para", "namun", "menurut", "antara", "dia", "dua",
    "ia", "seperti", "jika", "sehingga", "kembali", "dan", "ini", "karena", "oleh",
    "saat", "olehnya", "kepadanya", "tentang", "adalah", "bahwa", "dalam", "atas",
    "kemudian", "dengan", "akan", "juga", "dari", "ada", "mereka", "sudah", "saya",
    "anda", "kami", "kita", "bisa", "dapat", "setelah", "sebelum", "serta", "yaitu",
    "yakni", "bagi", "secara", "suatu", "hanya", "ia", "tersebut", "terhadap", "maupun",
    "hal", "lain", "lainnya", "harus", "bahkan", "sampai", "kemudian", "begitu",
    "sebagai", "selama", "terkait", "sebagaimana", "masing", "tertentu", "maka",
    "yaitu", "pun", "apabila", "dimana", "sebuah", "adanya", "itu", "inilah", "tersebut",
    "pula", "begitupun", "agaknya", "agar", "supaya", "hendak", "dimaksud", "bila",
    "kala", "lagi", "kelak", "sini", "situ", "sana", "amat",
    "selalu", "sering", "terkadang", "kadangkala", "biasanya", "terus", "tentu"
}

class Stemmer:
    prefixes = ["meng", "meny", "men", "mem", "me", "peng", "peny", "pen", "pem", "pe", "ber", "ter", "di", "ke", "se"]
    suffixes = ["nya", "lah", "kah", "pun", "kan", "an", "i"]
    
    protected = {
        "ipk", "s1", "s2", "s3", "d3", "d4", "sma", "smk", "sktm", "pkn", "stan",
        "ptn", "pts", "semester", "smt", "ekonomi", "beasiswa", "gratis", "prestasi",
        "kip", "mampu", "kurang", "penghasilan"
    }

    @classmethod
    def stem(cls, word):
        if not word or len(word) <= 3 or word in cls.protected:
            return word
        
        for suf in cls.suffixes:
            if word.endswith(suf) and len(word) - len(suf) >= 3:
                word = word[:-len(suf)]
                break
                
        for pref in cls.prefixes:
            if word.startswith(pref) and len(word) - len(pref) >= 3:
                word = word[len(pref):]
                break
                
        return word

def jaccard_similarity(query_tokens, doc_tokens):
    q_set = set(query_tokens)
    d_set = set(doc_tokens)
    intersection = q_set.intersection(d_set)
    union = q_set.union(d_set)
    return len(intersection) / len(union) if union else 0.0

def dice_similarity(query_tokens, doc_tokens):
    q_set = set(query_tokens)
    d_set = set(doc_tokens)
    intersection = q_set.intersection(d_set)
    total = len(q_set) + len(d_set)
    return (2 * len(intersection)) / total if total > 0 else 0.0

def overlap_similarity(query_tokens, doc_tokens):
    q_set = set(query_tokens)
    d_set = set(doc_tokens)
    intersection = q_set.intersection(d_set)
    min_len = min(len(q_set), len(d_set))
    return len(intersection) / min_len if min_len > 0 else 0.0

def build_bow(doc_tokens, vocab):
    return [doc_tokens.count(word) for word in vocab]

class Preprocessor:
    def __init__(self, use_stemming=True, remove_stopwords=True):
        self.use_stemming = use_stemming
        self.remove_stopwords = remove_stopwords
        self.stemmer = Stemmer()

    def tokenize(self, text):
        if not text:
            return []
        
        # 1. case folding
        text = text.lower()
        
        # 2. normalisasi angka desimal (koma jadi titik)
        text = re.sub(r'(\d+),(\d+)', r'\1.\2', text)
        
        # 3. hapus tanda baca kecuali titik pada angka
        text = re.sub(r'[^a-z0-9\.]', ' ', text)
        text = re.sub(r'(?<!\d)\.|\.(?!\d)', ' ', text)
        
        # 4. tokenisasi
        tokens = text.split()
        
        # 5. stopword removal & stemming
        res = []
        for t in tokens:
            t = t.strip()
            if not t:
                continue
            if self.remove_stopwords and t in STOPWORDS:
                continue
            if self.use_stemming:
                t = self.stemmer.stem(t)
            res.append(t)
            
        return res

class TFIDFVectorSpaceModel:
    def __init__(self, title_weight=0.15, requirements_weight=0.85):
        self.preprocessor = Preprocessor()
        self.title_weight = title_weight
        self.requirements_weight = requirements_weight
        self.documents = []
        self.doc_tokens = []
        self.vocab = set()
        self.idf = {}
        self.doc_vectors = []
        self.doc_norms = []
        self.inverted_index = defaultdict(set)
        self.total_docs = 0

    def fit(self, documents):
        self.documents = documents
        self.total_docs = len(documents)
        self.doc_tokens = []
        df_counter = Counter()

        print(f"Indexing {self.total_docs} dokumen...")

        for idx, doc in enumerate(documents):
            title_text = doc.get("title", "")
            req_text = doc.get("requirements", "")
            cov_text = doc.get("coverage", "")
            doc_text = doc.get("documents", "")

            title_tokens = self.preprocessor.tokenize(title_text)
            req_tokens = self.preprocessor.tokenize(f"{req_text} {cov_text} {doc_text}")

            all_tokens = title_tokens + req_tokens
            self.doc_tokens.append((title_tokens, req_tokens))

            # buat inverted index
            unique_tokens = set(all_tokens)
            for t in unique_tokens:
                df_counter[t] += 1
                self.inverted_index[t].add(idx)

            self.vocab.update(unique_tokens)

        # hitung idf: log((N + 1) / (DF + 1)) + 1
        for term, df in df_counter.items():
            self.idf[term] = math.log((self.total_docs + 1.0) / (df + 1.0)) + 1.0

        # hitung vektor tf-idf dokumen
        self.doc_vectors = []
        self.doc_norms = []
        for title_tokens, req_tokens in self.doc_tokens:
            tf_title = Counter(title_tokens)
            tf_req = Counter(req_tokens)
            doc_terms = set(tf_title.keys()).union(set(tf_req.keys()))

            vector = {}
            norm_sq = 0.0

            for term in doc_terms:
                count_t = tf_title.get(term, 0)
                count_r = tf_req.get(term, 0)

                tf_t = (1.0 + math.log(count_t)) if count_t > 0 else 0.0
                tf_r = (1.0 + math.log(count_r)) if count_r > 0 else 0.0

                weighted_tf = (self.title_weight * tf_t) + (self.requirements_weight * tf_r)
                tfidf_val = weighted_tf * self.idf.get(term, 0.0)

                vector[term] = tfidf_val
                norm_sq += tfidf_val ** 2

            norm = math.sqrt(norm_sq)
            self.doc_vectors.append(vector)
            self.doc_norms.append(norm if norm > 0 else 1.0)

        print(f"Indexing selesai. Ukuran vocab: {len(self.vocab)} kata.")

    def search(self, query, top_k=10):
        query_tokens = self.preprocessor.tokenize(query)
        if not query_tokens:
            return []

        # vektor query
        query_tf = Counter(query_tokens)
        query_vec = {}
        query_norm_sq = 0.0
        for term, count in query_tf.items():
            if term in self.idf:
                tf_weight = 1.0 + math.log(count)
                val = tf_weight * self.idf[term]
                query_vec[term] = val
                query_norm_sq += val ** 2

        query_norm = math.sqrt(query_norm_sq)
        if query_norm == 0:
            return []

        # hitung cosine similarity
        scores = []
        for i in range(self.total_docs):
            doc_vec = self.doc_vectors[i]
            dot_product = 0.0
            matched_terms = []
            
            for term, q_val in query_vec.items():
                if term in doc_vec:
                    contrib = q_val * doc_vec[term]
                    dot_product += contrib
                    matched_terms.append((term, contrib))

            if dot_product > 0:
                cosine_sim = dot_product / (query_norm * self.doc_norms[i])
                scores.append({
                    "score": round(cosine_sim, 4),
                    "document": self.documents[i],
                    "matched_terms": sorted(matched_terms, key=lambda x: x[1], reverse=True),
                    "query_tokens": query_tokens
                })

        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores[:top_k]

def load_data(filepath="data/scholarships.json"):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    docs = load_data()
    vsm = TFIDFVectorSpaceModel()
    vsm.fit(docs)

    test_queries = [
        "semester 3 minimal ipk 3.25",
        "kondisi ekonomi kurang mampu sktm",
        "beasiswa s1 ptn semester 1",
        "beasiswa d3 politeknik full gratis"
    ]

    for q in test_queries:
        print(f"\nQuery: '{q}'")
        results = vsm.search(q, top_k=3)
        for rank, r in enumerate(results, 1):
            doc = r["document"]
            matched = [f"{t[0]} ({t[1]:.2f})" for t in r["matched_terms"][:4]]
            print(f"#{rank} [Score: {r['score']}] - {doc['title']} ({doc['source']})")
            print(f"   Matched: {', '.join(matched)}")
            print(f"   Syarat: {doc['requirements'][:150]}...\n")
