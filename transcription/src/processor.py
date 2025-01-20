import logging
from pathlib import Path
from typing import Iterator, Optional, Tuple
from audio.downloader import AudioDownloader
from audio.converter import AudioConverter
from transcription.transcriber import Transcriber

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MediaProcessor:
    def __init__(self, 
                 model_name: str = 'tiny.en',
                 output_dir: str = './downloads',
                 raw_dir: str = './raw_downloads',
                 transcripts_dir: str = './transcripts'):
        self.downloader = AudioDownloader(raw_dir)
        self.converter = AudioConverter(output_dir)
        self.transcriber = Transcriber(model_name, transcripts_dir)
        logger.info("MediaProcessor initialized with model: %s", model_name)

    def transcribe_wav(self, wav_file: Path) -> Optional[str]:
        """Transcribe a single WAV file."""
        return self.transcriber.transcribe(wav_file)

    def transcribe_files(self, files: Iterator[Path], convert: bool) -> Iterator[Tuple[Optional[str], Optional[Path]]]:
        """Transcribe multiple WAV files in parallel."""
        for wav_file in files:
            if convert:
                wav_file = self.converter.convert_to_wav(wav_file)
                if not wav_file:
                    logger.error("Failed to convert file to WAV: %s", wav_file)
                    continue

            yield self.transcribe_wav(wav_file)

    def process_url(self, url: str, skip_transcription: bool = False) -> Tuple[Optional[str], Optional[Path]]:
        """Process a single URL: download, convert, and optionally transcribe."""
        logger.info("Processing URL: %s", url)
        downloaded_file = self.downloader.download_single(url)
        if not downloaded_file:
            logger.error("Failed to download file from URL: %s", url)
            return None, None

        wav_file = self.converter.convert_to_wav(downloaded_file)
        if not wav_file:
            logger.error("Failed to convert file to WAV: %s", downloaded_file)
            return None, None

        # Clean up downloaded file
        downloaded_file.unlink(missing_ok=True)
        logger.info("Downloaded file cleaned up: %s", downloaded_file)

        if skip_transcription:
            logger.info("Skipping transcription for URL: %s", url)
            return None, wav_file

        # Transcribe
        transcription = self.transcriber.transcribe(wav_file)
        logger.info("Transcription completed for URL: %s", url)
        return transcription

    def process_playlist(self, url: str, skip_transcription: bool = False) -> Iterator[Tuple[Optional[str], Optional[Path]]]:
        """Process all videos in a YouTube playlist."""
        logger.info("Processing playlist URL: %s", url)
        for audio_file in self.downloader.download_playlist(url):
            wav_file = self.converter.convert_to_wav(audio_file)
            if not wav_file:
                logger.error("Failed to convert file to WAV: %s", audio_file)
                continue

            # Clean up downloaded file
            audio_file.unlink(missing_ok=True)
            logger.info("Downloaded file cleaned up: %s", audio_file)

            if skip_transcription:
                logger.info("Skipping transcription for file: %s", wav_file)
                yield None, wav_file
            else:
                transcription = self.transcriber.transcribe(wav_file)
                logger.info("Transcription completed for file: %s", wav_file)
                yield transcription