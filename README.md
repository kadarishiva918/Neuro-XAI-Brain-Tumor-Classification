# 🧠 Neuro-XAI — Brain Tumor Classification Platform

An explainable AI (XAI) platform for brain tumor classification from MRI scans using deep learning. Built with a 7-step clinical analysis pipeline featuring Grad-CAM, SHAP, and LIME explainability.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Flask](https://img.shields.io/badge/Flask-Backend-green)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-black)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange)

---

## 📌 About the Project

Neuro-XAI is a full-stack AI medical diagnostic platform that classifies brain tumors from MRI images into 4 categories:

| Class | Description |
|-------|-------------|
| Glioma | Malignant brain tumor |
| Meningioma | Tumor in brain membranes |
| Pituitary | Tumor in pituitary gland |
| No Tumor | Healthy brain scan |

---

## ✨ Features

- 7-step clinical analysis pipeline
- 93% validation accuracy
- Grad-CAM, SHAP, LIME explainability
- Clinical report generation
- History logs
- User authentication
- Dark mode support

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js, TypeScript, TailwindCSS |
| Backend | Flask, Python |
| AI Model | TensorFlow, Keras CNN |
| Explainability | Grad-CAM, SHAP, LIME |

---

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js 18+
- Anaconda (recommended)
- Git

---

### Step 1 — Clone the Repository
```bash
git clone https://github.com/kadarishiva918/Neuro-XAI-Brain-Tumor-Classification.git
cd Neuro-XAI-Brain-Tumor-Classification
```

### Step 2 — Setup Backend
```bash
cd backend
pip install -r requirements.txt
```

### Step 3 — Train the Model (First Time Only)
```bash
python train_model.py
```
> ⚠️ This will create `models/brain_tumor_model.h5` — takes 2-5 hours on CPU

### Step 4 — Start Backend
```bash
python app.py
```
> Backend runs on http://localhost:5000

### Step 5 — Setup Frontend (New Terminal)
```bash
cd frontend
npm install
npm run dev
```
> Frontend runs on http://localhost:3000

---

## 📁 Project Structure
Neuro-XAI-Brain-Tumor-Classification/
├── backend/
│   ├── app.py              # Flask API
│   ├── train_model.py      # Model training script
│   ├── labels.py           # Class labels
│   ├── models/             # Saved model files
│   ├── uploads/            # Uploaded MRI images
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js pages
│   │   ├── components/     # UI components
│   │   └── lib/            # API utilities
│   └── package.json
├── README.md
└── start.bat               # Quick start script
---

## 📊 Model Performance

| Metric | Result |
|--------|--------|
| Best Validation Accuracy | 93% |
| Training Epochs | 15 |
| Image Size | 224x224 |
| Classes | 4 |

---

## 🗂️ Dataset

The model is trained on the Brain Tumor MRI Dataset containing 4 classes:
- **Glioma** — 1000+ images
- **Meningioma** — 1000+ images
- **Pituitary** — 1000+ images
- **No Tumor** — 1000+ images

---

## 🖥️ Screenshots

### Login Page
> Enter your name to access the platform

### Dashboard
> Overview of recent scans and statistics

### MRI Diagnostics
> Upload MRI scan and get 7-step analysis

### Clinical Report
> Download detailed PDF report of diagnosis

---

## ⚠️ Important Notes

- Always start **backend first**, then frontend
- Model file (`brain_tumor_model.h5`) is not included due to size — run `train_model.py` to generate it
- Requires minimum **8GB RAM** for training
- For best results use **clear MRI brain scan images**

---

## 👤 Author

**Kadari Shiva Kumar Yadav**
- GitHub: [@kadarishiva918](https://github.com/kadarishiva918)

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgements

- Brain Tumor MRI Dataset from Kaggle
- TensorFlow and Keras documentation
- Next.js documentation
- Flask documentation
