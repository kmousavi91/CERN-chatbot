# 🔬 Physics Research Assistant

**Higgs Boson Analysis System**

---

## Overview

This project is a **Physics Research Assistant** designed to help researchers, students, and enthusiasts explore Higgs boson data. It uses **AI-powered search** and **document retrieval** to provide answers to physics questions from scientific papers, including measurements, formulas, theoretical explanations, and experiment comparisons.

The system also **plots Higgs boson resonance curves** using the Breit-Wigner formula, helping visualize key concepts in particle physics.

This tool is designed for **non-experts**: you do not need deep programming knowledge to use it.

---

## Features

* **AI-based Question Answering:** Ask physics questions in natural language, and get concise, accurate answers.
* **Higgs Boson Mass Extraction:** Extracts mass and uncertainties from research papers.
* **Formula Explanation:** Explains the Breit-Wigner resonance formula with visual plots.
* **Experiment Comparison:** Compares results from ATLAS and CMS experiments.
* **Theoretical Insights:** Provides explanations of Higgs boson properties within the Standard Model.
* **Interactive Web Interface:** Simple chat interface to interact with the assistant.

---

## Getting Started

### Prerequisites

You need to have **Docker** installed on your system. You also need an **API key** from Groq (or other compatible model provider).

### Setup

1. **Clone the repository**:

```bash
git clone <your-repo-url>
cd physics-rag-assistant/final
```

2. **Create a `.env` file** with your Groq API key:

```text
GROQ_API_KEY=your_api_key_here
MODEL_ID=llama-3.1-8b-instant  # optional, defaults to this model
```

> **Important:** Never share your `.env` file or commit it to GitHub. It contains your secret key.

3. **Build the Docker image**:

```bash
docker build -t higgs-assistant .
```

4. **Run the Docker container**:

```bash
docker run -p 7860:7860 --env-file .env higgs-assistant
```

5. Open your browser and go to:

```
http://localhost:7860
```

You should see the chat interface.

---

## Using the Assistant

* Type your physics question in **natural language**.
* The assistant automatically classifies your question and retrieves information from the PDFs.
* For **formula or resonance questions**, it will also show a **Higgs resonance plot**.
* **Confidence levels** are shown for each answer (High, Medium, Low).

### Example Questions

1. What is the measured Higgs boson mass?
2. Show the Higgs boson resonance plot.
3. Compare ATLAS and CMS results for 4-lepton decay.
4. Explain why the Higgs boson mass is important in the Standard Model.
5. What is the physical meaning of the Breit-Wigner width (\Gamma)?

---

## File Structure

```
final/
├─ app.py              # Main application code
├─ Dockerfile          # Docker configuration
├─ requirements.txt    # Python dependencies
├─ .env                # API keys (do NOT commit)
├─ data/               # PDFs and preprocessed data
│  ├─ multi_pdf_index.faiss
│  └─ multi_pdf_chunks.jsonl
```

---

## Notes

* The application is **self-contained** with all necessary dependencies installed via Docker.
* Large PDF files are included in `data/pdfs/`, but avoid committing sensitive or very large files to GitHub.
* If you encounter **port conflicts**, you can change the port in the Docker run command:

```bash
docker run -p 8000:7860 --env-file .env higgs-assistant
```

* The AI model used is **Groq LLaMA-3.1-8b Instant**, but you can configure a different model via `.env`.

---

## Security & Best Practices

* Never commit your `.env` file with secrets.
* Always use `--env-file` to pass secrets securely to Docker.
* Use Git LFS for very large PDFs to avoid GitHub push errors.

---

## Support

For questions or troubleshooting:

* Check Docker logs: `docker logs <container_id>`
* Check `app.py` console output
* Verify internet connectivity if AI model calls fail

---

**Enjoy exploring the Higgs boson with AI!**
