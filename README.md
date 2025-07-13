# 🧠 BebasDahh_Datathon

**KeloraAI: Predictive System for Trademark Application Success in Indonesia**

Repo untuk proyek KeloraAI yang menggunakan dataset PDKI, model CatBoost (text, sparse, image), dan pipeline multimodal untuk memprediksi apakah aplikasi merek dagang akan *Didaftar* atau *Ditolak*.

## 🚀 Installation & Requirements

Instalasi Rekomendasi:

```bash
git clone https://github.com/bebasdahh/BebasDahh_Datathon.git
cd BebasDahh_Datathon
pip install -r requirements.txt
```

`requirements.txt` mencakup:
- `catboost`
- `sentence-transformers`
- `transformers`
- `torch`, `timm`
- `pandas`, `numpy`
- `shap`, `scikit-learn`

---

## 🔧 Data & Notebook

- **Dataset**: Aplikasi merek dagang Indonesia (1988–2024), total 337.334 sampel, termasuk 87.424 logo.
- **Notebook utama**: `notebooks/notebook-bebas-dahh-pipelines-and-training.ipynb`
  - Proses preprocessing dan extraction embedding
  - Feature engineering: OHE kelas NICE, cosine similarity, gap waktu, statistik kelas
  - Training & evaluation CatBoost (text dense, text sparse, image)
  - Analisis SHAP

---

## 📊 Performance & Evaluation

| Model Variant                | F1-Score |
|-----------------------------|----------|
| **Image (DINOv2)**         | **0.9072** |
| Text Dense (Multilingual E5)| 0.8520 |
| Text Sparse (OpenSearch)   | 0.8511 |

- Pipeline berbasis visual (logo) menghasilkan akurasi tertinggi.
- SHAP menunjukkan bahwa fitur similarity dan time-gap paling berpengaruh.

---

## 🚧 Limitations & Bias

- Data tersedia hanya sampai 2024
- Logo hanya ada ~26% sampel → visual pipeline hanya bisa diaplikasikan sebagian
- Dataset tidak menyertakan alasan penolakan secara detail
- Ada class imbalance, gunakan F1-score khususnya untuk kelas minoritas

---

## 🔖 Citations

### 📄 Paper

```
@article{lynardi2024keloraai,
  title={KeloraAI: Sistem Open-source Prediksi Keberhasilan Aplikasi Merek Dagang menggunakan Embedding Based Semantic Retreival dan Visual Search Classification},
  author={Lynardi, G. T. R. P. and Syafitra, D. and Firdaus, H. A.},
  journal={Fakultas Ilmu Komputer, Universitas Indonesia},
  year={2024}
}
```

### 📄 Dataset

```
@article{lynardi2024keloraai,
  title={KeloraAI: Sistem Open-source Prediksi Keberhasilan Aplikasi Merek Dagang menggunakan Embedding Based Semantic Retreival dan Visual Search Classification},
  ...
}
```

---

## 📫 Contact & Resources

- **Authors**: Gibran Tegar R. P. Lynardi, Harish Azka Firdaus, Daffa Syafitra
- **Email**: gibran.tegar@ui.ac.id
- **GitHub**: https://github.com/bebasdahh/BebasDahh_Datathon
- **Dataset**: https://huggingface.co/datasets/gibranlynardi/dataset_aplikasi_merek_pdki
- **Model Cards**: https://huggingface.co/gibranlynardi/catboost_prediksi_aplikasi_merek
---

## 📌 License

Repo ini dilisensikan di bawah **Apache‑2.0** — silakan lihat `LICENSE` untuk detail.

