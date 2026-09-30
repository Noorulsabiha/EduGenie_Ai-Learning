import json
import re
from gemini_client import generate_text


def clean_json_block(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def generate_quiz(passage: str):
    prompt = f"""
Create exactly 3 multiple-choice questions from the passage below.

Return ONLY valid JSON. Do not use Markdown.
Required format:
[
  {{
    "question": "Question text",
    "options": ["A", "B", "C", "D"],
    "answer": "A"
  }}
]

Rules:
- Exactly 3 questions.
- Exactly 4 options for every question.
- The answer must be exactly one of the four option strings.
- Questions must be answerable from the passage.
- Make distractors plausible but incorrect.

Passage:
{passage}
"""
    raw = clean_json_block(generate_text(prompt))

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Quiz JSON could not be parsed: {exc}\n\nModel output:\n{raw}")

    if not isinstance(data, list) or len(data) != 3:
        raise RuntimeError("Gemini did not return exactly 3 quiz questions.")

    for item in data:
        if not isinstance(item, dict):
            raise RuntimeError("Invalid quiz question format.")
        if "question" not in item or "options" not in item or "answer" not in item:
            raise RuntimeError("A quiz question is missing required fields.")
        if len(item["options"]) != 4:
            raise RuntimeError("Each quiz question must contain exactly 4 options.")
        if item["answer"] not in item["options"]:
            raise RuntimeError("Quiz answer is not one of the options.")

    return data
