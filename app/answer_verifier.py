import os
from dotenv import load_dotenv
from openai import OpenAI
from app.utils import parse_json_response
import json

from app.models import(
     AnswerVerificationReport,
    Quiz
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def verify_quiz_answers(
        quiz:Quiz
)->AnswerVerificationReport:
    
    quiz_data = [
        {
            "question_number":index + 1,
            "question":question.question,
            "options":question.options,
            "correct_answer":question.correct_answer
        }
        for index, question in enumerate(quiz.questions)
    ]

    prompt = f"""
You are checking whether the marked answers in a quiz are actually correct.enumerate

QUIZ:
{json.dumps(quiz_data, indent =2)}

For EACH question:

1.Solve the question yourself. 
2.Determine which option is actually correct. 
3. Read the quiz's provided "correct_answer".
4. Compare the provided "correct_answer" with the answer you independently determined.

IMPORTANT:
- "correct" means whether the PROVIDED correct_answer is correct.
- If the provided correct_answer does NOT match the actual correct option,
  set "correct" to false.
- "expected_answer" must contain the actual correct option.
- Do NOT set "correct" to true just because you successfully found the right answer.

Example:

If the quiz says:
"correct_answer": "D"

but you determine the actual answer is "B",

return:

{{
  "question_number": 1,
  "correct": false,
  "expected_answer": "B",
  "reason": "The provided answer D is incorrect. The actual correct answer is B because ..."
}}

Return ONLY valid JSON in this exact format:

{{
  "passed": true,
  "results": [
    {{
      "question_number": 1,
      "correct": true,
      "expected_answer": "B",
      "reason": "Short explanation of why B is correct."
    }}
  ]
}}

Set "passed" to true ONLY if every marked answer is correct.enumerate
"""

    response = client.chat.completions.create(
        model = "deepseek-chat",
        messages = [
            {
                "role":"user",
                "content":prompt
            }
        ]
    )

    content = response.choices[0].message.content
    data = parse_json_response(content)

    for result in data["results"]:
        question_index = result["question_number"] - 1

        provided_answer = quiz.questions[question_index].correct_answer
        expected_answer = result["expected_answer"]

        result["correct"] = (
            provided_answer.strip().upper()
            == expected_answer.strip().upper()
        )

    data["passed"] = all(
        result["correct"]
        for result in data["results"]
    )

    return AnswerVerificationReport(**data)