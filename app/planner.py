import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from app.utils import parse_json_response

from app.models import (
    LessonBlueprint,
    CoursePlan
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def create_course_plan(
    blueprint: LessonBlueprint
) -> CoursePlan:

    prompt = f"""
You are planning which instructional materials should be generated for a lesson.

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

Available actions:

- generate_quiz
- generate_lesson_resources
- generate_reading
- generate_worksheet

Create an execution plan using only the actions that are genuinely useful for this lesson.

Rules:
- Do not include every action by default.
- Choose actions based on the lesson's actual needs.
- Reading is useful when students need explanation, background knowledge, or conceptual text.
- Worksheet is useful when students need repeated written practice or skill rehearsal.
- Quiz is useful when a short assessment would help check mastery.
- Lesson resources are useful when the teacher needs instructional activities, examples, practice, or an exit ticket.
- Put the actions in a sensible order.
- Do not repeat an action.
- Use ONLY the allowed action names listed above.

Return ONLY valid JSON in this exact format:

{{
  "steps": [
    {{
      "action": "generate_lesson_resources",
      "reason": "Short explanation."
    }}
  ]
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

    return CoursePlan(**data)