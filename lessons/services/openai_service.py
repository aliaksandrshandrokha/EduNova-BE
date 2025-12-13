"""
OpenAI service for generating lesson content (more reliable JSON).
"""
import os
import json
import logging
import time
from typing import Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

_client = None

def get_openai_client():
    """Get or create OpenAI client instance (lazy initialization)."""
    global _client
    if _client is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                _client = OpenAI(api_key=api_key)
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                _client = False
        else:
            logger.warning("OPENAI_API_KEY not found in environment variables. OpenAI features will not work.")
            _client = False
    return _client if _client is not False else None


def _lesson_schema() -> Dict[str, Any]:
    # Structured Outputs: strict schema + additionalProperties false prevents extra keys. [web:294][web:297]
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "description": {"type": "string"},
            "content": {"type": "string"},
            "activities": {"type": "array", "items": {"type": "string"}},
            "questions": {"type": "array", "items": {"type": "string"}},
            "summary": {"type": "string"},
        },
        "required": ["description", "content", "activities", "questions", "summary"],
    }


def _validate_result(result: Dict[str, Any]) -> None:
    expected_keys = {"description", "content", "activities", "questions", "summary"}
    if set(result.keys()) != expected_keys:
        raise ValueError(f"Unexpected keys returned: {sorted(set(result.keys()) - expected_keys)}")

    if not isinstance(result["description"], str): raise ValueError("description must be string")
    if not isinstance(result["content"], str): raise ValueError("content must be string")
    if not isinstance(result["summary"], str): raise ValueError("summary must be string")
    if not isinstance(result["activities"], list) or not all(isinstance(x, str) for x in result["activities"]):
        raise ValueError("activities must be list[str]")
    if not isinstance(result["questions"], list) or not all(isinstance(x, str) for x in result["questions"]):
        raise ValueError("questions must be list[str]")


def generate_lesson_content(topic: str, subject: str, grade_level: str, duration_minutes: int) -> Dict[str, Any]:
    client = get_openai_client()
    if not client:
        raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in your environment variables.")

    # Params by duration
    if duration_minutes <= 30:
        paragraphs = "4-5"
        min_words = 400
        max_tokens = 1600  # increased to reduce truncation risk
        activities_count = "5-7"
        questions_count = "6-10"
        lesson_type = "SHORT"
    elif duration_minutes <= 60:
        paragraphs = "7-9"
        min_words = 600
        max_tokens = 2600
        activities_count = "6-8"
        questions_count = "8-12"
        lesson_type = "MEDIUM"
    else:
        paragraphs = "12-16"
        min_words = 800
        max_tokens = 4200
        activities_count = "8-10"
        questions_count = "10-15"
        lesson_type = "LONG"

    prompt = f"""Generate educational lesson content for:

Topic: {topic}
Subject: {subject}
Grade: {grade_level}
Duration: {duration_minutes} minutes

Return ONLY a JSON object with EXACTLY these keys:
description, content, activities, questions, summary

Rules:
- description: ~250-word overview explaining the topic, importance, and learning objectives for {grade_level}
- content: {paragraphs} distinct paragraphs (minimum {min_words} words total), separated by \\n\\n
  - Each paragraph 80-150 words
  - Include examples, explanations, and real-world connections
  - This is a {duration_minutes}-minute ({lesson_type}) lesson, so content MUST be proportionally detailed
- activities: {activities_count} items (array of strings), each with clear instructions + objective
- questions: {questions_count} items (array of strings), mixed difficulty
- summary: exactly 5 sentences

Do not include markdown/code fences. Do not include any other keys.
"""

    model = os.getenv("OPENAI_LESSON_MODEL", "gpt-4o")

    schema = _lesson_schema()

    last_error: Exception | None = None

    # Retry on truncation / invalid JSON / schema mismatch. [web:300]
    for attempt in range(1, 4):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert educational content creator. "
                            "Output MUST be valid JSON that conforms to the provided schema. "
                            "No markdown, no commentary."
                        ),
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # lower randomness => fewer formatting issues
                max_tokens=max_tokens,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "lesson_content",
                        "schema": schema,
                        "strict": True,
                    },
                },
            )

            finish_reason = getattr(response.choices[0], "finish_reason", None)
            raw = (response.choices[0].message.content or "").strip()

            # If truncated, retry with higher max_tokens or same (common cause of unterminated strings). [web:300]
            if finish_reason == "length":
                raise ValueError("Model output truncated (finish_reason=length).")

            if not raw:
                raise ValueError("Empty response content from model.")

            # With strict schema this should already be valid JSON, but keep parsing explicitly.
            result = json.loads(raw)
            _validate_result(result)

            # Validate minimum content length (keep your tolerance)
            content_text = result.get("content", "")
            word_count = len(content_text.split())
            if word_count < int(min_words * 0.7):
                raise ValueError(
                    f"Content too short: {word_count} words (expected ~{min_words}+ for {duration_minutes} min)."
                )

            # Validate paragraph structure (soft check)
            paragraph_count = len([p for p in content_text.split("\n\n") if p.strip()])
            if paragraph_count < 3:
                logger.warning(
                    f"Content appears to have only {paragraph_count} paragraph(s). Expected ~{paragraphs}."
                )

            return {
                "description": result["description"],
                "content": result["content"],
                "activities": result["activities"],
                "questions": result["questions"],
                "summary": result["summary"],
            }

        except Exception as e:
            last_error = e
            logger.error(f"Attempt {attempt}/3 failed: {e}")
            time.sleep(0.6 * attempt)

    raise Exception(f"Failed to generate lesson content after retries: {last_error}")
