"""Placeholder for voice processing in the multimodal pipeline."""
import whisper
import os
from tempfile import NamedTemporaryFile

class VoiceProcessor:
    def __init__(self, model_name="base"):
        self.model = whisper.load_model(model_name)

    def transcribe(self, audio_file):
        # Save uploaded file to a temp file (for Whisper)
        with NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            temp_audio.write(audio_file.read())
            temp_audio_path = temp_audio.name

        # Transcribe
        result = self.model.transcribe(temp_audio_path)
        text = result["text"]

        # Clean up
        os.unlink(temp_audio_path)

        return text