# अर्थ ArthaBot – Hindi Ambiguity Resolver

> **End-to-End NLP Project** | Fine-tuned Transformer for Hindi & Hinglish Ambiguity Detection  
> *Text Analytics and Natural Language Processing*

---

![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=flat&logo=python&logoColor=white)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=flat&logo=pytorch&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Transformers-FFD21E?style=flat&logo=huggingface&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?style=flat&logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18+-61DAFB?style=flat&logo=react&logoColor=black)
![Vite](https://img.shields.io/badge/Vite-5.0+-646CFF?style=flat&logo=vite&logoColor=white)

---

## What is ArthaBot?

ArthaBot is a full-stack NLP application that detects and explains **all 8 types of linguistic ambiguity** in Hindi and Hinglish sentences. Unlike simple API wrappers, ArthaBot trains a real transformer model (`bert-base-multilingual-cased`) on hand-annotated Hindi data and serves predictions through a REST API connected to a polished React frontend.

**You enter a Hindi or Hinglish sentence → the trained transformer classifies which ambiguity types are present → you see full explanations, all possible meanings, and the most likely interpretation.**

---

## Ambiguity Types Detected

| # | Type | Example in Hindi |
|---|------|-----------------|
| 1 | **Lexical Ambiguity** | *वो आम खाता है* – 'आम' = mango OR common |
| 2 | **Syntactic Ambiguity** | *राम और श्याम की बहन आई* – whose sister? |
| 3 | **Semantic Ambiguity** | *उसकी आँखें बोलती हैं* – literal or figurative? |
| 4 | **Pragmatic Ambiguity** | *पानी लाओ* – command, request, or plea? |
| 5 | **Referential Ambiguity** | *उसने उसे देखा* – who saw whom? |
| 6 | **Scope Ambiguity** | *सब लोग नहीं आए* – some or none? |
| 7 | **Phonological Ambiguity** | *Usne unhe choda* – transliteration ambiguity |
| 8 | **Morphological Ambiguity** | *खेला* – verb (played) or noun (a game)? |

---

## Project Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   ARTHABOT SYSTEM                       │
│                                                         │
│  ┌─────────────┐   HTTP POST    ┌───────────────────┐  │
│  │  React UI   │ ────────────►  │  FastAPI Server   │  │
│  │  Port 5173  │ ◄────────────  │    Port 8000      │  │
│  └─────────────┘   JSON resp.   └────────┬──────────┘  │
│                                          │             │
│                                          ▼             │
│                               ┌─────────────────────┐  │
│                               │  Fine-Tuned BERT    │  │
│                               │  mBERT + Classifier │  │
│                               │  (saved_model/)     │  │
│                               └─────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

**Backend (Python)**
- `transformers` – HuggingFace library for loading and fine-tuning BERT
- `torch` – PyTorch for model training and inference
- `fastapi` – REST API server
- `uvicorn` – ASGI server

**Model**
- Base: `bert-base-multilingual-cased` (178M parameters, 104 languages, includes Hindi)
- Task: Multi-label classification (8 binary outputs)
- Loss: `BCEWithLogitsLoss`
- Optimizer: `AdamW` (lr=2e-5, weight_decay=0.01)

**Frontend (JavaScript)**
- React 18 + Vite
- Lucide React icons
- No external UI library — pure inline styles

---

## Repository Structure

```
arthabot/
│
├── arthabot-backend/
│   ├── train_model.py          # Fine-tunes bert-base-multilingual-cased
│   ├── server.py               # FastAPI inference server
│   ├── requirements.txt        # Python dependencies
│   ├── frontend_App.jsx        # Copy this to React src/App.jsx
│   └── data/
│       └── training_data.json  # 25 hand-annotated Hindi/Hinglish examples
│
└── hindi-ambiguity-resolver/   # React frontend
    ├── src/
    │   ├── App.jsx             # Main React component
    │   └── main.jsx
    ├── index.html
    ├── package.json
    └── vite.config.js
```

---

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- ~4GB RAM
- Internet connection for first run (downloads ~700MB model weights)

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/your-username/arthabot.git
cd arthabot
```

---

### Step 2 — Backend Setup

```bash
cd arthabot-backend

# Install Python dependencies
pip install -r requirements.txt
```

---

### Step 3 — Train the Model

```bash
python train_model.py
```

**Expected output:**
```
============================================================
  ArthaBot — Transformer Training
  Model : bert-base-multilingual-cased
  Task  : Hindi/Hinglish Ambiguity Detection
============================================================

✓ Loaded 25 training examples
✓ Loading tokenizer: bert-base-multilingual-cased
✓ Loading model: bert-base-multilingual-cased
✓ Device: cpu

── Training for 15 epochs ──

  Epoch  1/15  |  Loss: 0.4821
  Epoch  2/15  |  Loss: 0.3914
  ...
  Epoch 15/15  |  Loss: 0.0812

✓ Model saved to ./saved_model/
✓ Training complete!
```

> Training takes **5–10 minutes on CPU**. If you have a CUDA GPU it will be under 1 minute.

---

### Step 4 — Start the API Server

```bash
python server.py
```

```
Loading model from saved_model
✓ Model loaded on cpu
INFO:     Uvicorn running on http://0.0.0.0:8000
```

> Keep this terminal running.

---

### Step 5 — Frontend Setup

Open a **second terminal:**

```bash
cd hindi-ambiguity-resolver

# Copy the updated App.jsx that calls localhost:8000
cp ../arthabot-backend/frontend_App.jsx src/App.jsx

# Install dependencies
npm install

# Start dev server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## API Reference

### `GET /`
Health check — returns model info.

```json
{
  "name": "ArthaBot API",
  "status": "running",
  "model": "bert-base-multilingual-cased (fine-tuned)",
  "task": "Hindi/Hinglish Ambiguity Detection"
}
```

---

### `POST /analyze`

**Request:**
```json
{
  "sentence": "वो आम खाता है"
}
```

**Response:**
```json
{
  "original_sentence": "वो आम खाता है",
  "language_detected": "Hindi",
  "ambiguity_found": true,
  "ambiguities": [
    {
      "type": "LEXICAL AMBIGUITY",
      "category": "Word-level",
      "explanation": "The word 'आम' has multiple meanings...",
      "severity": "high",
      "confidence_score": 0.87,
      "nlp_concept": "Polysemy / Homonymy"
    }
  ],
  "possible_meanings": [
    {
      "meaning_number": 1,
      "interpretation": "He eats mango.",
      "explanation": "Primary reading — 'आम' as fruit.",
      "context_clue": "Food/eating context supports this reading."
    }
  ],
  "resolved_most_likely": "He eats mango — most natural interpretation.",
  "confidence": "high",
  "linguistic_note": "Classic Hindi polysemy..."
}
```

---

## Model Details

| Property | Value |
|----------|-------|
| Base model | `bert-base-multilingual-cased` |
| Parameters | 178 million |
| Transformer layers | 12 |
| Hidden size | 768 |
| Attention heads | 12 |
| Task | Multi-label classification |
| Labels | 8 (one per ambiguity type) |
| Loss function | BCEWithLogitsLoss |
| Optimizer | AdamW (lr=2e-5) |
| Epochs | 15 |
| Prediction threshold | 0.35 (sigmoid) |
| Training examples | 25 hand-annotated sentences |

---

## Training Data Sample

The `data/training_data.json` contains 25 hand-annotated sentences:

```json
[
  {
    "sentence": "वो आम खाता है",
    "labels": [1, 0, 0, 0, 0, 0, 0, 0],
    "ambiguity_types": ["LEXICAL AMBIGUITY"],
    "language": "Hindi"
  },
  {
    "sentence": "राम और श्याम की बहन आई",
    "labels": [0, 1, 0, 0, 0, 0, 0, 0],
    "ambiguity_types": ["SYNTACTIC AMBIGUITY"],
    "language": "Hindi"
  },
  {
    "sentence": "Usne apni car mein unhe choda",
    "labels": [0, 0, 0, 1, 0, 0, 0, 0],
    "ambiguity_types": ["PRAGMATIC AMBIGUITY"],
    "language": "Hinglish"
  }
]
```

Label vector index → ambiguity type:
```
[0] Lexical  [1] Syntactic  [2] Semantic   [3] Pragmatic
[4] Referential  [5] Scope  [6] Phonological  [7] Morphological
```

---

## Limitations

- Small training dataset (25 examples) – accuracy improves significantly with more data
- Single-sentence analysis – no cross-sentence referential resolution
- CPU inference only by default – add `.to("cuda")` calls for GPU support
- Rule-based meaning generation – templates rather than generative explanations
