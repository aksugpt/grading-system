import json
import os
import statistics

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from tenacity import retry, stop_after_attempt, wait_exponential

import config
from prompts import SYSTEM_PROMPT, build_user_prompt

load_dotenv()


class CriterionScore(BaseModel):
    reason: str
    score: int = Field(ge=0, le=10)


class RawGrade(BaseModel):
    content: CriterionScore
    argument: CriterionScore
    organization: CriterionScore
    language: CriterionScore
    clarity: CriterionScore
    strengths: list[str] = []
    improvements: list[str] = []
    feedback: str = ""


def letter_grade(score: float) -> str:
    for lower_bound, letter in config.GRADE_BANDS:
        if score >= lower_bound:
            return letter
    return "F"


def weighted_total(scores: dict[str, float]) -> float:
    """Combine 0-10 criterion scores into a 0-100 overall score."""
    return round(sum(scores[name] * w for name, w in config.WEIGHTS.items()) * 10, 1)


def _extract_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[4:]
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model reply")
    return json.loads(text[start : end + 1])


def _client():
    from groq import Groq

    key = os.getenv("GROQ_API_KEY")
    if not key or key == "your_key_here":
        raise RuntimeError("GROQ_API_KEY is missing. Put it in the .env file.")
    return Groq(api_key=key)


@retry(stop=stop_after_attempt(3), wait=wait_exponential(min=2, max=20), reraise=True)
def _grade_once(client, essay_prompt: str, essay: str) -> RawGrade:
    reply = client.chat.completions.create(
        model=config.MODEL,
        temperature=config.TEMPERATURE,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(essay_prompt, essay)},
        ],
    )
    return RawGrade.model_validate(_extract_json(reply.choices[0].message.content))


def grade_essay(essay: str, essay_prompt: str = "") -> dict:
    essay = essay.strip()
    if len(essay.split()) < 20:
        raise ValueError("Essay is too short to grade (need at least 20 words).")
    essay = essay[: config.MAX_ESSAY_CHARS]

    client = _client()
    runs: list[RawGrade] = []
    for _ in range(max(1, config.NUM_RUNS)):
        try:
            runs.append(_grade_once(client, essay_prompt, essay))
        except (ValidationError, ValueError, json.JSONDecodeError):
            continue
    if not runs:
        raise RuntimeError("The model did not return a valid grade. Try again.")

    scores = {
        name: statistics.median(getattr(r, name).score for r in runs)
        for name in config.WEIGHTS
    }
    total = weighted_total(scores)
    first = runs[0]
    return {
        "scores": scores,
        "reasons": {name: getattr(first, name).reason for name in config.WEIGHTS},
        "total": total,
        "letter": letter_grade(total),
        "strengths": first.strengths,
        "improvements": first.improvements,
        "feedback": first.feedback,
        "runs_used": len(runs),
    }
