from pathlib import Path
from typing import List, Dict, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
from .pdf_parser import PDFParser
from .llm_service import LLMService


class DataExtractor:
    """
    Orchestrates the data extraction process from a PDF document.
    """

    def __init__(self):
        """Initializes the DataExtractor with a PDF parser and LLM service."""
        self.parser = PDFParser()
        self.llm_service = LLMService()

    def extract_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts structured data from a single PDF file.

        Args:
            file_path (Path): The path to the PDF file.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                  represents an extracted record.
        """
        print(f"-> Starting extraction for: {file_path.name}")

        # --- Parse PDF to get text content ---
        document_text = self.parser.parse_document(file_path)
        if not document_text:
            print(f"   [Warning] Could not parse or empty content for {file_path.name}")
            return []

        print(f"   => Document Parsing completed for {file_path.name}")

        # --- Use LLM to extract structured data ---
        extraction_result = self.llm_service.extract_structured_data(document_text)

        # --- Format the results ---
        formatted_records = []
        for record in extraction_result.records:
            record_dict = record.model_dump(by_alias=True, exclude_none=True)
            record_dict["Filename"] = file_path.name.split(".pdf")[0]
            formatted_records.append(record_dict)

        print(f"   => Found {len(formatted_records)} records in {file_path.name}")
        return formatted_records


class AdvancedDataExtractor:
    """
    Orchestrates data extraction using a Map-Reduce approach to handle large documents.
    It splits the document into chunks and processes each one individually.
    """

    def __init__(self, chunk_size: int = 4000, chunk_overlap: int = 300):
        """
        Initializes the AdvancedDataExtractor.

        Args:
            chunk_size (int): The character count for each text chunk.
            chunk_overlap (int): The number of characters to overlap between chunks.
        """
        self.parser = PDFParser()
        self.llm_service = LLMService()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size, chunk_overlap=chunk_overlap
        )
