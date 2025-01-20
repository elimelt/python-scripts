from pathlib import Path
import subprocess
from typing import Optional
from utils.file_utils import FileUtils

class AudioConverter:
    def __init__(self, output_dir: str = './downloads'):
        self.output_dir = Path(output_dir)
        FileUtils.ensure_directory(self.output_dir)

    def convert_to_wav(self, input_path: Path) -> Optional[Path]:
        """Convert audio file to WAV format using ffmpeg."""
        new_filename = FileUtils.sanitize_filename(input_path.name)
        output_path = self.output_dir / new_filename

        try:
            subprocess.run([
                'ffmpeg',
                '-i', str(input_path),
                '-ar', '16000',  # 16kHz sample rate
                '-ac', '1',      # mono
                '-acodec', 'pcm_s16le',  # 16-bit PCM
                str(output_path)
            ], check=True, capture_output=True)
            
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"Error converting {input_path}: {e.stderr.decode()}")
            return None