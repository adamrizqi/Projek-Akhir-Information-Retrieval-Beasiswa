# Sistem Temu Kembali Informasi Beasiswa (TF-IDF & Vector Space Model)

Projek Akhir Mata Kuliah **Information Retrieval (Temu Kembali Informasi)**.

Sistem temu kembali informasi (IR) untuk mencari beasiswa berdasarkan kecocokan persyaratan (seperti semester, IPK, kondisi ekonomi, dan jenjang), mengimplementasikan materi praktikum IR minggu 3 hingga minggu 7.



```text
.
├── data/
│   ├── scholarships.json        # Dataset beasiswa (281 dokumen)
│   └── scholarships.csv         # Dataset format CSV
├── templates/
│   └── index.html               # Tampilan web antarmuka pencarian
├── ir_engine.py                 # Core engine preprocessing, similarity, TF-IDF, & VSM
├── scraper.py                   # Script crawling dan scraping beasiswa
├── search_cli.py                # Antarmuka pengujian terminal (CLI)
├── evaluate.py                  # Evaluasi Precision@5, Recall@5, F1@5, dan MAP
├── evaluation_report.md         # Laporan hasil evaluasi
└── app.py                       # Server web Flask
```

---

### A. Pengujian via Terminal (CLI)
```bash
python search_cli.py
```

Contoh query:
- `semester 3 minimal ipk 3.25`
- `kondisi ekonomi kurang mampu sktm`
- `beasiswa s1 ptn semester 1`
- `beasiswa d3 politeknik full gratis`

### B. Menjalankan Evaluasi Sistem (P@5, R@5, F1@5, MAP)
```bash
python evaluate.py
```

### C. Menjalankan Web Aplikasi (Flask)
```bash
python app.py
```
Buka browser pada alamat: `http://localhost:5000`
