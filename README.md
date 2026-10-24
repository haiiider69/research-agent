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

## Tech stack

- Python
- Gemini API (`google-genai`)
- DuckDuckGo search (`ddgs`)

## Roadmap

- [x] Version 1: agent loop with a web search tool
- [x] Version 2: tool to read full web pages
- [ ] Version 3: Streamlit interface
- [ ] Version 4: evaluation with test questions