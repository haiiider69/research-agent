
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

  <img width="1908" height="957" alt="research agent" src="https://github.com/user-attachments/assets/1fe86283-a6ed-496a-ab35-ed869ae0f3f8" />

## Roadmap

- [x] Version 1: agent loop with a web search tool
- [x] Version 2: tool to read full web pages
- [x] Version 3: Streamlit interface
- [ ] Version 4: evaluation with test questions
