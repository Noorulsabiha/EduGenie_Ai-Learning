from gemini_client import generate_text


def get_learning_recommendations(topic: str, level: str = "Beginner") -> str:
    prompt = f"""
Create a personalized learning path for the topic "{topic}".

Student level: {level}

Organize it from beginner to advanced:
1. Prerequisites
2. Beginner concepts
3. Intermediate concepts
4. Advanced concepts
5. Practice/project ideas
6. Suggested resource types (videos, articles, books, documentation)

Keep the path practical and easy to follow. Do not invent specific URLs.
"""
    return generate_text(prompt)
