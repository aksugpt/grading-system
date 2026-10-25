"""Settings for the essay grader. Change the model name here if Groq retires it."""

MODEL = "qwen/qwen3.8-27b"  # alternative: "openai/gpt-oss-120b"
TEMPERATURE = 0.1
NUM_RUNS = 1  # set to 3 to average several gradings for steadier scores

# Each criterion is scored 0-10. Weights must add up to 1.0.
WEIGHTS = {
    "content": 0.30,
    "argument": 0.25,
    "organization": 0.20,
    "language": 0.15,
    "clarity": 0.10,
}

# Overall score is 0-100. Lower bound of each letter grade.
GRADE_BANDS = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0, "F"),
]

MAX_ESSAY_CHARS = 20000
