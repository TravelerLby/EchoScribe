import sys
from pathlib import Path
from faster_whisper import WhisperModel


class Transcriber:
    """
    Core class that encapsulates Whisper model loading and audio transcription functionality.
    """

    def __init__(self):
        """Initialize transcriber and load the Whisper model."""
        self.model = self._load_model()

    def _get_application_path(self):
        """Get the root directory path of the application."""
        if getattr(sys, 'frozen', False):
            return Path(sys.executable).parent
        else:
            return Path(__file__).resolve().parent.parent.parent

    def _load_model(self):
        """Load the local Whisper model from the Models directory."""
        app_root = self._get_application_path()

        model_path = app_root / "Models" / "faster_whisper_base_en"
        print(f"Loading model from local path: {model_path}")

        if not model_path.exists():
            print(f"[CRITICAL ERROR] Model folder does not exist at: {model_path}")
            return None

        try:
            # Load model with CPU and int8 for better compatibility
            loaded_model = WhisperModel(str(model_path), device="cpu", compute_type="int8")
            print("[SUCCESS] Model loaded successfully!")
            return loaded_model
        except Exception as e:
            print(f"[CRITICAL ERROR] Unknown error occurred while loading model: {e}")
            return None

    def transcribe_audio(self, audio_file_path):
        """Transcribe audio file to text.
        
        Args:
            audio_file_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text as string, or error message
        """
        if not self.model:
            print("Model not loaded, cannot perform transcription.")
            return "Error: Model failed to load successfully."

        try:
            # Transcribe with beam search for better accuracy
            segments, info = self.model.transcribe(audio_file_path, beam_size=5)
            print(f"Detected language '{info.language}' with probability {info.language_probability}")

            # Collect all transcribed text segments
            result_text_list = []
            for segment in segments:
                result_text_list.append(segment.text.strip())

            return "\n".join(result_text_list)
        except Exception as e:
            print(f"Error occurred while transcribing audio file: {e}")
            return f"Error: Transcription failed - {e}"