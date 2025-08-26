from pathlib import Path
from typing import List
from llama_parse import LlamaParse
from langchain.schema.document import Document
from src.config import LLAMA_CLOUD_API_KEY


class PDFParser:
    """A class to parse PDF documents using the LlamaParse API."""

    def __init__(self, api_key: str = LLAMA_CLOUD_API_KEY):
        """
        Initializes the PDFParser.

        Args:
            api_key (str): The API key for the Llama Cloud service.
        """
        if not api_key:
            raise ValueError("Llama Cloud API key is required for parsing PDFs.")
        self.parser = LlamaParse(api_key=api_key, result_type="markdown", verbose=True)

    def parse_document(self, file_path: Path) -> str:
        """
        Parses a single PDF document and returns its content as a single string.

        Args:
            file_path (Path): The path to the PDF file.

        Returns:
            str: The extracted text content of the document.
        """
        try:
            documents: List[Document] = self.parser.load_data(str(file_path))
            # Combine content from all parsed pages/sections into one string
            return "\n".join([doc.text for doc in documents])
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
