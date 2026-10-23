from ddgs import DDGS

results = DDGS().text("latest stable Python version", max_results=3)

for r in results:
    print(r["title"])
    print(r["href"])
    print()