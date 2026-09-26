from .voice_processor import VoiceProcessor
from .text_processor import TextProcessor

class InputRouter:
    def __init__(self):
        self.voice_processor = VoiceProcessor()
        self.text_processor = TextProcessor()

    def route(self, input_data, input_type="text"):
        if input_type == "voice":
            return self.voice_processor.transcribe(input_data)
        elif input_type == "text":
            return self.text_processor.process(input_data)
        else:
            raise ValueError(f"Unsupported input type: {input_type}")