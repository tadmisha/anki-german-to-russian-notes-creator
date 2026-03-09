import os
import groq
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()

_GROQ_API_KEY = os.getenv("GROQ_API_KEY")

_example_generation_prompt_path = Path(__file__).parent / "data" / "prompts" / "example_generator_prompt.txt"
_tag_selection_prompt_path = Path(__file__).parent / "data" / "prompts" / "tags_selection_prompt.txt"

with open(_example_generation_prompt_path, "r", encoding="utf-8") as file:
    _example_generation_prompt_base = file.read()

with open(_tag_selection_prompt_path, "r", encoding="utf-8") as file:
    _tag_selection_prompt_base = file.read()


_client = groq.Client(api_key=os.getenv("GROQ_API_KEY"))

def generate_example_with_translation(word: str, pos: str, russian_word: str) -> tuple[str]:
    prompt = _example_generation_prompt_base % (word, pos, word, pos, russian_word)

    response = _client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {"role": "system", "content": "You are a helpful German language tutor specialized in example creation."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=40,
        reasoning_effort="none"
    )

    content = response.choices[0].message.content.strip()

    german_sentence, russian_sentence = content.split('\n')

    return (german_sentence, russian_sentence)


def choose_most_suitable_tags(word: str, pos: str) -> tuple[str]:
    prompt = _tag_selection_prompt_base % (word, pos)

    response = _client.chat.completions.create(
        model="qwen/qwen3-32b",
        messages=[
            {"role": "system", "content": "You are a helpful language assistant specialized in categorizing German words for language learning."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=50,
        reasoning_effort="none"
    )

    content = response.choices[0].message.content.strip()

    return content
