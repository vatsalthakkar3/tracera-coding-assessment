import pytest
from unittest.mock import MagicMock
from pathlib import Path

from src.utils.data_extractor import DataExtractor
from src.schemas import DocumentExtractionResult, ExtractedRecord

# Mock data to be returned by the LLM service
MOCK_EXTRACTED_DATA = DocumentExtractionResult(
    records=[
        ExtractedRecord.model_validate(
            {
                "Account Number": "ACC-12345",
                "Meter Number": "MTR-67890",
                "From Date": "2023-01-01",
                "To Date": "2023-01-31",
                "Usage": "154,150.50",
                "Cost": "54,575.25",
            }
        )
    ]
)


@pytest.fixture
def mocked_data_extractor(mocker):
    """Fixture to create a DataExtractor with mocked dependencies."""
    # Mock PDFParser
    mock_pdf_parser = MagicMock()
    mock_pdf_parser.parse_document.return_value = "This is a mock PDF text content."
    mocker.patch("src.utils.data_extractor.PDFParser", return_value=mock_pdf_parser)

    # Mock LLMService
    mock_llm_service = MagicMock()
    mock_llm_service.extract_structured_data.return_value = MOCK_EXTRACTED_DATA
    mocker.patch("src.utils.data_extractor.LLMService", return_value=mock_llm_service)

    return DataExtractor()


def test_extract_from_file_success(mocked_data_extractor):
    """
    Tests the successful extraction flow for a single file.
    """
    dummy_file_path = Path("dummy/doc1.pdf")
    result = mocked_data_extractor.extract_from_file(dummy_file_path)

    assert len(result) == 1
    record = result[0]

    # assert record["Filename"] == "doc1" --- IGNORE ---
    assert record["Account Number"] == "ACC-12345"
    assert record["Usage"] == "154,150.50"

    # Check if the dependencies were called correctly
    mocked_data_extractor.parser.parse_document.assert_called_once_with(dummy_file_path)
    mocked_data_extractor.llm_service.extract_structured_data.assert_called_once_with(
        "This is a mock PDF text content."
    )


def test_extract_from_file_parsing_failure(mocker):
    """
    Tests the case where PDF parsing returns no content.
    """
    mocker.patch("src.utils.data_extractor.PDFParser.parse_document", return_value="")
    mocker.patch("src.utils.data_extractor.LLMService")  # Mock LLM so it's not instantiated

    extractor = DataExtractor()
    result = extractor.extract_from_file(Path("dummy/failed_doc.pdf"))

    assert result == []
    extractor.llm_service.extract_structured_data.assert_not_called()
