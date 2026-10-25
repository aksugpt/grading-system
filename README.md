# Essay Grader

Paste an essay, get a 0-100 score, a letter grade, per-criterion scores and feedback.
Uses an open-source LLM (Qwen3.8 27B) through the Groq API. Groq retires models from time to time; if you get a "model_not_found" error, pick a current one in `config.py`.

## Setup

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env      # then put your Groq key in .env
```

## Run

```
streamlit run app.py
```

## Tweaking

- `config.py`: model name, criterion weights, grade bands, number of runs to average.
- `prompts.py`: the rubric text the model sees. Better rubric descriptions = better grades.
- `samples/`: example essays for testing.
