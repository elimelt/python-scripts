from pathlib import Path
from typing import Tuple, Optional
import whisper
from utils.text_utils import TextFormatter
from utils.file_utils import FileUtils

class Transcriber:
    def __init__(self, model_name: str = 'tiny.en', transcripts_dir: str = './transcripts'):
        self.model = whisper.load_model(model_name)
        self.transcripts_dir = Path(transcripts_dir)
        FileUtils.ensure_directory(self.transcripts_dir)

    def transcribe(self, audio_path: Path) -> Tuple[Optional[str], Optional[Path]]:
        """Transcribe audio file and save to transcripts directory."""
        try:
            result = self.model.transcribe(str(audio_path))
            formatted_text = TextFormatter.format_transcript(result['text'])
            
            transcript_path = self.transcripts_dir / f"{audio_path.stem}_transcript.txt"
            transcript_path.write_text(formatted_text, encoding='utf-8')
            
            return formatted_text, transcript_path
        except Exception as e:
            print(f"Error transcribing {audio_path}: {e}")
            raise e
            # return None, None