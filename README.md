#  Challenge 1B – Persona-Driven Document Intelligence

This project extracts the most relevant sections from a group of PDFs using **semantic ranking**, based on a given **persona** and **task**. It is designed for Adobe’s “Connecting the Dots” Hackathon – Challenge 1B.

---

##  How It Works

- Accepts a `challenge1b_input.json` describing the persona, job-to-be-done, and list of PDFs
- Parses PDFs for layout-aware line-level content
- Uses **Sentence-BERT** model (`multi-qa-MiniLM-L6-cos-v1`) to rank sections most relevant to the persona and task
- Outputs:
  - Top sections with headings
  - Semantic-rich summaries for those sections

---

## Folder Structure

```
Challenge_1b/
├── main.py
├── Dockerfile
├── requirements.txt
├── Collection 1/
│   ├── PDFs/
│   ├── challenge1b_input.json
│   └── challenge1b_output.json (auto-generated)
├── Collection 2/
│   ├── PDFs/
│   ├── challenge1b_input.json
│   └── challenge1b_output.json (auto-generated)
├── Collection 3/
│   ├── PDFs/
│   ├── challenge1b_input.json
│   └── challenge1b_output.json (auto-generated)
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

Replace `Collection_1`, `Collection_2`, etc. as needed:

```bash
docker run --rm \
  -v $(pwd)/Collection_1:/app/Collection_1 \
  -v $(pwd)/Collection_2:/app/Collection_2 \
  -v $(pwd)/Collection_3:/app/Collection_3 \
  pdf-insights:latest
```

---

##  Local Testing (without Docker)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Script

```bash
python main.py
```

---

##  Output Format

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

##  Features

- **Semantic similarity** via `SentenceTransformer`
- **Heading detection** via layout heuristics
- **Parallel multi-document support**
- Outputs clean JSON ready for downstream applications

---

##  Requirements

In `requirements.txt`:

```text
numpy
PyMuPDF==1.23.3
sentence-transformers==2.2.2
```

---

## Customization

- Modify `TOP_K` and `CTX_LINES` in `main.py` to control how many sections are extracted and how much context to include.
- Customize heading detection rules for more precision depending on document styles.

---
