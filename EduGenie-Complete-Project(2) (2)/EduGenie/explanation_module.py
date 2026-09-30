import os
from gemini_client import generate_text

# The project document describes LaMini-Flan-T5 as a lightweight local
# explanation model. It is optional here because installing PyTorch/Transformers
# can be very large on a normal student laptop.
_LOCAL_MODEL_ENABLED = os.getenv("USE_LOCAL_EXPLANATION_MODEL", "false").lower() == "true"


def _local_lamini_explanation(topic: str) -> str:
    try:
        from transformers import pipeline

        generator = pipeline(
            "text2text-generation",
            model="MBZUAI/LaMini-Flan-T5-783M",
        )
        prompt = (
            "Explain this topic for a beginner in simple language with a short "
            f"example: {topic}"
        )
        result = generator(prompt, max_new_tokens=220, do_sample=False)
        return result[0]["generated_text"].strip()
    except Exception:
        # If the optional local model cannot load, use the cloud model instead.
        return ""


def explain_concept(topic: str) -> str:
    if _LOCAL_MODEL_ENABLED:
        local_result = _local_lamini_explanation(topic)
        if local_result:
            return local_result

    prompt = f"""
You are EduGenie, a beginner-friendly educational tutor.

Explain the following concept as if the student has very little background.
Use this structure:
1. Simple definition
2. How it works
3. One easy example
4. Key points to remember

Topic:
{topic}
"""
    return generate_text(prompt)
