import string
import json
import re
import requests

from utils.constants import GEMINI_API_KEY, UPSKILL_ENGLISH_PROMPT


def remove_punc(text):
    exclude = set(string.punctuation)
    return ''.join(ch for ch in text if ch not in exclude)


def replace_space_with_underscope(text: str):
    space = " "
    underscore = "\_"
    return text.replace(space, underscore)


def normalize_text(text: str):
    return replace_space_with_underscope(remove_punc(text))


def get_question(prompt: str):
    response = requests.post(
        "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
        headers={'X-goog-api-key': GEMINI_API_KEY},
        json={"contents": [{"parts": [{ "text": prompt }]}]},
    )
    text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    else:
        return None