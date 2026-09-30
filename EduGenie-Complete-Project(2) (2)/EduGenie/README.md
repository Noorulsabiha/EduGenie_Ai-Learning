# EduGenie: Google Gemini Powered Learning Assistant

This project follows the supplied EduGenie project document:
- FastAPI backend
- HTML + CSS frontend
- Gemini-powered Q&A, quiz generation, summarization and learning recommendations
- Concept explanation module with optional LaMini-Flan-T5 local model
- REST endpoints: `/qa`, `/explain`, `/quiz`, `/summarize`, `/learn/recommendations`

## 1. Requirements

Install:
- Python 3.10+
- VS Code
- A Gemini API key

## 2. Open the project

Open the `EduGenie` folder in VS Code.

## 3. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
python -m venv .venv
.venv\Scripts\activate
```

## 4. Install packages

```bash
pip install -r requirements.txt
```

## 5. Create the .env file

Copy `.env.example` and rename the copy to:

```text
.env
```

Then replace:

```text
GEMINI_API_KEY=YOUR_GEMINI_API_KEY_HERE
```

with your own key.

Do NOT upload `.env` to GitHub.

## 6. Run EduGenie

```bash
uvicorn main:app --reload
```

Open the URL shown in the terminal, normally:

```text
http://127.0.0.1:8000
```

## 7. Test

Try:
- Explain: `What is a CPU?`
- QnA: `What is binary search?`
- Quiz: paste a short paragraph
- Summary: paste a long paragraph
- Recommend Path: `Python programming`

## API endpoints

- GET `/`
- GET `/health`
- POST `/qa`
- POST `/explain`
- POST `/quiz`
- POST `/summarize`
- POST `/learn/recommendations`

## Optional LaMini-Flan-T5

The project document describes LaMini-Flan-T5-783M for local concept explanation.

For the easiest setup, keep:

```text
USE_LOCAL_EXPLANATION_MODEL=false
```

The explanation module then uses Gemini.

If you specifically want to test the local model, install the appropriate PyTorch and Transformers packages for your machine, then set:

```text
USE_LOCAL_EXPLANATION_MODEL=true
```

The code automatically falls back to Gemini if the local model cannot be loaded.

## Security

Never put your real API key in Python, HTML, JavaScript or GitHub. Use `.env`.
