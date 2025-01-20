from pathlib import Path
from typing import Iterator, Optional, Tuple
from audio.downloader import AudioDownloader
from audio.converter import AudioConverter
from transcription.transcriber import Transcriber

class MediaProcessor:
    def __init__(self, 
                 model_name: str = 'tiny.en',
                 output_dir: str = './downloads',
                 raw_dir: str = './raw_downloads',
                 transcripts_dir: str = './transcripts'):
        self.downloader = AudioDownloader(raw_dir)
        self.converter = AudioConverter(output_dir)
        self.transcriber = Transcriber(model_name, transcripts_dir)

    def process_url(self, url: str, skip_transcription: bool = False) -> Tuple[Optional[str], Optional[Path]]:
        """Process a single URL: download, convert, and optionally transcribe."""
        downloaded_file = self.downloader.download_single(url)
        if not downloaded_file:
            return None, None

        wav_file = self.converter.convert_to_wav(downloaded_file)
        if not wav_file:
            return None, None

        # Clean up downloaded file
        downloaded_file.unlink(missing_ok=True)

        if skip_transcription:
            return None, wav_file

        # Transcribe
        return self.transcriber.transcribe(wav_file)

    def process_playlist(self, url: str, skip_transcription: bool = False) -> Iterator[Tuple[Optional[str], Optional[Path]]]:
        """Process all videos in a YouTube playlist."""
        for audio_file in self.downloader.download_playlist(url):
            wav_file = self.converter.convert_to_wav(audio_file)
            if not wav_file:
                continue

            # Clean up downloaded file
            audio_file.unlink(missing_ok=True)

            if skip_transcription:
                yield None, wav_file
            else:
                yield self.transcriber.transcribe(wav_file)