# Scheme-AI: Government Scheme Eligibility & Application Assistant

🚀 **Live Web Application:** [Access Scheme-AI here](https://scheme-ai-gwwcupwmsehdxmhfugverz.streamlit.app)

An Agentic AI assistant built for data science and computer science student projects. It performs conversational profiling, filters government welfare schemes based on demographic constraints, and uses a Retrieval-Augmented Generation (RAG) agent to explain benefits and provide step-by-step application guidance.

---

## Key Features

1. **Multilingual Voice Dictation:** Allows users to speak queries directly in **English (IN)** or **Hindi (IN)**. Uses a browser-based audio recorder that sends audio files to a backend running **Groq's Whisper API (`whisper-large-v3`)** for ultra-fast, highly accurate speech-to-text conversion.
2. **Dual-Backend Robustness:** Features a decoupled REST architecture (**FastAPI backend** + **Streamlit frontend**) that gracefully falls back to **in-process execution** if the FastAPI server is not running. This ensures a 100% fail-safe evaluation experience.
3. **Hybrid Eligibility Engine:** Filters schemes based on demographic attributes (Age, Income, Occupation, State, Category, Gender) in a structured relational database (SQLite), then re-ranks them using an LLM (Gemini) to determine the final match confidence and reasoning.
4. **Pure-Python Vector Store (RAG):** Implements a lightweight SQLite-backed vector search with custom cosine similarity calculations. Avoids compilation or installation issues associated with binary vector databases on Python 3.13.
5. **Rich Dashboard Analytics:** A visually stunning interactive interface using Streamlit, Plotly graphs, and custom CSS for a modern dark/light glassmorphic presentation.

---

## Project Structure

```text
minor_project/
├── backend/
│   ├── database.py         # SQLite connection & CRUD operations (thread-safe)
│   ├── vector_store.py     # Custom SQLite-based vector store (RAG)
│   ├── eligibility.py      # Demographic filter & LLM evaluation
│   ├── models.py           # Pydantic schema validation
│   └── main.py             # FastAPI REST endpoints & audio transcription
├── frontend/
│   └── app.py              # Streamlit dashboard, voice recorder, & chat assistant
├── data/
│   └── schemes.json        # 54 seeded government schemes
├── scripts/
│   └── ingest.py           # Database seeding pipeline
├── requirements.txt        # Core dependencies (including groq and python-multipart)
└── README.md               # User guide
```

---

## Setup & Running Guide

### 1. Create and Activate Virtual Environment
```bash
# Create environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Keys
You need to set the following environment variables:

```bash
# Required for RAG Chat and LLM Eligibility matching
export GEMINI_API_KEY="your_gemini_api_key_here"

# Required for Voice Dictation (Speech-to-Text transcription)
export GROQ_API_KEY="your_groq_api_key_here"
```
*Note: If neither `GEMINI_API_KEY` nor `GROQ_API_KEY` is provided, the application will run in **Demo Mode** (using local heuristic matching and search-grounded text rendering). If only `GROQ_API_KEY` is provided, all features (including Chat, Eligibility, and Voice Dictation) will run fully using Groq.*

### 4. Ingest and Seed Database
Run the ingestion pipeline to initialize the SQLite database and generate vector embeddings for RAG:
```bash
python3 scripts/ingest.py
```

### 5. Running the Application

For the full REST architecture, run the backend and frontend in separate terminals:

**Terminal 1 (Backend API):**
```bash
source .venv/bin/activate
python3 -m uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 (Frontend Dashboard):**
```bash
source .venv/bin/activate
streamlit run frontend/app.py
```

*Tip: If you do not run the backend API server, the Streamlit app will automatically fall back to **In-Process Engine** mode, calling database and matching logic directly from local modules. Note that backend-dependent features (like Voice Dictation) require the Backend API to be running.*
