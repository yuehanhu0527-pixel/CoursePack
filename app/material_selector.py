import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from app.utils import parse_json_response

from app.models import (
    LessonBlueprint,
    MaterialSelection
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def select_materials(
    blueprint: LessonBlueprint
) -> MaterialSelection:

    prompt = f"""
You are deciding which instructional materials are useful for a lesson.

LESSON BLUEPRINT

Grade: {blueprint.grade}
Subject: {blueprint.subject}
Learning objective: {blueprint.objective}

Concepts:
{blueprint.concepts}

Lesson sequence:
{[
    {
        "time": step.time,
        "activity": step.activity
    }
    for step in blueprint.lesson_sequence
]}

Assessment targets:
{blueprint.assessment_targets}

Available material types:

1. quiz
   Use when a short assessment would help check whether students met the objective.

2. lesson_resources
   Use when the teacher would benefit from warm-up activities,
   direct instruction guidance, examples, guided practice,
   independent practice, media suggestions, or an exit ticket.

3. reading
   Use when students need explanatory text, background knowledge,
   conceptual explanation, or content that benefits from reading.
   Do NOT select reading just because it is available.

4. worksheet
   Use when students would benefit from repeated practice,
   problem solving, written exercises, or skill rehearsal.

Return ONLY valid JSON in this exact format:

{{
  "quiz": true,
  "lesson_resources": true,
  "reading": false,
  "worksheet": true,
  "reason": "Short explanation of why these materials fit the lesson."
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

    return MaterialSelection(**data)