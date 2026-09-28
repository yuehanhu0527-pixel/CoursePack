import json


def parse_json_response(content: str):
    if content is None:
        raise ValueError("LLM returned no content.")

    content = content.strip()

    if not content:
        raise ValueError("LLM returned empty content.")

    if content.startswith("```json"):
        content = content[len("```json"):]

    elif content.startswith("```"):
        content = content[len("```"):]

    if content.endswith("```"):
        content = content[:-3]

    content = content.strip()

    return json.loads(content)