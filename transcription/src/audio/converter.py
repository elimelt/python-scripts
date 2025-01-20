from pathlib import Path
import subprocess
from typing import Optional, List
import logging
from concurrent.futures import ThreadPoolExecutor
from utils.file_utils import FileUtils

class AudioConverter:
    def __init__(self, output_dir: str = "./downloads", max_workers: int = 4):
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        FileUtils.ensure_directory(self.output_dir)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        # Pre-construct the ffmpeg command template
        self.ffmpeg_cmd_template = [
            "ffmpeg",
            "-y",  # Overwrite output files without asking
            "-loglevel", "error",  # Reduce ffmpeg output
            "-i", None,  # Input placeholder
            "-ar", "16000",
            "-ac", "1",
            "-acodec", "pcm_s16le",
            None  # Output placeholder
        ]

    def convert_to_wav(self, input_path: Path) -> Optional[Path]:
        """Convert single audio file to WAV format using ffmpeg."""
        new_filename = FileUtils.sanitize_filename(input_path.name)
        output_path = self.output_dir / new_filename

        # Create command for this specific file
        cmd = self.ffmpeg_cmd_template.copy()
        cmd[5] = str(input_path)  # Set input path
        cmd[-1] = str(output_path)  # Set output path

        try:
            # Use subprocess.Popen for better performance
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            _, stderr = process.communicate()

            if process.returncode == 0:
                self.logger.info(f"Successfully converted {input_path}")
                return output_path
            else:
                self.logger.error(f"Error converting {input_path}: {stderr.decode()}")
                return None

        except Exception as e:
            self.logger.error(f"Exception converting {input_path}: {str(e)}")
            return None

    def convert_batch(self, input_paths: List[Path]) -> List[Optional[Path]]:
        """Convert multiple audio files in parallel."""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            return list(executor.map(self.convert_to_wav, input_paths))