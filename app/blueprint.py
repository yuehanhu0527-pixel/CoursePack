import os
import json

from dotenv import load_dotenv
from openai import OpenAI
from app.models import LessonBlueprint
from app.utils import parse_json_response

load_dotenv()

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                base_url="https://api.deepseek.com")

def build_blueprint(

        grade:int,
        subject:str,
        objective:str,
        class_length: int,
) ->LessonBlueprint:

    prompt = f"""
You are an instructional designer.

Create a lesson blueprint based on:

Grade: {grade}
Subject: {subject}
Learning objective: {objective}
Class length: {class_length} minutes

Return ONLY valid JSON.

Use this exact structure:

{{
  "concepts": [],
  "prerequisites": [],
  "vocabulary": [],
  "lesson_sequence": [
    {{
      "time": "0-5 min",
      "activity": "Description of the activity"
    }}
  ],
  "assessment_targets": []
}}

IMPORTANT:
Every item in "lesson_sequence" must contain exactly:
- "time": a string such as "0-5 min"
- "activity": a string

Do not use "time_minutes".
Do not rename any fields.
"""

    response = client.chat.completions.create(
        model = 'deepseek-chat',
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    content = response.choices[0].message.content

    data = parse_json_response(content)


    for step in data.get("lesson_sequence", []):
        if "time" not in step and "time_minutes" in step:
            step["time"] = f'{step["time_minutes"]} min'

    data["grade"] = grade
    data["subject"] = subject
    data["objective"] = objective
    data["class_length"] = class_length

    return LessonBlueprint(**data)