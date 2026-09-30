import os
from pathlib import Path

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

from qna import answer_question
from explanation_module import explain_concept
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(title="EduGenie - Google Gemini Powered Learning Assistant")
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request,
        "index.html",
        {"result": None, "error": None}
    )


@app.post("/qa")
async def qa_api(payload: dict):
    question = (payload.get("question") or "").strip()
    if not question:
        return {"error": "Please enter a question."}
    try:
        return {"result": answer_question(question)}
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/explain")
async def explain_api(payload: dict):
    topic = (payload.get("topic") or "").strip()
    if not topic:
        return {"error": "Please enter a topic."}
    try:
        return {"result": explain_concept(topic)}
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/quiz")
async def quiz_api(payload: dict):
    passage = (payload.get("passage") or "").strip()
    if not passage:
        return {"error": "Please enter a passage."}
    try:
        return {"result": generate_quiz(passage)}
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/summarize")
async def summarize_api(payload: dict):
    text = (payload.get("text") or "").strip()
    if not text:
        return {"error": "Please enter text to summarize."}
    try:
        return {"result": summarize_text(text)}
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/learn/recommendations")
async def recommendations_api(payload: dict):
    topic = (payload.get("topic") or "").strip()
    if not topic:
        return {"error": "Please enter a topic."}
    level = (payload.get("level") or "Beginner").strip()
    try:
        return {"result": get_learning_recommendations(topic, level)}
    except Exception as exc:
        return {"error": str(exc)}


@app.post("/run", response_class=HTMLResponse)
async def run_task(
    request: Request,
    task: str = Form(...),
    user_input: str = Form(...)
):
    user_input = user_input.strip()

    if not user_input:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"result": None, "error": "Please enter some text."}
        )

    try:
        if task == "Explain":
            result = explain_concept(user_input)
        elif task == "QnA":
            result = answer_question(user_input)
        elif task == "Quiz":
            result = generate_quiz(user_input)
        elif task == "Summary":
            result = summarize_text(user_input)
        elif task == "Recommend Path":
            result = get_learning_recommendations(user_input, "Beginner")
        else:
            raise ValueError("Unknown task selected.")

        return templates.TemplateResponse(
            request,
            "index.html",
            {"result": result, "error": None}
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request,
            "index.html",
            {"result": None, "error": str(exc)}
        )


@app.get("/health")
async def health():
    return {"status": "ok", "service": "EduGenie"}
