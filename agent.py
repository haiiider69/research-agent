import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from ddgs import DDGS
import requests
from bs4 import BeautifulSoup

load_dotenv()
client = genai.Client()

MODEL = "gemini-3.5-flash-lite"
MAX_STEPS = 5

SYSTEM = (
    "You are a research assistant. Use web_search to find sources. "
    "Then use read_page to read the most promising link in full before answering. "
    "Finish with a short answer and list the source URLs you used."
)


def web_search(query: str) -> str:
    """Search the web for current information. Returns titles, links and snippets."""
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
)


def run_agent(question: str) -> str:
    contents = [types.Content(role="user", parts=[types.Part(text=question)])]

    for step in range(MAX_STEPS):
        response = client.models.generate_content(
            model=MODEL, contents=contents, config=config
        )

        # No tool requested -> the model is done
        if not response.function_calls:
            return response.text

        # Keep the model's request in the conversation
        contents.append(response.candidates[0].content)

        # Run each requested search and send the results back
        parts = []
        for call in response.function_calls:
            
                print(f"[step {step + 1}] {call.name}: {call.args}")
                result = TOOLS[call.name](**call.args)
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