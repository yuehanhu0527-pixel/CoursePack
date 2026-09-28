import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from app.models import (
    LessonBlueprint,
    ReadingMaterial
)

from app.utils import parse_json_response


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def generate_reading(
    blueprint: LessonBlueprint,
    retrieved_context: list[str] | None = None
) -> ReadingMaterial:

    # If no retrieved context is provided,
    # use an empty list so the function still works normally.
    if retrieved_context is None:
        retrieved_context = []

    # Convert the retrieved chunks into one block of text
    # that can be inserted into the prompt.
    source_context = "\n\n".join(retrieved_context)

    prompt = f"""
You are creating a student reading material for a lesson.

LESSON BLUEPRINT:
{json.dumps(blueprint.model_dump(), indent=2)}

SOURCE MATERIAL:
{source_context}

Create a reading that supports the lesson objective and concepts.

Rules:

- Keep the reading appropriate for the stated grade level.
- Align the reading with the lesson blueprint.
- Use relevant information from the provided source material when useful.
- Keep the reading focused on the lesson objective.
- Do not introduce unnecessarily advanced or unrelated concepts.
- Do not include information that conflicts with the lesson blueprint.
- Organize the reading clearly for students.
- If the source material is limited or not useful, still create a reading based on the lesson blueprint.

Return ONLY valid JSON in this exact format:

{{
  "title": "Reading title",
  "introduction": "Introduction text",
  "sections": [
    "Section 1",
    "Section 2"
  ],
  "summary": "Summary text"
}}
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = response.choices[0].message.content

    data = parse_json_response(content)

    return ReadingMaterial(**data)