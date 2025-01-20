import logging
from pathlib import Path
from typing import Iterator, Optional
from pytubefix import YouTube, Playlist
from pytubefix.cli import on_progress
from utils.file_utils import FileUtils

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class AudioDownloader:
    def __init__(self, output_dir: str = "./raw_downloads"):
        self.output_dir = Path(output_dir)
        FileUtils.ensure_directory(self.output_dir)
        logging.info(f"Output directory set to: {self.output_dir}")

    def download_single(self, url: str) -> Optional[Path]:
        """Download audio from a single YouTube URL."""
        try:
            logging.info(f"Starting download for: {url}")
            yt = YouTube(
                url,
                use_oauth=True,
                allow_oauth_cache=True,
                on_progress_callback=on_progress,
            )
            audio_stream = yt.streams.filter(only_audio=True).first()
            if audio_stream:
                downloaded_path = Path(
                    audio_stream.download(output_path=str(self.output_dir))
                )
                logging.info(f"Downloaded to: {downloaded_path}")
                return downloaded_path
        except Exception as e:
            logging.error(f"Error downloading {url}: {e}")
        return None

    def download_playlist(self, url: str) -> Iterator[Path]:
        """Download audio from all videos in a YouTube playlist."""
        try:
            logging.info(f"Starting playlist download for: {url}")
            playlist = Playlist(url)
            for video in playlist.videos:
                video_url = video.watch_url
                logging.info(f"Downloading: {video_url}")
                yield self.download_single(video_url)
        except Exception as e:
            logging.error(f"Error processing playlist {url}: {e}")
