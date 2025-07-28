import os, re, json, fitz
from datetime import datetime
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
import numpy as np
from sentence_transformers import SentenceTransformer, util

MODEL_NAME = "multi-qa-MiniLM-L6-cos-v1"
TOP_K = 5
CTX_LINES = 4
model = SentenceTransformer(MODEL_NAME)

@dataclass
class Line:
    text: str
    page: int
    font_size: float
    bold: bool
    y0: float
    y1: float

@dataclass
class Section:
    heading: Line
    body: List[Line] = field(default_factory=list)

    def as_text(self) -> str:
        lines = [self.heading.text] + [l.text for l in self.body]
        return " ".join(lines)


def parse_lines(doc: fitz.Document) -> List[Line]:
    out: List[Line] = []
    for page_n in range(len(doc)):
        page = doc[page_n]
        for block in page.get_text("dict").get("blocks", []):
            if "lines" not in block:
                continue
            for line in block["lines"]:
                text = "".join(s["text"] for s in line["spans"]).strip()
                if not text:
                    continue
                spans = line["spans"]
                font_size = max(s["size"] for s in spans)
                bold = any(s["flags"] & 16 for s in spans)
                y0, y1 = line["bbox"][1], line["bbox"][3]
                out.append(Line(text, page_n + 1, font_size, bold, y0, y1))
    return out


def detect_headings(lines: List[Line]) -> List[int]:
    if not lines:
        return []
    fs_median = np.median([l.font_size for l in lines])
    indices = []
    for idx, l in enumerate(lines):
        is_numbered = bool(re.match(r"^\d+(\.\d+)*\s", l.text))
        is_upper = l.text.isupper() and len(l.text) <= 80
        large_font = l.font_size > fs_median * 1.15
        candidate = (large_font or l.bold or is_numbered or is_upper)
        if candidate and 4 < len(l.text) < 120:
            indices.append(idx)
    return indices


def build_sections(lines: List[Line], headings: List[int]) -> List[Section]:
    sections: List[Section] = []
    for i, h_idx in enumerate(headings):
        start = h_idx + 1
        end = headings[i + 1] if i + 1 < len(headings) else len(lines)
        body = lines[start: min(end, start + CTX_LINES)]
        sections.append(Section(lines[h_idx], body))
    return sections


def rank_sections(sections: List[Section], query: str, top_k: int = TOP_K) -> List[Tuple[int, float]]:
    if not sections:
        return []
    corpus = [s.as_text() for s in sections]
    corpus_emb = model.encode(corpus, convert_to_tensor=True, normalize_embeddings=True)
    q_emb = model.encode(query, convert_to_tensor=True, normalize_embeddings=True)
    sims = util.cos_sim(q_emb, corpus_emb)[0].cpu().numpy()
    top = np.argsort(sims)[-top_k:][::-1]
    return [(idx, float(sims[idx])) for idx in top]


def write_output(collection_dir: str, input_docs: List[str], persona: str, job: str, results: List[Dict]):
    ts = datetime.utcnow().isoformat()
    extracted = [
        {k: r[k] for k in ("document", "section_title", "importance_rank", "page_number")}
        for r in results
    ]
    subsections = [
        {k: r[k] for k in ("document", "refined_text", "page_number")}
        for r in results
    ]
    out_json = {
        "metadata": {
            "input_documents": input_docs,
            "persona": persona,
            "job_to_be_done": job,
            "processing_timestamp": ts
        },
        "extracted_sections": extracted,
        "subsection_analysis": subsections
    }
    out_path = os.path.join(collection_dir, "challenge1b_output.json")
    with open(out_path, "w") as f:
        json.dump(out_json, f, indent=2, ensure_ascii=False)


def process_collection_folder(collection_dir: str):
    input_json_path = os.path.join(collection_dir, "challenge1b_input.json")
    if not os.path.exists(input_json_path):
        return

    with open(input_json_path) as f:
        spec = json.load(f)

    persona = spec["persona"]["role"]
    job = spec["job_to_be_done"]["task"]
    query = f"{persona}. {job}"

    docs = [d["filename"] for d in spec["documents"]]
    all_results = []

    for fname in docs:
        pdf_path = os.path.join(collection_dir, fname)
        if not os.path.exists(pdf_path):
            continue

        doc = fitz.open(pdf_path)
        lines = parse_lines(doc)
        headings = detect_headings(lines)
        sections = build_sections(lines, headings)
        ranked = rank_sections(sections, query)

        for rank_pos, (idx, score) in enumerate(ranked, 1):
            sec = sections[idx]
            all_results.append({
                "document": fname,
                "section_title": sec.heading.text[:150],
                "importance_rank": rank_pos,
                "page_number": sec.heading.page,
                "refined_text": sec.as_text()
            })
        doc.close()

    write_output(collection_dir, docs, persona, job, all_results)


def process_all_collections():
    base_dir = os.getcwd()
    for folder in os.listdir(base_dir):
        collection_path = os.path.join(base_dir, folder)
        if os.path.isdir(collection_path) and folder.lower().startswith("collection"):
            print(f"Processing {folder}")
            process_collection_folder(collection_path)


if __name__ == "__main__":
    process_all_collections()
