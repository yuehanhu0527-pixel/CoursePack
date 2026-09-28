import os
import json

from dotenv import load_dotenv
from openai import OpenAI

from app.models import LessonBlueprint, Quiz
from app.utils import parse_json_response


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def generate_quiz(
    blueprint: LessonBlueprint,
    num_questions: int = 5
) -> Quiz:

    prompt = f"""
You are an experienced teacher.

Create a quiz based ONLY on the lesson blueprint below.

Grade: {blueprint.grade}
Subject: {blueprint.subject}
Learning objective: {blueprint.objective}

Concepts:
{blueprint.concepts}

Assessment targets:
{blueprint.assessment_targets}

Create exactly {num_questions} multiple-choice questions.

Rules:
- Only test concepts included in the blueprint.
- Each question must have exactly 4 answer options.
- Only one option can be correct.
- Use a mix of easy, medium, and hard questions.
- Return ONLY valid JSON.

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

ASSESSMENT CONSISTENCY RULES:

- Make sure the question stem, options, correct answer,
  and concept label are semantically consistent.

- The correct answer must actually answer what the question asks.

- Do not label a direct effect as an indirect effect,
  or one concept as another related concept.

- If the objective requires students to analyze, explain,
  apply, or use evidence, include questions that actually require
  that level of thinking.

- Do not make the entire quiz definition-only
  when the learning objective requires application or analysis.

- Do not introduce a substantially new skill, task type,
  or problem structure that is not supported by the blueprint,
  lesson concepts, or assessment targets.

Return this exact structure:

{{
  "title": "Quiz title",
  "questions": [
    {{
      "question": "Question text",
      "options": [
        "A. ...",
        "B. ...",
        "C. ...",
        "D. ..."
      ],
      "correct_answer": "A",
      "concept": "concept being tested",
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

