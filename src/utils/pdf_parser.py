from pathlib import Path
from typing import List
from llama_parse import LlamaParse
from langchain.schema.document import Document
from src.config import LLAMA_CLOUD_API_KEY, CACHE_DIR
import hashlib


class PDFParser:
    """A class to parse PDF documents using the LlamaParse API."""

    def __init__(self, api_key: str = LLAMA_CLOUD_API_KEY, cache_dir: str = CACHE_DIR):
        """
        Initializes the PDFParser.

        Args:
            api_key (str): The API key for the Llama Cloud service.
        """
        if not api_key:
            raise ValueError("Llama Cloud API key is required for parsing PDFs.")
        self.parser = LlamaParse(api_key=api_key, result_type="markdown", verbose=True)
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

    def _get_file_hash(self, file_path: Path) -> str:
        """
        Generate a hash for the file based on its content and modification time.

        Args:
            file_path (Path): The path to the PDF file.

        Returns:
            str: A unique hash for the file.
        """
        stat = file_path.stat()
        file_info = f"{file_path.name}_{stat.st_size}_{stat.st_mtime}"

        return hashlib.md5(file_info.encode()).hexdigest()

    def _get_cache_path(self, file_path: Path) -> Path:
        """
        Get the cache file path for a given PDF file.

        Args:
            file_path (Path): The path to the PDF file.

        Returns:
            Path: The path to the cached markdown file.
        """
        file_hash = self._get_file_hash(file_path)
        cache_filename = f"{file_path.stem}_{file_hash}.md"
        return self.cache_dir / cache_filename

    def _load_from_cache(self, cache_path: Path) -> str:
        """
        Load content from cache file.

        Args:
            cache_path (Path): The path to the cached file.

        Returns:
            str: The cached content, or empty string if loading fails.
        """
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"Error reading cache file {cache_path}: {e}")
            return ""

    def _save_to_cache(self, cache_path: Path, content: str) -> None:
        """
        Save content to cache file.

        Args:
            cache_path (Path): The path to save the cache file.
            content (str): The content to cache.
        """
        try:
            with open(cache_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Cached parsed content to {cache_path}")
        except Exception as e:
            print(f"Error saving to cache file {cache_path}: {e}")

    def _cleanup_old_cache_files(self, file_path: Path) -> None:
        """
        Remove old cache files for the same document (with different hashes).

        Args:
            file_path (Path): The path to the PDF file.
        """
        try:
            pattern = f"{file_path.stem}_*.md"
            current_hash = self._get_file_hash(file_path)

            for cache_file in self.cache_dir.glob(pattern):
                parts = cache_file.stem.split("_")
                if len(parts) > 1:
                    file_hash = parts[-1]
                    if file_hash != current_hash:
                        cache_file.unlink()
                        print(f"Removed old cache file: {cache_file}")
        except Exception as e:
            print(f"Error cleaning up old cache files: {e}")

    def parse_document(self, file_path: Path, use_cache: bool = True) -> str:
        """
        Parses a single PDF document and returns its content as a single string.
        Uses caching to avoid re-parsing the same document.

        Args:
            file_path (Path): The path to the PDF file.
            use_cache (bool): Whether to use caching. Defaults to True.

        Returns:
            str: The extracted text content of the document.
        """
        # try:
        #     documents: List[Document] = self.parser.load_data(str(file_path))
        #     return "\n".join([doc.text for doc in documents])
        # except Exception as e:
        #     print(f"Error parsing document {file_path.name}: {e}")
        #     return ""

        if not file_path.exists():
            print(f"File not found: {file_path}")
            return ""

        # --- check cache ---
        if use_cache:
            cache_path = self._get_cache_path(file_path)

            if cache_path.exists():
                print(f"Loading from cache: {cache_path}")
                cached_content = self._load_from_cache(cache_path)
                if cached_content:
                    return cached_content

        # --- Parse document using API ---
        print(f"Parsing document with API: {file_path.name}")
        try:
            documents: List[Document] = self.parser.load_data(str(file_path))
            content = "\n".join([doc.text for doc in documents])
            print(content)

            # --- Save to cache if enabled ---
            if use_cache and content:
                cache_path = self._get_cache_path(file_path)
                self._save_to_cache(cache_path, content)
                self._cleanup_old_cache_files(file_path)

            return content

        except Exception as e:
            print(f"Error parsing document {file_path.name}: {e}")
            return ""


if __name__ == "__main__":
    # Example usage
    parser = PDFParser()
    sample_pdf_path = Path("./data/test1.pdf")
    content = parser.parse_document(sample_pdf_path)

    # Write the parsed content to a markdown file for inspection
    with open("parsed_output.md", "w") as f:
        f.write(content)
    print("Parsed content written to parsed_output.md")
    print(content)
