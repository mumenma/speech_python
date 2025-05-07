import os
import tempfile
from contextlib import contextmanager
from typing import Generator, Optional

class TempFileHandler:
    def __init__(self, cache_dir: str = None):
        self.temp_files = []
        self.cache_dir = cache_dir or os.path.join(tempfile.gettempdir(), 'temp_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    @contextmanager
    def create_temp_file(self, suffix: str) -> Generator[str, None, None]:
        """Create a temporary file with the given suffix in the cache directory."""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir=self.cache_dir)
        self.temp_files.append(temp_file.name)
        try:
            yield temp_file.name
        finally:
            temp_file.close()

    def cleanup(self) -> None:
        """Clean up all temporary files."""
        for file_path in self.temp_files[:]:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                    self.temp_files.remove(file_path)
            except Exception:
                pass

    def delete_file(self, file_path: str) -> None:
        """Delete a specific temporary file and remove it from the list."""
        if file_path in self.temp_files:
            try:
                if os.path.exists(file_path):
                    os.unlink(file_path)
                self.temp_files.remove(file_path)
            except Exception:
                pass

    def __del__(self):
        """Destructor to ensure cleanup when the object is destroyed."""
        self.cleanup()