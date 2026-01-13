import os
import re
import json
import faiss
import io
import base64
import numpy as np
import matplotlib.pyplot as plt
import gradio as gr
from sentence_transformers import SentenceTransformer
from groq import Groq
from dotenv import load_dotenv


# ================= CONFIG =================
GROQ_API_KEY = "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"  # Replace with your valid key
MODEL_ID = "llama-3.1-8b-instant"

DATA_DIR = "data"
INDEX_FILE = os.path.join(DATA_DIR, "multi_pdf_index.faiss")
CHUNKS_FILE = os.path.join(DATA_DIR, "multi_pdf_chunks.jsonl")
EMBED_MODEL = "all-MiniLM-L6-v2"



# ================= INIT =================
client = Groq(api_key=GROQ_API_KEY)
embedder = SentenceTransformer(EMBED_MODEL)
index = faiss.read_index(INDEX_FILE)

with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
    documents = [json.loads(l) for l in f]

# ================= UTILITIES =================
def split_questions(text):
    parts = re.split(r"\?\s*", text)
    return [p.strip() + "?" for p in parts if p.strip()]

def classify_query(q):
    q = q.lower()
    if any(k in q for k in ["atlas", "cms", "4l", "four-lepton"]):
        return "comparison"
    if any(k in q for k in ["breit", "resonance", "width", "gamma", "plot", "figure", "diagram"]):
        return "formula"
    if any(k in q for k in ["why", "mechanism", "vacuum", "stability"]):
        return "theory"
    if any(k in q for k in ["mass", "measured", "gev", "uncertainty"]):
        return "measurement"
    return "general"

def retrieve(query, k):
    qv = embedder.encode([query]).astype("float32")
    _, idx = index.search(qv, k)
    return [documents[i] for i in idx[0]]

def deduplicate(docs):
    seen = set()
    unique = []
    for d in docs:
        key = d["text"][:300]
        if key not in seen:
            seen.add(key)
            unique.append(d)
    return unique

def is_valid_mass_chunk(text):
    t = text.lower()
    if "signal strength" in t or "μ" in t or "\\hat{\\mu}" in t:
        return False
    if "mass" not in t or "gev" not in t:
        return False
    return True

def is_formula_chunk(text):
    t = text.lower()
    if any(k in t for k in ["cross section", "branching ratio", "luminosity"]):
        return False
    if "gev" in t and "mass" in t:
        return False
    return True

def paper_router(docs, query):
    q = query.lower()
    if "atlas" in q:
        return [d for d in docs if "atlas" in d["source"].lower()]
    if "cms" in q:
        return [d for d in docs if "cms" in d["source"].lower()]
    return docs

def confidence_score(docs, answer_text):
    n = len(docs)
    base = 0.3 + 0.1 * min(n, 5)
    if re.search(r"m_H\s*=\s*[\d\.]+\s*\\pm\s*[\d\.]+", answer_text):
        base += 0.4
    if base > 1.0:
        base = 1.0
    if base >= 0.85:
        return "High"
    elif base >= 0.65:
        return "Medium"
    else:
        return "Low"

def format_citations(docs):
    sources = set(d["source"] for d in docs)
    return ", ".join(list(sources)[:3])

# ================= HIGGS RESONANCE PLOT =================
def plot_breit_wigner(M=125, Gamma=4.1):
    E = np.linspace(M-20, M+20, 500)
    P = 1 / ((E**2 - M**2)**2 + (M**2 * Gamma**2))
    plt.figure(figsize=(6,4))
    plt.plot(E, P)
    plt.title("Higgs Resonance (Breit-Wigner)")
    plt.xlabel("Energy [GeV]")
    plt.ylabel("P(E)")
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close()
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    return f"![Higgs Resonance](data:image/png;base64,{img_b64})"

# ================= PROMPTS =================
PROMPTS = {
    "measurement": """
You are a Physics Measurement Extraction System.
STRICT RULES:
1. ONLY extract the Higgs boson mass m_H.
2. ACCEPT values ONLY if explicitly stated as a mass AND in GeV.
3. IGNORE signal strength (μ), cross sections, or fit parameters.
4. Output EXACTLY one sentence in the form:
   $m_H = XXX.XX \\pm XX.XX$ GeV
5. Optionally provide 1-2 sentences short explanation.
6. If no valid mass exists, say:
   The specific Higgs mass value is not found in the documents.
""",
    "formula": """
You are a Physics Phenomenology System.
RULES:
1. Explain the Higgs resonance shape concisely (max 3 sentences).
2. Show the relativistic Breit–Wigner formula ONCE:
$$P(E) = \\frac{1}{(E^2 - M^2)^2 + M^2\\Gamma^2}$$
3. Explain the physical meaning of Γ.
4. Do NOT include repeated sentences.
5. Do not retrieve long paragraphs from PDFs; only use context if needed.
""",
    "comparison": """
You are an Experimental Physics Comparison System.
RULES:
1. Compare ATLAS and CMS results if both appear.
2. Identify decay channels (e.g. 4ℓ).
3. Separate statistical and systematic uncertainties.
4. Max 4 sentences.
5. If one experiment is missing, say so.
""",
    "theory": """
You are a Theoretical Physics Explanation System.
RULES:
1. Answer conceptually.
2. Do NOT include numerical values from the papers.
3. Explain within the Standard Model.
4. Max 4 sentences.
""",
    "general": """
You are a Physics Research Assistant.
Use only the provided context.
Be concise and accurate.
"""
}

# ================= CHAT LOGIC =================
def chat_logic(user_input, history):
    questions = split_questions(user_input)
    for q in questions:
        qtype = classify_query(q)
        last_task = next((msg.get("task") for msg in reversed(history) if msg.get("task")), None)
        reset_notice = ""
        if last_task and last_task != qtype:
            reset_notice = "IMPORTANT: NEW TASK. Do NOT repeat previous answers.\n"

        k = 8 if qtype == "comparison" else 5
        docs = retrieve(q, k)
        docs = deduplicate(docs)
        docs = paper_router(docs, q)

        if qtype == "measurement":
            docs = [d for d in docs if is_valid_mass_chunk(d["text"])]
        if qtype == "formula":
            docs = [d for d in docs if is_formula_chunk(d["text"])][:3]

        context = "" if qtype in ["theory", "general"] else "\n".join(f"[{d['source']}]\n{d['text']}" for d in docs)

        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": PROMPTS[qtype]},
                {"role": "user", "content": f"{reset_notice}CONTEXT:\n{context}\n\nQUESTION:\n{q}"}
            ],
            temperature=0.0,
            max_tokens=400
        )

        answer_text = response.choices[0].message.content.strip()

        # Deduplicate repeated sentences
        seen_sents = set()
        cleaned = []
        for s in re.split(r'(?<=[.!?])\s+', answer_text):
            if s.strip() not in seen_sents:
                seen_sents.add(s.strip())
                cleaned.append(s.strip())
        answer_text = " ".join(cleaned)

        messages = []

        # Measurement formula formatting
        if qtype == "measurement" and re.search(r"m_H\s*=\s*[\d\.]+\s*\\pm\s*[\d\.]+", answer_text):
            formula_match = re.search(r"(m_H\s*=\s*[\d\.]+\s*\\pm\s*[\d\.]+)", answer_text)
            if formula_match:
                formula = formula_match.group(1)
                formula = f"{formula}\\ \\mathrm{{GeV}}"
                explanation = answer_text.replace(formula_match.group(1), "").strip()
                md_message = f"$$\n{formula}\n$$\n\n{explanation}"
                messages.append(md_message)
            else:
                messages.append(answer_text)
        else:
            parts = re.split(r"(\$\$.*?\$\$)", answer_text, flags=re.DOTALL)
            for p in parts:
                if p.strip():
                    messages.append(p.strip())

        if qtype == "formula":
            messages.append(plot_breit_wigner())

        if qtype not in ["theory", "general"]:
            sources_text = format_citations(docs)
            if sources_text:
                messages.append(f"**Sources:** {sources_text}")

        conf = confidence_score(docs, answer_text)
        messages.append(f"**Confidence:** {conf}")

        history.append({"role":"user","content":q})
        for m in messages:
            history.append({"role":"assistant","content":m})

    return history, ""

# ================= UI =================
with gr.Blocks(theme=gr.themes.Soft(primary_hue="purple")) as app:
    gr.Markdown("# 🔬 Physics Research Assistant\n**Higgs Boson Analysis System**")
    chatbot = gr.Chatbot(type="messages", height=650, show_label=False)
    with gr.Row():
        msg = gr.Textbox(placeholder="Ask a physics question…", scale=9)
        btn = gr.Button("Analyze", variant="primary", scale=1)
    btn.click(chat_logic, [msg, chatbot], [chatbot, msg])
    msg.submit(chat_logic, [msg, chatbot], [chatbot, msg])

if __name__ == "__main__":
    app.launch(server_name="0.0.0.0", server_port=7863, share=False)

