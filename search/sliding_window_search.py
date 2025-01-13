#!/usr/bin/env python3

import argparse
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass
import os
import re
from pathlib import Path
from typing import List, Tuple, Dict, Iterator, Optional, Set
from collections import defaultdict


@dataclass
class Token:

    text: str
    start: int
    end: int
    normalized: str

    @classmethod
    def from_text(cls, text: str, start: int, end: int) -> "Token":
        return cls(text, start, end, text.lower())


@dataclass
class SearchMatch:

    window_size: int
    start_pos: int
    end_pos: int
    text: str
    score: float = 0.0
    file_path: Optional[str] = None


class TextTokenizer:

    def __init__(self):
        self.token_cache: Dict[str, List[Token]] = {}

    def tokenize(self, text: str) -> List[Token]:

        if text in self.token_cache:
            return self.token_cache[text]

        tokens = []
        current_token = []
        token_start = None

        for i, char in enumerate(text):
            if char.isspace() or char in ".,;:!?\"'()[]{}":
                if current_token:
                    token_text = "".join(current_token)
                    tokens.append(Token.from_text(token_text, token_start, i))
                    current_token = []
                    token_start = None
            else:
                if token_start is None:
                    token_start = i
                current_token.append(char)

        if current_token:
            token_text = "".join(current_token)
            tokens.append(Token.from_text(token_text, token_start, len(text)))

        self.token_cache[text] = tokens
        return tokens


class SearchStrategy(ABC):

    @abstractmethod
    def search(
        self, text: str, query_terms: List[str], window_size: int
    ) -> Iterator[SearchMatch]:

        pass


class FileFinder:

    DEFAULT_IGNORE_DIRS = {
        "__pycache__",
        "node_modules",
        ".git",
        ".svn",
        ".hg",
        ".idea",
        ".vscode",
        ".tox",
        "venv",
        ".env",
        "venv",
        "bin",
        "env",
        "dist",
        "build",
        "target",
        "vendor",
    }

    DEFAULT_IGNORE_EXTENSIONS = {
        ".pyc",
        ".pyo",
        ".pyd",
        ".class",
        ".jar",
        ".o",
        ".so",
        ".dll",
        ".exe",
        ".bin",
        ".zip",
        ".tar",
        ".gz",
        ".DS_Store",
        ".bz2",
        ".7z",
        ".rar",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".ico",
        ".mp3",
        ".mp4",
        ".avi",
        ".mov",
        ".wmv",
        ".pdf",
        ".doc",
        ".docx",
        ".xls",
        ".xlsx",
        ".ppt",
        ".pptx",
        ".db",
        ".sqlite",
        ".sqlite3",
        ".mdb",
        ".bin",
        ".dat",
        ".pkl",
        ".pickle",
        ".cache",
        ".log",
    }

    def __init__(
        self,
        file_pattern: Optional[str] = None,
        ignore_dirs: Optional[Set[str]] = None,
        ignore_extensions: Optional[Set[str]] = None,
        no_ignore: bool = False,
    ):
        self.pattern = re.compile(file_pattern) if file_pattern else None

        self.ignore_dirs = (
            set()
            if no_ignore
            else (ignore_dirs if ignore_dirs is not None else self.DEFAULT_IGNORE_DIRS)
        )
        self.ignore_extensions = (
            set()
            if no_ignore
            else (
                ignore_extensions
                if ignore_extensions is not None
                else self.DEFAULT_IGNORE_EXTENSIONS
            )
        )

    def should_process_file(self, file_path: str) -> bool:

        basename = os.path.basename(file_path)
        _, ext = os.path.splitext(basename)
        ext = ext.lower()

        if ext in self.ignore_extensions:
            return False

        if self.pattern and not self.pattern.search(basename):
            return False

        return True

    def should_process_dir(self, dir_path: str) -> bool:

        dir_name = os.path.basename(dir_path)
        return dir_name not in self.ignore_dirs

    def find_files(self, path: str) -> Iterator[str]:
        path_obj = Path(path)

        if path_obj.is_file():
            if self.should_process_file(str(path_obj)):
                yield str(path_obj)
            return

        for root, dirs, files in os.walk(path_obj):

            dirs[:] = [
                d for d in dirs if self.should_process_dir(os.path.join(root, d))
            ]

            for file in files:
                file_path = os.path.join(root, file)
                if self.should_process_file(file_path):
                    yield file_path


class SlidingWindowSearch(SearchStrategy):

    def __init__(self):
        self.tokenizer = TextTokenizer()

        self.term_positions: Dict[str, Dict[str, List[int]]] = {}

    def _build_term_index(
        self, tokens: List[Token], query_terms: List[str]
    ) -> Dict[str, List[int]]:

        term_positions = defaultdict(list)
        for i, token in enumerate(tokens):
            if token.normalized in query_terms:
                term_positions[token.normalized].append(i)
        return term_positions

    def search(
        self, text: str, query_terms: List[str], window_size: int
    ) -> Iterator[SearchMatch]:
        normalized_terms = [term.lower() for term in query_terms]
        tokens = self.tokenizer.tokenize(text)

        if len(tokens) < window_size:
            return

        if text not in self.term_positions:
            self.term_positions[text] = self._build_term_index(tokens, normalized_terms)
        term_positions = self.term_positions[text]

        if not all(term in term_positions for term in normalized_terms):
            return

        first_positions = [
            pos[0] for positions in term_positions.values() for pos in [positions]
        ]
        i = min(first_positions)

        while i <= len(tokens) - window_size:
            window = tokens[i : i + window_size]

            if all(
                any(term == token.normalized for token in window)
                for term in normalized_terms
            ):

                start_pos = window[0].start
                end_pos = window[-1].end
                window_text = text[start_pos:end_pos]

                score = 1.0 / window_size

                yield SearchMatch(
                    window_size, start_pos, end_pos, window_text, score, None
                )

                last_occurrence = 0
                for term in normalized_terms:
                    for j in range(len(window) - 1, -1, -1):
                        if window[j].normalized == term:
                            last_occurrence = max(last_occurrence, j)
                            break

                i += last_occurrence + 1
            else:

                next_pos = float("inf")
                current_pos = i + window_size - 1
                for term in normalized_terms:
                    positions = term_positions[term]
                    for pos in positions:
                        if pos > current_pos:
                            next_pos = min(next_pos, pos - window_size + 1)
                            break

                if next_pos == float("inf"):
                    break

                i = next_pos


class TextHighlighter:

    def __init__(self, use_color: bool = True):
        self.use_color = use_color

    def highlight_match(self, match: SearchMatch, query_terms: List[str]) -> str:

        if not self.use_color:
            return match.text

        highlighted = match.text

        sorted_terms = sorted(query_terms, key=len, reverse=True)

        positions = []
        for term in sorted_terms:
            term_lower = term.lower()
            start = 0
            while True:
                start = highlighted.lower().find(term_lower, start)
                if start == -1:
                    break
                positions.append((start, start + len(term), term))
                start += 1

        for start, end, term in sorted(positions, reverse=True):
            original_term = highlighted[start:end]
            highlighted = (
                highlighted[:start]
                + f"\033[1;33m{original_term}\033[0m"
                + highlighted[end:]
            )

        return highlighted

    def format_match(
        self, match: SearchMatch, query_terms: List[str], show_position: bool = True
    ) -> str:

        highlighted_text = self.highlight_match(match, query_terms)

        header = f"\n{'=' * 80}\n"
        file_info = f"File: {match.file_path}\n" if match.file_path else ""
        if show_position:
            header += (
                f"{file_info}"
                f"Window Size: {match.window_size} tokens | "
                f"Position: characters {match.start_pos}-{match.end_pos} | "
                f"Score: {match.score:.3f}\n"
            )
        else:
            header += f"{file_info}Window Size: {match.window_size} tokens\n"
        header += f"{'-' * 80}\n"

        return f"{header}{highlighted_text}\n"


class WindowSearchCLI:

    def __init__(self):
        self.search_strategy = SlidingWindowSearch()
        self.highlighter = TextHighlighter()
        self.file_finder = None

    def parse_args(self):

        parser = argparse.ArgumentParser(
            description="Search text using a sliding window approach to find sections containing all query terms.",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:

  %(prog)s -f document.txt -q "python" "machine learning" -w 50


  %(prog)s -f document.txt -q "python" "data" --min-window 20 --max-window 100
  

  cat document.txt | %(prog)s -q "python" "data"
""",
        )

        parser.add_argument(
            "-f",
            "--file",
            help="Input file or directory (if not specified, reads from stdin)",
        )
        parser.add_argument(
            "-E", "--file-pattern", help="Regular expression pattern to filter files"
        )
        parser.add_argument(
            "--no-ignore",
            action="store_true",
            help="Disable default ignore patterns for files and directories",
        )
        parser.add_argument(
            "--ignore-dir",
            action="append",
            default=[],
            help="Additional directory names to ignore (can be specified multiple times)",
        )
        parser.add_argument(
            "--ignore-ext",
            action="append",
            default=[],
            help="Additional file extensions to ignore (can be specified multiple times)",
        )
        parser.add_argument(
            "-q", "--query", nargs="+", required=True, help="Query terms to search for"
        )
        parser.add_argument(
            "-w",
            "--window",
            type=int,
            default=50,
            help="Window size in tokens (default: 50)",
        )
        parser.add_argument(
            "--min-window",
            type=int,
            help="Minimum window size to try (enables variable window search)",
        )
        parser.add_argument(
            "--max-results",
            type=int,
            default=5,
            help="Maximum number of results to show (default: 5)",
        )
        parser.add_argument(
            "--no-color", action="store_true", help="Disable colored output"
        )

        return parser.parse_args()

    def read_input(self, args) -> Iterator[Tuple[str, str]]:
        if not args.file:

            yield None, sys.stdin.read()
            return

        ignore_dirs = set(FileFinder.DEFAULT_IGNORE_DIRS)
        ignore_dirs.update(args.ignore_dir)

        ignore_extensions = set(FileFinder.DEFAULT_IGNORE_EXTENSIONS)
        ignore_extensions.update("." + ext.lstrip(".") for ext in args.ignore_ext)

        self.file_finder = FileFinder(
            args.file_pattern,
            ignore_dirs=ignore_dirs if not args.no_ignore else set(),
            ignore_extensions=ignore_extensions if not args.no_ignore else set(),
            no_ignore=args.no_ignore,
        )

        for file_path in self.file_finder.find_files(args.file):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    yield file_path, content
            except (IOError, UnicodeDecodeError) as e:
                print(f"Error reading file {file_path}: {e}", file=sys.stderr)
                continue

    def search_text(
        self,
        file_path: Optional[str],
        text: str,
        query_terms: List[str],
        window_size: int,
        min_window: Optional[int] = None,
        max_results: int = 5,
    ) -> List[SearchMatch]:

        matches = []

        if min_window is not None:
            window_sizes = range(min_window, window_size + 1, 10)
        else:
            window_sizes = [window_size]

        for size in window_sizes:
            for match in self.search_strategy.search(text, query_terms, size):
                match.file_path = file_path
                matches.append(match)

        matches.sort(key=lambda x: (-x.score, x.start_pos))
        return matches[:max_results]

    def run(self):

        args = self.parse_args()

        self.highlighter.use_color = not args.no_color

        all_matches = []
        files_searched = 0
        files_with_matches = 0

        for file_path, content in self.read_input(args):
            files_searched += 1

            matches = self.search_text(
                file_path,
                content,
                args.query,
                args.window,
                args.min_window,
                args.max_results,
            )

            if matches:
                files_with_matches += 1
                all_matches.extend(matches)

        all_matches.sort(key=lambda x: (-x.score, x.file_path or "", x.start_pos))
        all_matches = all_matches[: args.max_results]

        if not all_matches:
            print(f"\nNo matches found in {files_searched} files searched.")
            return

        print(
            f"\nFound {len(all_matches)} matches in {files_with_matches} of {files_searched} files "
            f"for terms: {', '.join(args.query)}"
        )
        for match in all_matches:
            print(self.highlighter.format_match(match, args.query))


def main():
    cli = WindowSearchCLI()
    cli.run()


if __name__ == "__main__":
    main()
