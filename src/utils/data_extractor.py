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

        # --- Consolidate Stage ---
        try:
            consolidated_result = self.llm_service.consolidate_records(extraction_result.records)
            final_records = consolidated_result.records
        except Exception as e:
            print(f"   [Error] Failed to consolidate records: {e}. Returning raw data.")
            final_records = extraction_result.records

        # --- Format the results ---
        formatted_records = []
        for record in final_records:
            record_dict = record.model_dump(by_alias=True, exclude_none=True)
            record_dict["Filename"] = file_path.name.split(".pdf")[0]
            print(record_dict)
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

    def extract_from_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """
        Extracts structured data from a large PDF file using chunking.

        Args:
            file_path (Path): The path to the PDF file.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, where each dictionary
                                  represents an extracted record.
        """
        print(f"-> Starting ADVANCED extraction for: {file_path.name}")

        # --- Parse PDF to get text content ---
        document_text = self.parser.parse_document(file_path)
        if not document_text:
            print(f"   [Warning] Could not parse content for {file_path.name}")
            return []

        # --- Split text into chunks ---
        chunks = self.text_splitter.split_text(document_text)
        print(f"   Document split into {len(chunks)} chunks.")

        # --- Process each chunk and collect raw results ---
        raw_records = []
        for i, chunk in enumerate(chunks):
            print(f"   Processing chunk {i + 1}/{len(chunks)}...")
            try:
                extraction_result = self.llm_service.extract_structured_data(chunk)
                raw_records.extend(extraction_result.records)
            except Exception as e:
                print(f"   [Error] Could not process chunk {i + 1}: {e}")

        if not raw_records:
            print(f"   => No records found in {file_path.name}")
            return []

        print(f"   Found {len(raw_records)} raw records from all chunks.")

        # --- Consolidate Stage ---
        try:
            consolidated_result = self.llm_service.consolidate_records(raw_records)
            final_records = consolidated_result.records
        except Exception as e:
            print(f"   [Error] Failed to consolidate records: {e}. Returning raw data.")
            final_records = raw_records

        # --- Final formatting ---
        formatted_records = []
        for record in final_records:
            record_dict = record.model_dump(by_alias=True, exclude_none=True)
            record_dict["Filename"] = file_path.name.split(".pdf")[0]
            print(record_dict)
            formatted_records.append(record_dict)

        print(
            f"   => Consolidated to {len(formatted_records)} final unique records for {file_path.name}"
        )
        return formatted_records
