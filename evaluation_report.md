# Laporan Evaluasi Kinerja Sistem Information Retrieval (TF-IDF & VSM)

## 1. Ringkasan Evaluasi
- **Ukuran Korpus**: 281 Dokumen Beasiswa Terindeks (data/scholarships.json)
- **Model IR**: Vector Space Model (VSM) dengan TF-IDF & Smoothed IDF
- **Field Weighting**: Persyaratan = **0.85**, Judul = **0.15**
- **Jumlah Skenario Query**: 8 Skenario Persyaratan Mahasiswa
- **Metrik Evaluasi**: Precision@5, Recall@5, F1-Score@5, Mean Average Precision (MAP)

---

## 2. Ringkasan Metrik Rata-rata

| Metrik Evaluasi | Nilai Rata-rata | Persentase |
| :--- | :---: | :---: |
| **Mean Precision@5** | **0.5500** | 55.0% |
| **Mean Recall@5** | **0.3613** | 36.1% |
| **Mean F1-Score@5** | **0.4199** | 42.0% |
| **Mean Average Precision (MAP)** | **0.4350** | 43.5% |

---

## 3. Detail Hasil per Skenario Query

| ID | Query | P@5 | R@5 | F1@5 | AP | Dokumen Relevan Terambil (Top 5) |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| Q1 | `semester 3 minimal ipk 3.25` | 0.4000 | 0.4000 | 0.4000 | 0.5954 | IND-056, IND-160 |
| Q2 | `kondisi ekonomi kurang mampu sktm penghasilan` | 0.6000 | 0.2727 | 0.3750 | 0.2799 | IND-212, IND-070, IND-146 |
| Q3 | `mahasiswa s1 ptn semester 5` | 0.2000 | 0.1667 | 0.1818 | 0.1430 | IND-171 |
| Q4 | `beasiswa d3 politeknik full gratis` | 0.6000 | 0.5000 | 0.5455 | 0.5061 | IND-074, IND-244, IND-058 |
| Q5 | `pendaftaran kip kuliah bantuan kuliah` | 0.8000 | 0.4444 | 0.5714 | 0.7068 | IND-202, IND-204, IND-205, IND-245 |
| Q6 | `prestasi akademik mahasiswa berprestasi ipk 3.50` | 0.4000 | 0.5000 | 0.4444 | 0.4167 | IND-078, IND-070 |
| Q7 | `bantuan ukt biaya hidup mahasiswa s1 semester 4` | 0.4000 | 0.2222 | 0.2857 | 0.1556 | IND-115, IND-020 |
| Q8 | `mahasiswa d4 s1 minimal ipk 3.00` | 1.0000 | 0.3846 | 0.5556 | 0.6765 | IND-201, IND-251, IND-260, IND-265, IND-008 |

---

## 4. Analisis Hasil

1. **Akurasi Top-5 (Precision@5 = 55.0%)**:
   - Sistem mampu menampilkan rata-rata 55% dokumen yang benar-benar relevan pada 5 urutan teratas.
   - Skenario dengan kata kunci jenjang dan nilai IPK spesifik (misalnya Q5 dan Q8) menghasilkan presisi tinggi (80% - 100%).

2. **Cakupan Relevansi (Recall@5 = 36.1%)**:
   - Nilai recall dibatasi oleh $K=5$, sedangkan ground truth beberapa skenario memiliki lebih dari 10 dokumen relevan.

3. **Peringkat Dokumen Relevan (MAP = 0.4350)**:
   - Skor MAP menunjukkan bahwa dokumen yang relevan cenderung berada pada ranking atas hasil pencarian berkat pembobotan TF-IDF dan Cosine Similarity.
