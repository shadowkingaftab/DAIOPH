import re

prompts = [
    "I need to plan a weekend trip. First, suggest 3 destinations within 300 miles of New York City. Then, for the best option, create a detailed itinerary with activities for Saturday and Sunday.",
    "First, research the best laptops for programming. Then, compare their specs in a table. Finally, recommend the best one and explain why.",
    "Do X. Then do Y."
]

for prompt in prompts:
    print(f"Prompt: {prompt}")
    sequential_match = re.search(
        r'^(.*?)\b(First|Initially|Start by|Step 1:?|Do)\b\s*(.*?)\s*\b(Then|Next|After that|Step 2:?|do)\b\s*(.*?)(?:\s*\b(Finally|Lastly|Step 3:?)\b\s*(.*))?$',
        prompt,
        re.IGNORECASE | re.DOTALL
    )
    if sequential_match:
        prefix = sequential_match.group(1).strip()
        task1_core = sequential_match.group(3).strip().lstrip(',').strip()
        task2_core = sequential_match.group(5).strip().lstrip(',').strip()
        task3_core = sequential_match.group(7)
        if task3_core:
            task3_core = task3_core.strip().lstrip(',').strip()
            
        task1 = f"{prefix} {task1_core}".strip() if prefix else task1_core
        print("Task 1:", task1)
        print("Task 2:", task2_core)
        if task3_core:
            print("Task 3:", task3_core)
    else:
        print("No match")
    print("-" * 40)
