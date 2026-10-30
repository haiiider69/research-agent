import json
import time
from agent import run_agent

with open("questions.json", encoding="utf-8") as f:
    tests = json.load(f)

correct = 0

for i, test in enumerate(tests, start=1):
    print(f"\n=== Question {i}/{len(tests)}: {test['question']}")
    try:
        answer = run_agent(test["question"])
    except Exception as e:
        answer = f"ERROR: {e}"

    passed = test["expected"].lower() in answer.lower()
    correct += passed
    if passed:
            print("✅ correct")
    else:
        print(f"❌ wrong (expected '{test['expected']}')")
        print(f"   Agent answered: {answer[:300]}")

    time.sleep(5)  # pause between questions to respect the free tier

print(f"\nScore: {correct}/{len(tests)} = {correct / len(tests):.0%}")