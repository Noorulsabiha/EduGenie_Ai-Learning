from gemini_client import generate_text


def summarize_text(text: str) -> str:
    prompt = f"""
Summarize the following educational text for a student.

Requirements:
- Keep the important information.
- Remove repetition.
- Use simple, clear language.
- Prefer short paragraphs and bullet points.
- Do not add information that is not present in the source.

Text:
{text}
"""
    return generate_text(prompt)
