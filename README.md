# 🔍 Challenge 1B – Persona-Driven Document Intelligence

This project extracts the most relevant sections from a group of PDFs using **semantic ranking**, based on a given **persona** and **task**. It is designed for Adobe’s “Connecting the Dots” Hackathon – Challenge 1B.

---

## 🧠 How It Works

- Accepts a `challenge1b_input.json` describing the persona, job-to-be-done, and list of PDFs
- Parses PDFs for layout-aware line-level content
- Uses a **Sentence-BERT** model (`multi-qa-MiniLM-L6-cos-v1`) to semantically rank sections most relevant to the persona and task
- Outputs:
  - Top-ranked sections with headings
  - Semantic-rich summaries of those sections

---

## 📂 Folder Structure

```
Challenge_1b/
├── main.py
├── Dockerfile
├── requirements.txt
├── input/
│   ├── Collection 1/
│   │   ├── PDFs/
│   │   └── challenge1b_input.json
│   ├── Collection 2/
│   ├── Collection 3/
├── output/
│   ├── Collection 1/
│   │   └── challenge1b_output.json (auto-generated)
│   ├── Collection 2/
│   ├── Collection 3/
```

Each `challenge1b_input.json` should look like:

```json
{
  "persona": { "role": "Sustainability Consultant" },
  "job_to_be_done": { "task": "Find net-zero design practices in high-rise buildings" },
  "documents": [
    { "filename": "sample1.pdf" },
    { "filename": "sample2.pdf" }
  ]
}
```

---

## 🐳 Docker Setup

### 1. Build the Docker Image

```bash
docker build --platform linux/amd64 -t pdf-insights:latest .
```

### 2. Run the Container

Mount `input` and `output` folders:

```bash
docker run --rm \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  pdf-insights:latest
```

---

## 🧪 Local Testing (without Docker)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Script

```bash
python main.py
```

---

## 📤 Output Format

Each `challenge1b_output.json` includes:

```json
{
  "metadata": {
    "input_documents": [...],
    "persona": "Sustainability Consultant",
    "job_to_be_done": "Find net-zero design practices...",
    "processing_timestamp": "2025-07-28T12:34:56Z"
  },
  "extracted_sections": [
    {
      "document": "sample1.pdf",
      "section_title": "Sustainable Building Strategies",
      "importance_rank": 1,
      "page_number": 5
    }
  ],
  "subsection_analysis": [
    {
      "document": "sample1.pdf",
      "refined_text": "Sustainable Building Strategies use daylighting...",
      "page_number": 5
    }
  ]
}
```

---

## 🔧 Features

- **Semantic similarity** via `SentenceTransformer`
- **Layout-based heading detection**
- **Supports multiple collections in parallel**
- Clean JSON output for downstream pipelines

---

## 📦 Requirements

`requirements.txt`:

```text
numpy
PyMuPDF==1.23.3
sentence-transformers==2.2.2
```

---

## 🛠 Customization

- Modify `TOP_K` and `CTX_LINES` in `main.py` to tune the number of results and context lines.
- You can refine heading detection logic for your specific document style.

---

## ✅ Notes

- All inputs must be placed inside `/app/input/Collection_X/`
- All outputs will be written to `/app/output/Collection_X/`
- PDFs must reside in the same folder as the `challenge1b_input.json` under each collection

```bash
input/
└── Collection 1/
    ├── PDFs/
    └── challenge1b_input.json

output/
└── Collection 1/
    └── challenge1b_output.json
```

---
