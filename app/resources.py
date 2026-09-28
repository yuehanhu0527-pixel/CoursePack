import os

from dotenv import load_dotenv
from openai import OpenAI

from app.models import (
    LessonBlueprint,
    LessonResources
)

from app.utils import parse_json_response


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def generate_lesson_resources(
    blueprint: LessonBlueprint
) -> LessonResources:

    lesson_sequence = [
        {
            "time": step.time,
            "activity": step.activity
        }
        for step in blueprint.lesson_sequence
    ]

    prompt = f"""
You are an instructional designer.

Create lesson resources based ONLY on the lesson blueprint below.

Grade: {blueprint.grade}
Subject: {blueprint.subject}
Learning objective: {blueprint.objective}
Class length: {blueprint.class_length} minutes

Concepts:
{blueprint.concepts}

Prerequisites:
{blueprint.prerequisites}

Vocabulary:
{blueprint.vocabulary}

Assessment targets:
{blueprint.assessment_targets}

Lesson sequence:
{lesson_sequence}


IMPORTANT LESSON-SEQUENCE RULES:

- Create exactly ONE resource section for EACH lesson sequence step.
- Keep the resource sections in the SAME ORDER as the lesson sequence.
- Copy the EXACT time from each lesson sequence step.
- Copy the EXACT activity from each lesson sequence step.
- Do NOT add new lesson stages.
- Do NOT omit any lesson stages.
- Each resource section must directly support its corresponding activity.
- Resources must stay within the lesson blueprint.
- Do not introduce concepts outside the blueprint.
- The short "step" label may be concise and does not need to exactly
  match the activity text.
- Media resources may be described using suggestions or search keywords.
- Do NOT invent URLs.


SOURCE INTEGRITY RULES:

- Never invent a quotation, source, citation, author, publication,
  document title, date, study, or URL.

- If you use a real external source or direct quotation,
  provide enough identifying information when appropriate,
  such as:
  title, author or issuing body, and date.

- Do not present AI-created text as if it were an authentic
  historical document, article, letter, speech, study,
  literary quotation, or other real-world source.

- If you create text for classroom analysis instead of using
  a verified original source, clearly label it as one of:
  "Adapted practice passage"
  "Simplified practice passage"
  "Simulated source"
  "Teacher-created practice passage"

- Do not attach a real person's name, publication name,
  historical date, or source title to AI-created text.

- Mentioning or recommending a real book, song, musical work,
  artwork, or other well-known work is allowed.
  Do not invent quotations from that work.

- If exact source text is not necessary for the activity,
  prefer describing the source or providing search keywords
  rather than inventing the source content.


TIME FEASIBILITY RULES:

- Keep resources realistic for the assigned time.
- Do not overload a short lesson step with too many readings,
  questions, writing tasks, group tasks, or presentations.
- If a lesson step is short, keep the resources focused and concise.
- Prefer excerpts, short tasks, or jigsaw-style activities when
  full-length materials would not fit the available time.


Return ONLY valid JSON in this exact structure:

{{
  "sections": [
    {{
      "step": "Short step label",
      "time": "Exact time copied from the lesson sequence",
      "activity": "Exact activity copied from the lesson sequence",
      "resources": [
        {{
          "type": "Resource type",
          "description": "What the teacher or students should use"
        }}
      ]
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

    return LessonResources(**data)