"""
classifier.py
-------------
The NLP brain of the system.
Loads a pretrained zero-shot classification model and uses it
to detect the INTENT of any text prompt, along with a confidence score.

Zero-shot means: we never trained this model on our data.
We just give it our labels and it figures out the best match.
Model used: typeform/distilbert-base-uncased-mnli (~268MB, fast)

Fine-tuned model support:
  Set CLASSIFIER_MODEL_PATH=models/fine_tuned_classifier in .env
  after running: python training/train_classifier.py --epochs 5 --eval

Multi-language support:
  Automatically detects input language using langdetect.
  Translates non-English prompts to English via googletrans.
  Sequential patterns detected in Hindi, Spanish, French, and English.
"""

import os
import re
from transformers import pipeline
from dotenv import load_dotenv
import time
import sys
from collections import defaultdict

load_dotenv()

# ── Multi-language support ────────────────────────────────────────────────────
try:
    from langdetect import detect, DetectorFactory
    DetectorFactory.seed = 0  # Ensures consistent detection results
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

try:
    from googletrans import Translator
    HAS_GOOGLETRANS = True
except ImportError:
    HAS_GOOGLETRANS = False

# ── spaCy for smarter sentence segmentation ───────────────────────────────────
try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
    HAS_SPACY = True
except Exception:
    _nlp = None
    HAS_SPACY = False

# Sequential keywords per language for smart decomposition
SEQUENTIAL_KEYWORDS = {
    "en": ["first", "then", "next", "after that", "finally", "initially", "step"],
    "hi": ["पहले", "फिर", "अगला", "उसके बाद", "अंत में", "चरण"],  # Hindi
    "es": ["primero", "luego", "después", "finalmente", "paso"],    # Spanish
    "fr": ["d'abord", "ensuite", "après", "enfin", "étape"],       # French
    "de": ["zuerst", "dann", "danach", "schließlich", "schritt"],  # German
    "ar": ["أولاً", "ثم", "بعد ذلك", "أخيراً"],                    # Arabic
}


def detect_language(text: str) -> str:
    """Detect the language of the input text. Returns ISO 639-1 language code."""
    if not HAS_LANGDETECT or not text or not text.strip():
        return "en"
    try:
        return detect(text.strip())
    except Exception:
        return "en"


def translate_to_english(text: str, src_lang: str) -> str:
    """Translate text from src_lang to English. Falls back to original on error."""
    if not HAS_GOOGLETRANS or src_lang == "en" or not text.strip():
        return text
    try:
        translator = Translator()
        result = translator.translate(text, src=src_lang, dest="en")
        return result.text if result and result.text else text
    except Exception:
        return text  # Graceful fallback — keep original text


def decompose_prompt(prompt: str, lang: str = "en") -> dict:
    """
    Intelligently decompose a prompt into sequential subtasks.
    Works for any language using keyword detection and sentence splitting.

    Returns a DAG dict with nodes for use in the orchestrator.
    """
    # Step 1: Sentence segmentation
    if HAS_SPACY and lang == "en" and _nlp:
        doc = _nlp(prompt)
        sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
    else:
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', prompt) if s.strip()]

    if not sentences:
        sentences = [prompt]

    # Step 2: Get sequential keywords for detected language
    lang_keywords = SEQUENTIAL_KEYWORDS.get(lang.lower(), SEQUENTIAL_KEYWORDS["en"])

    # Step 3: Group sentences into tasks by sequential markers
    tasks = []
    current_task = []
    for sent in sentences:
        sent_lower = sent.lower()
        is_step_start = any(kw in sent_lower for kw in lang_keywords)
        if is_step_start and current_task:
            tasks.append(" ".join(current_task).strip())
            current_task = [sent]
        else:
            current_task.append(sent)
    if current_task:
        tasks.append(" ".join(current_task).strip())

    # Step 4: If no sequential split found, chunk by sentence count
    if len(tasks) == 1 and len(sentences) > 2:
        mid = max(1, len(sentences) // 2)
        tasks = [
            " ".join(sentences[:mid]).strip(),
            " ".join(sentences[mid:]).strip(),
        ]
        tasks = [t for t in tasks if t]

    # Step 5: Build DAG nodes
    nodes = []
    for i, task_text in enumerate(tasks):
        node_id = f"n{i+1}"
        nodes.append({
            "id": node_id,
            "task": task_text,
            "model": "qwen",
            "route": "Hybrid",
            "depends_on": [f"n{i}"] if i > 0 else [],
        })

    return {"nodes": nodes, "language": lang}


# ── Load model (zero-shot or fine-tuned) ────────────────────────────────────
# Helper to get config from Streamlit Secrets or Environment
def get_config(key, default=None):
    try:
        import streamlit as st
        if key in st.secrets:
            return st.secrets[key]
    except (ImportError, Exception):
        pass
    return os.getenv(key, default)

# Set CLASSIFIER_MODEL_PATH in .env after running training/train_classifier.py
_CUSTOM_PATH = get_config("CLASSIFIER_MODEL_PATH", "").strip()
_MODEL_ID    = _CUSTOM_PATH if _CUSTOM_PATH and os.path.isdir(_CUSTOM_PATH) \
               else "typeform/distilbert-base-uncased-mnli"

if _CUSTOM_PATH and not os.path.isdir(_CUSTOM_PATH):
    print(f"[classifier] WARNING: CLASSIFIER_MODEL_PATH='{_CUSTOM_PATH}' not found, using default.",
          file=sys.stderr)

_classifier = None

def get_classifier():
    global _classifier
    if _classifier is None:
        print(f"Loading classifier: {_MODEL_ID}", file=sys.stderr)
        _classifier = pipeline(
            "zero-shot-classification",
            model=_MODEL_ID
        )
        print("Classifier loaded successfully!", file=sys.stderr)
    return _classifier


# ── Define your intent labels ────────────────────────────────────────────────
INTENT_LABELS = [
    "summarize", "translate", "analyze_data", "generate_code",
    "multi_step", "ambiguous", "urgent", "simple_query"
]

def classify_prompt(prompt: str) -> dict:
    """
    Takes a raw text prompt.
    Returns a dictionary with:
      - prompt        : the original text
      - top_intent    : the top detected label
      - top_confidence: how sure the model is (0.0 to 1.0)
      - intent_matrix : normalized probabilities for all labels
      - is_multi_step : boolean if multi_step confidence is high
      - is_ambiguous  : boolean if ambiguous confidence is high
      - latency_ms    : how long classification took in milliseconds
      - intent        : (backwards compatibility) same as top_intent
      - confidence    : (backwards compatibility) same as top_confidence
      - all_scores    : (backwards compatibility) same as intent_matrix
    """

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    # Start the timer — we measure how long classification takes
    start_time = time.time()

    # ── The actual classification ────────────────────────────────────────────
    # The model reads the prompt and scores it against each label.
    clf = get_classifier()
    result = clf(prompt.strip(), INTENT_LABELS)
    
    intent_probs = {label: score for label, score in zip(result["labels"], result["scores"])}

    # Add domain-specific logic (e.g., detect multi-step tasks)
    text_lower = prompt.lower()
    if " and " in text_lower or " then " in text_lower:
        intent_probs["multi_step"] *= 1.5  # Boost multi-step confidence
        
    if "urgent" in text_lower or "asap" in text_lower:
        intent_probs["urgent"] *= 1.5

    # Normalize probabilities
    total = sum(intent_probs.values())
    intent_probs = {k: round(v/total, 4) for k, v in intent_probs.items()}

    # Stop the timer
    latency_ms = round((time.time() - start_time) * 1000, 2)
    
    # Get top intent after post-processing
    top_intent, top_confidence = max(intent_probs.items(), key=lambda x: x[1])

    # ── Package everything into a clean dictionary ───────────────────────────
    return {
        "prompt":         prompt.strip(),
        "top_intent":     top_intent,
        "top_confidence": top_confidence,
        "intent_matrix":  intent_probs,
        "is_multi_step":  intent_probs.get("multi_step", 0) > 0.3,
        "is_ambiguous":   intent_probs.get("ambiguous", 0) > 0.2,
        "latency_ms":     latency_ms,
        
        # Backwards compatibility for existing code (like mcp_server.py)
        "intent":         top_intent,
        "confidence":     top_confidence,
        "all_scores":     intent_probs
    }


# ── Quick self-test (run this file directly to verify it works) ──────────────
if __name__ == "__main__":
    test_prompts = [
        "What is the difference between edge AI and cloud AI?",
        "Translate this paragraph to Kannada",
        "Analyze the sensor data and generate a weekly report",
        "Summarize this PDF and then email it to my team ASAP",
        "Write a poem about distributed computing"
    ]

    print("\n=== CLASSIFIER SELF-TEST ===\n")
    for p in test_prompts:
        out = classify_prompt(p)
        print(f"Prompt        : {out['prompt']}")
        print(f"Top Intent    : {out['top_intent']}")
        print(f"Confidence    : {out['top_confidence'] * 100:.1f}%")
        print(f"Is Multi-Step?: {out['is_multi_step']}")
        print(f"Is Urgent?    : {out['intent_matrix'].get('urgent', 0) > 0.3}")
        print(f"Latency       : {out['latency_ms']} ms")
        print("-" * 50)
