import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from app.utils import parse_json_response

from app.models import (
    AlignmentReport,
    RevisionDecision
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def decide_revision(
    alignment_report: AlignmentReport
) -> RevisionDecision:

    report_data = alignment_report.model_dump()

    prompt = f"""
You are deciding what should be revised in an instructional course pack.

ALIGNMENT REPORT:
{json.dumps(report_data, indent=2)}

Choose the single most appropriate next action.

Allowed actions:

- revise_quiz
- revise_lesson_resources
- revise_reading
- revise_worksheet
- no_revision

Rules:

1. Identify which material is actually responsible for the alignment problem.

2. Revise only the material that needs correction.
   Do not regenerate unrelated materials.

3. Use the affected_materials and evidence in the alignment report.

4. If several issues point to the same material, choose that material.

5. If the reported issue is minor and does not require changing instructional content,
   choose "no_revision".

Return ONLY valid JSON:

{{
  "action": "revise_worksheet",
  "reason": "The worksheet contains unsupported content that is outside the lesson blueprint."
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

    return RevisionDecision(**data)