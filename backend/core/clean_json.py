import json
import re
import ast

def clean_json_response(content: str) -> list:
    try:
        content = re.sub(r"^```json|```$", "", content.strip(), flags=re.MULTILINE).strip()
        return json.loads(content)
    except json.JSONDecodeError as e:
        # logger.error(f"Failed to decode LLM response: {e}")
        return []
