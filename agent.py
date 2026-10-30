import json
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai import errors
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup
import time
from datetime import date

load_dotenv()
client = genai.Client()

MODEL = "gemini-3.5-flash-lite"
MAX_STEPS = 5

SYSTEM = (
    f"Today's date is {date.today().isoformat()}. "
    "You are a research assistant. Use web_search to find sources. "
    "Do at most 3 searches in total. Then use read_page on the most promising link. "
    "After that, answer: a short answer followed by the source URLs you used. "
    "If sources conflict, prefer the most recent one."
)


def web_search(query: str) -> str:
    """Search the web for current information. Returns titles, links and snippets."""
    if not query or not query.strip():
        return "No search query was given. Call web_search again with a query text."
    try:
        results = DDGS().text(query, max_results=5)
    except Exception as e:
        return f"Search failed: {e}. Try a different, shorter query."
    return json.dumps(results, ensure_ascii=False)

def read_page(url: str) -> str:
    """Download a web page and return its main text(remove extra's from html template only leaves texts)."""
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Could not read the page: {e}"

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = " ".join(soup.get_text(separator=" ").split())
    return text[:6000]

TOOLS = {"web_search": web_search, "read_page": read_page}


config = types.GenerateContentConfig(
    system_instruction=SYSTEM,
    tools=[web_search, read_page],
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
     tool_config=types.ToolConfig(
        function_calling_config=types.FunctionCallingConfig(mode="NONE")
    ),
)
final_config = types.GenerateContentConfig(
    system_instruction=SYSTEM
    + " You can no longer use tools. Answer now using what you already know or found.",
)
MIN_GAP = 5  # seconds between model calls (the free tier allows 15 per minute)
_last_call = 0.0


def ask_model(contents, cfg=None):
    global _last_call
    use_cfg = cfg or config
    for attempt in range(4):
        pause = MIN_GAP - (time.time() - _last_call)
        if pause > 0:
            time.sleep(pause)
        _last_call = time.time()
        try:
            response = client.models.generate_content(
                model=MODEL, contents=contents, config=use_cfg
            )
        except errors.ServerError as e:
            print(f"Model busy ({e.code}), retrying...")
            time.sleep(2 ** (attempt + 1))
            continue
        except errors.ClientError as e:
            if e.code == 429:
                print("Rate limit reached, waiting 30s...")
                time.sleep(30)
                continue
            raise
        if response.function_calls or response.text:
            return response
        reason = response.candidates[0].finish_reason if response.candidates else "no candidates"
        print(f"   [empty reply, finish reason: {reason}]")
        if attempt >= 1:
            print("   [switching to answering without tools]")
            use_cfg = final_config
    raise RuntimeError("The model is busy or keeps returning empty replies. Try again in a minute.")

def run_agent(question: str, on_step=None) -> str:
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]

    for step in range(MAX_STEPS):
        last_step = step == MAX_STEPS - 1
        response = ask_model(contents, final_config if last_step else None)
        
        if not response.function_calls:
            if not response.text:
                reason = response.candidates[0].finish_reason if response.candidates else "no candidates"
                print(f"   [empty answer] finish reason: {reason}")
            return response.text or ""

        # Keep the model's request in the conversation
        contents.append(response.candidates[0].content)

        # Run each requested search and send the results back
        parts = []
        for call in response.function_calls:
            
                message = f"[step {step + 1}] {call.name}: {call.args}"
                print(message)
                if on_step:
                    on_step(message)
                args = dict(call.args)
                if "queries" in args:
                    good = [q for q in args.pop("queries")if isinstance(q, str) and q.strip()]
                    args["query"] = good[0] if good else ""
                result = TOOLS[call.name](**args)
                print(f"   -> {str(result)[:150]}")

                parts.append(
                types.Part.from_function_response(
                    name=call.name, response={"result": result}
                )
            )
        contents.append(types.Content(role="user", parts=parts))

    return "Stopped: reached the step limit."


if __name__ == "__main__":
    q = input("Question: ")
    print("\n" + run_agent(q))