from models.liquid_neural_networks.lnn_intent_classifier import LiquidIntentClassifier
from memory.short_term_memory import ShortTermMemory
from multi_modal.input_router import InputRouter

class LiquidEngine:
    def __init__(self):
        self.classifier = LiquidIntentClassifier()
        self.memory = ShortTermMemory()
        self.input_router = InputRouter()
        self.classifier.load()

    def process_input(self, input_data, input_type="text"):
        # Route input (voice/text) to text
        prompt = self.input_router.route(input_data, input_type)

        # Classify the prompt
        intent = self.classifier.classify(prompt)

        # Store in memory
        self.memory.store(prompt, intent)

        # Update the classifier
        self.classifier.update(prompt, intent)

        return {
            "prompt": prompt,
            "intent": intent,
            "input_type": input_type
        }

    def train_from_memory(self, limit=100):
        interactions = self.memory.get_recent(limit)
        if interactions:
            prompts, intents = zip(*interactions)
            self.classifier.train(prompts, intents)