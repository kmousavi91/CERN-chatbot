import os
import json
import re

import faiss
from PyPDF2 import PdfReader
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = "data"
PDF_FOLDER = os.path.join(DATA_DIR, "pdfs")
INDEX_PATH = os.path.join(DATA_DIR, "multi_pdf_index.faiss")
CHUNKS_PATH = os.path.join(DATA_DIR, "multi_pdf_chunks.jsonl")

def process_pdfs():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = []

    for fname in os.listdir(PDF_FOLDER):
        if not fname.lower().endswith(".pdf"):
            continue

        reader = PdfReader(os.path.join(PDF_FOLDER, fname))
        text = "\n".join(p.extract_text() or "" for p in reader.pages)

        text = re.sub(r"(?is)\nreferences.*", "", text)
        if not text.strip():
            continue

        for chunk in splitter.split_text(text):
            chunks.append({"source": fname, "text": chunk.strip()})

    return chunks

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)

    print("📄 Processing PDFs...")
    chunks = process_pdfs()

    model = SentenceTransformer("all-MiniLM-L6-v2")
    embeddings = model.encode([c["text"] for c in chunks]).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)
    faiss.write_index(index, INDEX_PATH)

    with open(CHUNKS_PATH, "w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c) + "\n")

    print(f"✅ Indexed {len(chunks)} chunks")

