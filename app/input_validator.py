import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

from app.utils import parse_json_response


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


class InputValidationResult(BaseModel):
    match: bool
    suggested_subject: str | None = None
    reason: str


def validate_subject_objective(
    grade: int,
    subject: str,
    objective: str
) -> InputValidationResult:

    prompt = f"""
You are checking whether a teacher's selected subject
and lesson objective are reasonably compatible.

Grade:
{grade}

Selected subject:
{subject}

Lesson objective:
{objective}

Important rules:

- Do NOT be overly strict.
- Cross-disciplinary lessons are allowed.
- If the objective can reasonably fit the selected subject,
  set match to true.
- Only set match to false when the mismatch is clear and substantial.
- If match is false, suggest the single most appropriate subject.
- Keep the reason short and teacher-friendly.

Examples:

Selected subject: Music
Objective: Explain how tempo and dynamics affect mood.
→ match: true

Selected subject: Music
Objective: Analyze how an author develops theme using textual evidence.
→ likely match: false
→ suggested subject: English Language Arts

Selected subject: Science
Objective: Write an evidence-based explanation of climate change.
→ match: true
because writing can support science learning.

Selected subject: Social Studies
Objective: Calculate percentages in a population dataset.
→ this may still be valid if used for historical or demographic analysis,
so do not automatically reject it.

Return ONLY valid JSON:

{{
  "match": true,
  "suggested_subject": null,
  "reason": "The objective is appropriate for the selected subject."
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

    return InputValidationResult(**data)