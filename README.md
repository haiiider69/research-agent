
# Research Agent

A small AI agent that answers questions by searching the web, reading the results, and replying with sources. Built with Python and the Gemini API.

## How it works

1. You ask a question.
2. The model decides whether it needs to search the web.
3. If so, it asks for a web search or to read a page in full, my code runs it, and the results go back to the model. If a tool fails, the error goes back to the model, which can try something else.
4. This repeats (max 5 steps) until the model writes a final answer with source URLs.

## Setup

1. Clone the repo and create a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Create a `.env` file with your free Gemini API key (from Google AI Studio):

```
GEMINI_API_KEY=your_key_here
```

3. Run the agent:

```bash
python agent.py
```
4. Or launch the web interface:

```bash
streamlit run app.py
```

The page shows the agent's steps live while it searches and reads, then displays the final answer with sources.

## Tech stack

- Python
- Gemini API (`google-genai`)
- DuckDuckGo search (`ddgs`)
- Streamlit


## Evaluation

`evaluate.py` runs the agent on a questions file and scores each answer.

```bash
python evaluate.py                      # easy set (questions.json)
python evaluate.py questions_web.json   # harder set, needs the web
python evaluate.py questions_web.json 1 # only the first question
```

Each question on the harder set gets three checks:

1. **Correct**: the answer contains the expected keyword.
2. **Used the web**: the agent ran at least one tool.
3. **Sources valid**: the answer cites at least one URL, and every cited URL appeared in a tool result (no invented links).

A question counts toward the score only if it passes all three.

| Set | Result |
|-----|--------|
| `questions.json` (14 easy questions, answer check only) | 13/14 (93%) |
| `questions_web.json` (7 questions about 2026 events, three checks) | 3/7 (43%) full pass |

Reading the harder result: the 4 failures were not wrong answers. In each one the free-tier model kept returning a malformed tool call and the agent gave up before searching. The 3 questions that got through passed all three checks. A single run is a small sample, and results vary between runs.

Known limitations:
- Small test sets and simple keyword matching, so a wrong answer can pass and a correct one can fail.
- The "sources valid" check shows the agent did not invent a URL; it does not prove the page supports the claim.
- The free-tier Gemini model intermittently returns `MALFORMED_FUNCTION_CALL`. The agent retries, but the cause is not yet understood.
- The fallback that answers without tools after repeated malformed calls did not help in the one run where it was triggered.
- A full run uses a noticeable share of the free-tier daily quota.


## Roadmap

- [x] Version 1: agent loop with a web search tool
- [x] Version 2: tool to read full web pages
- [x] Version 3: Streamlit interface
- [x] Version 4: evaluation with test questions


## Interface
  <img width="1908" height="957" alt="research agent" src="https://github.com/user-attachments/assets/1fe86283-a6ed-496a-ab35-ed869ae0f3f8" />
