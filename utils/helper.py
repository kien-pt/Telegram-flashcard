import json
import string

from google import genai
from pydantic import BaseModel
from google.genai import types

from utils.constants import GEMINI_API_KEY, UPSKILL_ENGLISH_PROMPT


class QuestionSchema(BaseModel):
    question: str
    optionA: str
    optionB: str
    optionC: str
    optionD: str
    answer: str
    explain: str


def remove_punc(text):
    exclude = set(string.punctuation)
    return ''.join(ch for ch in text if ch not in exclude)


def replace_space_with_underscope(text: str):
    space = " "
    underscore = r"\_"
    return text.replace(space, underscore)


def normalize_text(text: str):
    return replace_space_with_underscope(remove_punc(text))


def get_question(prompt: str):
    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=QuestionSchema,
            temperature=0.7,
        ),
    )
    return json.loads(response.text)