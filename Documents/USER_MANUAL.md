# Scheme-AI: User Manual & Step-by-Step Guide

Welcome to **Scheme-AI**, an Agentic AI-powered welfare assistant that helps citizens identify eligible government schemes and provides step-by-step guidance on how to apply using conversational AI and speech-to-text.

This manual explains how to set up, run, and use the Scheme-AI application.

---

## 📋 Table of Contents
1. [Prerequisites](#-prerequisites)
2. [Installation & Setup](#-installation--setup)
3. [API Key Configuration](#-api-key-configuration)
4. [Step-by-Step User Guide](#-step-by-step-user-guide)
   * [Step 1: Fill out Demographic Profile](#step-1-fill-out-demographic-profile)
   * [Step 2: Review Recommendations & Analytics](#step-2-review-recommendations--analytics)
   * [Step 3: Conversational AI & Voice Assistant](#step-3-conversational-ai--voice-assistant)
   * [Step 4: Browse All Schemes](#step-4-browse-all-schemes)
5. [Troubleshooting Common Issues](#-troubleshooting-common-issues)

---

## 💻 Prerequisites
Make sure your system meets the following requirements before starting:
* **Operating System:** Windows 10/11, macOS, or Linux.
* **Python Version:** Python 3.10, 3.11, 3.12, or 3.13.
* **Browser:** **Google Chrome** or **Microsoft Edge** (strongly recommended for microphone access).
* **Internet Connection:** Required to connect to Groq/Gemini AI services.

---

## 🛠️ Installation & Setup

### 1. Clone the Project
Open your terminal (PowerShell on Windows, Terminal on Mac) and navigate to the project directory:
```bash
git clone https://github.com/LavinaFand21/Scheme-AI.git
cd Scheme-AI
```

### 2. Create and Activate Virtual Environment
* **On Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .venv\Scripts\activate
  ```
* **On macOS/Linux:**
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  ```

### 3. Install Required Packages
```bash
pip install -r requirements.txt
```

### 4. Seed the Database
Initialize and load the 54 government schemes into your local database:
* **On Windows:**
  ```powershell
  python -m scripts.ingest
  ```
* **On macOS/Linux:**
  ```bash
  python3 -m scripts.ingest
  ```

---

## 🔑 API Key Configuration

To enable the AI chatbot and voice dictation, you must export your Groq API key:

* **On Windows (PowerShell):**
  ```powershell
  $env:GROQ_API_KEY="your_groq_api_key_here"
  ```
* **On Windows (Command Prompt):**
  ```cmd
  set GROQ_API_KEY=your_groq_api_key_here
  ```
* **On macOS/Linux:**
  ```bash
  export GROQ_API_KEY="your_groq_api_key_here"
  ```

*(Optional: You can also export `GEMINI_API_KEY` for Gemini eligibility matching. If omitted, the system falls back to your Groq key automatically).*

---

## 🚀 Running the Application

To run the full decoupled application, you need to start the backend and frontend in **two separate terminal windows** (ensure the API key is set in both):

### Terminal 1: Start Backend API
* **On Windows:**
  ```powershell
  .\.venv\Scripts\python -m uvicorn backend.main:app --reload --port 8000
  ```
* **On macOS/Linux:**
  ```bash
  ./.venv/bin/python -m uvicorn backend.main:app --reload --port 8000
  ```

### Terminal 2: Start Frontend Dashboard
* **On Windows:**
  ```powershell
  .\.venv\Scripts\python -m streamlit run frontend/app.py
  ```
* **On macOS/Linux:**
  ```bash
  ./.venv/bin/python -m streamlit run frontend/app.py
  ```

The app will open automatically in your browser at `http://localhost:8501`.

---

## 📝 Step-by-Step User Guide

### Step 1: Fill out Demographic Profile
1. Locate the **Sidebar** on the left side of the screen.
2. Select your demographic attributes:
   * **Age** (using the slider)
   * **Gender** (Male / Female / Transgender)
   * **Annual Income** (in INR)
   * **Occupation** (Student, Farmer, Business owner, etc.)
   * **State / Union Territory**
   * **Social Category** (General, OBC, SC, ST, EWS)
3. Click the **"Find My Schemes & Lock Profile"** button. The green banner at the bottom will display `Mode: FastAPI Server Connected`.

---

### Step 2: Review Recommendations & Analytics
1. Open the **"Recommended Schemes"** tab.
2. Here, you will see cards for the schemes you qualify for. Each card displays:
   * A **Match Score** percentage.
   * A brief description of the scheme.
   * **Key Benefits** (financial details, subsidies).
   * **Match Reason** explaining exactly why you qualified based on your profile.
3. On the right, look at the **Analytics Insights** chart to see the category distribution of your eligible schemes.
4. Click the **"Guide Me"** button under any scheme card to set the context for the AI chatbot.

---

### Step 3: Conversational AI & Voice Assistant
1. Open the **"Conversational Application Assistant"** tab.
2. At the top, select your options:
   * **Assistant Reasoning Level:** Choose **Smart (70B)** for deep analysis or **Fast (8B)** for low latency.
   * **Voice Dictation Language:** Choose **English (IN)** or **Hindi (IN)**.
3. **Using Voice Input (Microphone):**
   * Click the circular **Microphone** button next to the input box.
   * The button will turn red and pulse, showing it is recording. Speak clearly into your microphone.
   * Click the button again to stop. The status text will change to `Transcribing...`.
   * The spoken text will automatically be typed into the chat input field.
4. Click **Send 🚀** to chat with the assistant and get step-by-step application guidance.

---

### Step 4: Browse All Schemes
1. Open the **"Search & Directory"** tab.
2. You can search the entire database of 54 government schemes.
3. Use the search bar to filter by name, category, or description.

---

## ⚠️ Troubleshooting Common Issues

### 1. `ModuleNotFoundError: No module named '...'`
* **Cause:** Dependencies were not installed inside your activated virtual environment.
* **Fix:** Explicitly run:
  * Windows: `.\.venv\Scripts\python -m pip install -r requirements.txt`
  * Mac/Linux: `./.venv/bin/python -m pip install -r requirements.txt`

### 2. `sqlite3.OperationalError: no such table: Vector_Store`
* **Cause:** The database was not initialized correctly before launching the app.
* **Fix:** Shut down the app (Ctrl+C) and run: `python -m scripts.ingest`.

### 3. Microphone is disabled or unclickable
* **Cause:** Modern browsers block microphone access on insecure connections.
* **Fix:** Ensure you are accessing the app using **`http://localhost:8501`** or **`http://127.0.0.1:8501`** in Google Chrome or Microsoft Edge. If accessing via a network IP, the mic will be blocked. Click **"Allow"** when Chrome prompts for mic permission.

### 4. Groq Connection Error / "Demo Mode" is stuck
* **Cause:** The API key is missing or your college network is blocking calls to Groq API.
* **Fix:** Verify you have run the `set GROQ_API_KEY` command in your active terminal. If on college Wi-Fi, try connecting to your **mobile phone's hotspot** to bypass strict firewalls.
