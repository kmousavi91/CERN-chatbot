# 🔬 Physics Research Assistant

**Higgs Boson Analysis System**

---

## Overview

This project is a **Physics Research Assistant** designed to help researchers, students, and enthusiasts explore Higgs boson data. It uses **AI-powered search** and **document retrieval** to provide answers to physics questions from scientific papers, including measurements, formulas, theoretical explanations, and experiment comparisons.

The system also **plots Higgs boson resonance curves** using the Breit-Wigner formula, helping visualize key concepts in particle physics.



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

You need to have **Docker** installed on your system. 

### Setup

1. **Clone the repository**:

```bash
git clone https://github.com/kmousavi91/CERN-chatbot.git
cd CERN-chatbot
```


2. **Build the Docker image**:

```bash
docker build -t higgs-assistant .
```

4. **Run the Docker container**:

```bash
docker run -p 7863:7863 higgs-assistant
```

5. Open your browser and go to:

```
http://localhost:7863
```

You should see the chat interface.

---

## Using the Assistant

* Type your physics question in **natural language**.
* The assistant automatically classifies your question and retrieves information from the PDFs.
* For **formula or resonance questions**, it will also show a **Higgs resonance plot**.
* **Confidence levels** are shown for each answer (High, Medium, Low).

### Example Questions

1. What is the most precise measurement of the Higgs boson mass reported by ATLAS and CMS, and what are the uncertainties?
2. Explain the Higgs boson resonance using the Breit–Wigner formula and describe the physical meaning of its decay width Γ.?
3. Compare the Higgs boson decay channels analyzed by ATLAS and CMS and highlight the differences in statistical and systematic uncertainties.?
4. Within the Standard Model, why does the Higgs boson have a finite decay width and how does it relate to its interactions?

---

## File Structure

```
final/
├─ app.py              # Main application code
├─ Dockerfile          # Docker configuration
├─ requirements.txt    # Python dependencies
├─ data/               # PDFs and preprocessed data
│  ├─ multi_pdf_index.faiss
│  └─ multi_pdf_chunks.jsonl
```

---

## Notes

* The application is **self-contained** with all necessary dependencies installed via Docker.
* Large PDF files are included in `data/pdfs/`, but avoid committing sensitive or very large files to GitHub.
* If you encounter **port conflicts**, you can change the port in the Docker run command:



* The AI model used is **Groq LLaMA-3.1-8b Instant**, 

---


---

## Support

For questions or troubleshooting:

* Check Docker logs: `docker logs <container_id>`
* Check `app.py` console output
* Verify internet connectivity if AI model calls fail

---

**Enjoy exploring the Higgs boson with AI!**
