import re

prompts = [
    "Step 1: X. Step 2: Y.",
    "First, X. Then, Y."
]

for prompt in prompts:
    print(f"Prompt: {prompt}")
    sequential_match = re.search(
        r'^(.*?)\b(First|Initially|Start by|Step 1:?|Do)\b\s*(.*?)\s*\b(Then|Next|After that|Step 2:?|do)\b\s*(.*?)(?:\s*\b(Finally|Lastly|Step 3:?)\b\s*(.*))?$',
        prompt,
        re.IGNORECASE | re.DOTALL
    )
    if sequential_match:
        print("Matched!")
    else:
        print("Failed!")
