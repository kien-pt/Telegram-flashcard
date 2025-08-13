import os

from dotenv import load_dotenv


HELLO_WORLD_TEXT =\
"""
 .---------------------------------.
| .-------------------------------. |
| |   _  ___          ___ _____   | |
| |  | |/ (_)___ _ _ | _ \_   _|  | |
| |  | ' <| / -_) ' \|  _/ | |    | |
| |  |_|\_\_\___|_||_|_|   |_|    | |
| |              Bot Flashcard    | |
| '-------------------------------' |
 '---------------------------------'                                                        
"""

START_TEXT = """
Welcome to the bot!

Select the topic you want to learn:
1. Vocabulary
2. Upskill English
"""

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELETHON_API_ID    = os.getenv("TELETHON_API_ID")
TELETHON_API_HASH  = os.getenv("TELETHON_API_HASH")
GEMINI_API_KEY     = os.getenv("GEMINI_API_KEY")
TELEGRAM_ADMIN_ID  = -1002333467815

NUMBER_EMOJI = ["1️⃣", "2️⃣", "3️⃣", "4️⃣"]

UPSKILL_ENGLISH_PROMPT = """
Task: Generate one multiple-choice question (MCQ) using the specified JSON format. The questions should be designed for someone aiming to achieve an IELTS score of 7 or higher.
			
Topics to Choose From:
	- Grammatical Error Identification
	- Sentence Completion
	- Sentence Correction
	- Synonyms and Antonyms
	- Appropriate Word Usage
	- Contextual Vocabulary
	- Coherence and Cohesion
	- Argument Analysis
	- Assumption Identification
	- Idioms and Phrasal Verbs

Requirements:
	- Each question should clearly state the task in the `question` field.
	- Provide four answer options (`optionA`, `optionB`, `optionC`, `optionD`) for each question.
	- Indicate the correct answer by setting the `answer` field to one of the options (`a`, `b`, `c`, or `d`).
	- Ensure that no question is repeated within the same response.
	- Use the JSON structure below for formatting the questions:

Here is an example of this JSON:
	{
		"question": "Markdown String",
		"optionA": "String",
		"optionB": "String",
		"optionC": "String",
		"optionD": "String",
		"answer": "a | b | c | d",
		"explain": "Markdown String",
	}

Notes:
	- Choosen topic must be random.
	- Replace "String" with appropriate text for each field. Only use "a", "b", "c", or "d" in the `answer` field.
	- "question" and "explain" could be in Markdown format.
    - ONLY RETURN THE RAW JSON OF THE RESPONSE.
"""
