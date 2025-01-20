from pathlib import Path
from typing import Iterator, Optional
from pytubefix import YouTube, Playlist
from utils.file_utils import FileUtils

class AudioDownloader:
    def __init__(self, output_dir: str = './raw_downloads'):
        self.output_dir = Path(output_dir)
        FileUtils.ensure_directory(self.output_dir)

    def download_single(self, url: str) -> Optional[Path]:
        """Download audio from a single YouTube URL."""
        try:
            yt = YouTube(url, use_oauth=True, allow_oauth_cache=True)
            audio_stream = yt.streams.filter(only_audio=True).first()
            if audio_stream:
                return Path(audio_stream.download(output_path=str(self.output_dir)))
        except Exception as e:
            print(f"Error downloading {url}: {e}")
        return None

    def download_playlist(self, url: str) -> Iterator[Path]:
        """Download audio from all videos in a YouTube playlist."""
        try:
            playlist = Playlist(url)
            for video in playlist.videos:
                # Getting detected as a bot with the below, try individual video downloads instead
                # audio_stream = video.streams.filter(only_audio=True).first()
                # if audio_stream:
                #     yield Path(audio_stream.download(output_path=str(self.output_dir)))

                url = video.watch_url
                print(f"Downloading: {url}")
                yield self.download_single(url)
        except Exception as e:
            print(f"Error processing playlist {url}: {e}")