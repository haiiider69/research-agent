import json
from dotenv import load_dotenv
from google import genai
from google.genai import types
from ddgs import DDGS

load_dotenv()
client = genai.Client()

MODEL = "gemini-3.5-flash-lite"
MAX_STEPS = 5

SYSTEM = (
    "You are a research assistant. Use web_search when you need facts. "
    "Finish with a short answer and list the source URLs you used."
)


def web_search(query: str) -> str:
    """Search the web for current information. Returns titles, links and snippets."""
    results = DDGS().text(query, max_results=5)
    return json.dumps(results, ensure_ascii=False)


config = types.GenerateContentConfig(
    system_instruction=SYSTEM,
    tools=[web_search],
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
            print(f"[step {step + 1}] searching: {call.args['query']}")
            result = web_search(**call.args)
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