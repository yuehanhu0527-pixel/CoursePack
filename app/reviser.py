import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from app.utils import parse_json_response

from app.models import (
    LessonBlueprint,
    Worksheet,
    Quiz,
    ReadingMaterial,
    LessonResources,
    AlignmentReport
)


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def revise_worksheet(
    blueprint: LessonBlueprint,
    worksheet: Worksheet,
    alignment_report: AlignmentReport
) -> Worksheet:

    prompt = f"""
You are revising a worksheet to fix the problems.

LESSON BLUEPRINT:
{json.dumps(blueprint.model_dump(), indent=2)}

CURRENT WORKSHEET:
{json.dumps(worksheet.model_dump(), indent=2)}

ALIGNMENT PROBLEMS:
{json.dumps(alignment_report.model_dump(), indent=2)}

Revise the worksheet so that the reported alignment problems are fixed.

Rules:

- Keep parts of the worksheet that are already correct.
- Change only what is necessary.
- Remove unsupported concepts.
- Keep all problems aligned with the lesson blueprint.
- Preserve the same general worksheet structure.
- Make sure every problem has a corresponding answer.
- Do not introduce new concepts outside the blueprint.

Return ONLY valid JSON in this exact format:

{{
  "title": "Worksheet title",
  "instructions": "Student instructions",
  "problems": [
    "Problem 1",
    "Problem 2"
  ],
  "answer_key": [
    "Answer 1",
    "Answer 2"
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

    return Worksheet(**data)


def revise_lesson_resources(
    blueprint: LessonBlueprint,
    lesson_resources: LessonResources,
    alignment_report: AlignmentReport
) -> LessonResources:

    prompt = f"""
You are revising lesson resources to fix instructional alignment problems.

LESSON BLUEPRINT:
{json.dumps(blueprint.model_dump(), indent=2)}

CURRENT LESSON RESOURCES:
{json.dumps(lesson_resources.model_dump(), indent=2)}

ALIGNMENT PROBLEMS:
{json.dumps(alignment_report.model_dump(), indent=2)}

Revise the lesson resources so that the reported alignment problems are fixed.

The lesson sequence has already been designed.
Do NOT redesign the lesson sequence.

Rules:

1. Preserve exactly one resource section for each lesson_sequence step.

2. Keep the resource sections in the same order as the lesson_sequence.

3. Preserve the exact time for each corresponding lesson step.

4. Preserve the exact activity for each corresponding lesson step.

5. Do NOT add new lesson stages.

6. Do NOT omit any lesson stage.

7. Keep resources that are already aligned and useful.

8. Revise only what is necessary to fix the reported alignment problems.

9. Remove unsupported or irrelevant concepts.

10. Add missing instructional support only when the alignment report
    identifies a real gap.

11. Every resource inside a section must directly support that section's
    lesson activity.

12. Keep resources appropriate for the stated grade level.

13. Do not introduce new concepts outside the blueprint.

14. The short "step" label may be improved for readability,
    but it must still describe the same lesson step.

Return ONLY valid JSON in this exact structure:

{{
  "sections": [
    {{
      "step": "short name for the lesson step",
      "time": "exact time copied from the lesson sequence",
      "activity": "exact activity copied from the lesson sequence",
      "resources": [
        {{
          "type": "resource type",
          "description": "resource content or teacher directions"
        }}
      ]
    }}
  ]
}}

The number of sections MUST equal the number of lesson_sequence steps.
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


def revise_reading(
    blueprint: LessonBlueprint,
    reading: ReadingMaterial,
    alignment_report: AlignmentReport
) -> ReadingMaterial:

    prompt = f"""
You are revising a reading passage to fix instructional alignment problems.

LESSON BLUEPRINT:
{json.dumps(blueprint.model_dump(), indent=2)}

CURRENT READING:
{json.dumps(reading.model_dump(), indent=2)}

ALIGNMENT PROBLEMS:
{json.dumps(alignment_report.model_dump(), indent=2)}

Revise the reading so that the reported alignment problems are fixed.

Rules:

- Keep content that is already aligned and useful.
- Revise only what is necessary.
- Remove unsupported or unnecessarily advanced concepts.
- Keep the reading appropriate for the stated grade level.
- Make sure the reading supports the lesson objective and concepts.
- Do not introduce new concepts outside the blueprint.
- Preserve the same general structure.

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


def revise_quiz(
    blueprint: LessonBlueprint,
    quiz: Quiz,
    revision_context: dict
) -> Quiz:

    prompt = f"""
You are revising a quiz to fix the problems described in the revision context.

LESSON BLUEPRINT:
{json.dumps(blueprint.model_dump(), indent=2)}

CURRENT QUIZ:
{json.dumps(quiz.model_dump(), indent=2)}

REVISION CONTEXT:
{json.dumps(revision_context, indent=2)}

Revise the quiz so that the problems described in the revision context are fixed.

Rules:

- Keep quiz questions that are already correct and aligned.
- Revise only questions that need correction.

- If the revision context contains an answer verification problem,
  correct the answer key and revise the question or options only when necessary.

- If the revision context contains an alignment problem,
  revise the quiz content to restore alignment with the lesson blueprint.

- Remove unsupported concepts or skills.
- Keep all questions within the lesson blueprint.
- Preserve the same number of questions when possible.
- Every question must have exactly 4 answer options.

- Each question must include:
  - question
  - options
  - correct_answer
  - concept
  - difficulty

- correct_answer must correspond to one of the provided options.
- Do not introduce new concepts outside the blueprint.
- Keep the quiz appropriate for the stated grade level.

Return ONLY valid JSON in this exact format:

{{
  "title": "Quiz title",
  "questions": [
    {{
      "question": "Question text",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "A",
      "concept": "Relevant concept",
      "difficulty": "easy"
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

    return Quiz(**data)