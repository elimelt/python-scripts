import sys
import argparse
from pathlib import Path
from typing import List
from processor import MediaProcessor

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Download, convert, and transcribe audio files')
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--urls', nargs='+', help='YouTube URLs to process')
    input_group.add_argument('--batch', action='store_true', help='Read URLs from stdin (one URL per line)')
    input_group.add_argument('--playlist', metavar='URL', help='Process all videos in a YouTube playlist')
    input_group.add_argument('--files', nargs='+', type=Path, help='Local audio files to transcribe')

    parser.add_argument('--model', default='tiny.en',
                      choices=['tiny.en', 'base.en', 'small.en', 'medium.en', 'large', 'turbo'],
                      help='Whisper model to use for transcription')
    parser.add_argument('--skip-transcription', action='store_true',
                      help='Skip transcription and only download/convert audio')
    parser.add_argument('--convert', action='store_true',
                      help='Convert input files to WAV before transcription')
    parser.add_argument('--output-dir', default='./downloads',
                      help='Directory for processed WAV files')
    parser.add_argument('--raw-dir', default='./raw_downloads',
                      help='Directory for raw downloaded files')
    parser.add_argument('--transcripts-dir', default='./transcripts',
                      help='Directory for transcript files')
    
    return parser

def process_local_files(processor: MediaProcessor, files: List[Path], convert: bool) -> None:
    """Process local audio files."""
    print('convert', convert)
    for transcription, file_path in processor.transcribe_files(files, convert):
        if file_path:
            print(f"\nProcessed: {file_path}")
            if transcription:
                preview = transcription[:500] + "..." if len(transcription) > 500 else transcription
                print("\nTranscription preview:")
                print(preview)
        else:
            print(f"Failed to process file", file=sys.stderr)

def process_batch(processor: MediaProcessor, skip_transcription: bool) -> None:
    """Process URLs from stdin."""
    for line in sys.stdin:
        url = line.strip()
        if url:
            try:
                print(f"\nProcessing: {url}")
                transcription, output_path = processor.process_url(url, skip_transcription)
                if transcription:
                    print(f"Transcription saved to: {output_path}")
            except Exception as e:
                print(f"Error processing {url}: {e}", file=sys.stderr)

def process_playlist(processor: MediaProcessor, playlist_url: str, skip_transcription: bool) -> None:
    """Process a YouTube playlist."""
    try:
        for transcript, path in processor.process_playlist(playlist_url, skip_transcription):
            if transcript:
                preview = transcript if len(transcript) < 100 else  transcript[:100] + "..."
                print(f"\nTranscription preview: {preview}")
            print(f"audio saved to: {path}")

    except Exception as e:
        print(f"Error processing playlist {playlist_url}: {e}")

def process_urls(processor: MediaProcessor, urls: List[str], skip_transcription: bool) -> None:
    """Process a list of URLs."""
    for url in urls:
        try:
            print(f"\nProcessing: {url}")
            transcription, output_path = processor.process_url(url, skip_transcription)
            if transcription:
                preview = transcription[:500] + "..." if len(transcription) > 500 else transcription
                print("\nTranscription preview:")
                print(preview)
        except Exception as e:
            print(f"Error processing {url}: {e}")

def main() -> None:
    parser = create_parser()
    args = parser.parse_args()

    processor = MediaProcessor(
        model_name=args.model,
        output_dir=args.output_dir,
        raw_dir=args.raw_dir,
        transcripts_dir=args.transcripts_dir
    )

    if args.files:
        process_local_files(processor, args.files, args.convert)
    elif args.batch:
        if sys.stdin.isatty():
            parser.error("No input provided for batch processing. Use pipe or redirect.")
        process_batch(processor, args.skip_transcription)
    elif args.playlist:
        process_playlist(processor, args.playlist, args.skip_transcription)
    else:
        process_urls(processor, args.urls, args.skip_transcription)

if __name__ == '__main__':
    main()