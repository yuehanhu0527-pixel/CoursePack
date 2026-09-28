import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from app.utils import parse_json_response

from app.models import (
    LessonBlueprint,
    Worksheet
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def generate_worksheet(
    blueprint: LessonBlueprint,
    num_problems: int = 6
) -> Worksheet:

    prompt = f"""
You are an instructional designer.

Create a student practice worksheet based ONLY on the lesson blueprint below.

Grade: {blueprint.grade}
Subject: {blueprint.subject}
Learning objective: {blueprint.objective}

Concepts:
{blueprint.concepts}

Assessment targets:
{blueprint.assessment_targets}

Create exactly {num_problems} practice problems.

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

- If a worksheet asks students to analyze a source,
  the source must either be clearly identified as a real source
  or clearly labeled as adapted/simulated practice material.

ASSESSMENT CONSISTENCY RULES:

- Make sure each problem and its corresponding answer are
  semantically consistent.

- The answer must directly respond to what the problem asks.

- Do not confuse related concepts such as cause vs. effect,
  direct vs. indirect effect, theme vs. topic,
  or definition vs. application.

- If the learning objective requires students to explain,
  analyze, apply, or use evidence, include practice problems
  that actually require that level of thinking.

- Do not make the worksheet entirely definition-based
  when the objective requires application or analysis.

- Do not introduce a substantially new skill, task type,
  or problem structure that is not supported by the blueprint,
  lesson concepts, or assessment targets.
  
Return ONLY valid JSON in this exact structure:

{{
  "title": "Worksheet title",
  "instructions": "Short student instructions",
  "problems": [
    "Problem 1",
    "Problem 2"
  ],
  "answer_key": [
    "Answer 1",
    "Answer 2"
  ]
}}

Rules:
- Stay within the lesson blueprint.
- Problems should be appropriate for the grade level.
- Use a reasonable progression from easier to harder problems.
- Include exactly {num_problems} problems.
- The answer_key must contain exactly {num_problems} answers.
- Keep each answer in the same order as its corresponding problem.
- Do not introduce concepts outside the blueprint.
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