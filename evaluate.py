import json
import re
import sys
import time
from agent import run_agent

QUESTIONS_FILE = sys.argv[1] if len(sys.argv) > 1 else "questions.json"

with open(QUESTIONS_FILE, encoding="utf-8") as f:
    tests = json.load(f)

LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else len(tests)
tests = tests[:LIMIT]


def clean(url):
    return url.rstrip(".,;:!?'\"*)]").rstrip("/")


def sources_ok(answer, seen):
    cited = [clean(u) for u in re.findall(r'https?://[^\s"<>\\]+', answer)]
    seen_clean = {clean(u) for u in seen}
    return bool(cited) and all(u in seen_clean for u in cited)


def mark(ok):
    return "✅" if ok else "❌"


totals = {"correct": 0, "web": 0, "sources": 0, "full": 0}

for i, test in enumerate(tests, start=1):
    print(f"\n=== Question {i}/{len(tests)}: {test['question']}")
    trace = {}
    try:
        answer = run_agent(test["question"], trace=trace)
    except Exception as e:
        answer = f"ERROR: {e}"

    correct = test["expected"].lower() in answer.lower()
    used_web = bool(trace.get("tools"))
    sources = sources_ok(answer, trace.get("urls", set()))
    full = correct and used_web and sources

    totals["correct"] += correct
    totals["web"] += used_web
    totals["sources"] += sources
    totals["full"] += full

    print(f"   tools used: {trace.get('tools', [])} | URLs seen: {len(trace.get('urls', []))}")
    print(f"   correct: {mark(correct)} | used web: {mark(used_web)} | sources valid: {mark(sources)}")
    if not full:
        print(f"   expected '{test['expected']}' | Agent answered: {answer[:300]}")

    time.sleep(5)  # pause between questions to respect the free tier

n = len(tests)
print(f"\nCorrect answer:        {totals['correct']}/{n}")
print(f"Used the web:          {totals['web']}/{n}")
print(f"Sources valid:         {totals['sources']}/{n}")
print(f"FULL PASS (all three): {totals['full']}/{n} = {totals['full'] / n:.0%}")