import hashlib
from pathlib import Path
import re

class FileUtils:
    @staticmethod
    def get_file_hash(filepath: Path) -> str:
        """Calculate SHA-256 hash of a file."""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for consistent naming."""
        base = Path(filename).stem
        sanitized = re.sub(r'[^a-zA-Z0-9]+', '_', base.lower()).strip('_')
        return f"{sanitized}.wav"

    @staticmethod
    def ensure_directory(directory: Path) -> Path:
        """Ensure directory exists and return Path object."""
        directory.mkdir(parents=True, exist_ok=True)
        return directory