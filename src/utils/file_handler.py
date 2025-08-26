from pathlib import Path
from typing import List
import pandas as pd


def get_pdf_files(directory: Path) -> List[Path]:
    """
    Gets a list of all PDF files in a given directory.

    Args:
        directory (Path): The directory to search for PDF files.

    Returns:
        List[Path]: A list of paths to the PDF files.
    """
    if not directory.is_dir():
        print(f"Error: Directory not found at {directory}")
        return []
    return list(directory.glob("*.pdf"))


def save_to_csv(data: List[dict], output_path: Path, columns: List[str]):
    """
    Saves a list of dictionaries to a CSV file.

    Args:
        data (List[dict]): The data to save.
        output_path (Path): The path to the output CSV file.
        columns (List[str]): The exact order of columns for the CSV.
    """
    if not data:
        print("Warning: No data to save.")
        return

    df = pd.DataFrame(data)

    final_columns = ["Filename"] + columns
    for col in final_columns:
        if col not in df.columns:
            df[col] = "-"

    df = df[final_columns]

    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"\nSuccessfully saved extracted data to {output_path}")


if __name__ == "__main__":
    # Example usage
    from src.config import DOCUMENTS_DIR, COLUMNS_TO_EXTRACT

    pdf_files = get_pdf_files(DOCUMENTS_DIR)
    for file in pdf_files:
        print(f"Found PDF file: {file.name}")

    # Example save to CSV
    record_dict = [
        {
            "Account Number": "ACC-12345",
            "Meter Number": "MTR-67890",
            "From Date": "2025-01-01",
            "To Date": "2025-01-31",
            "Usage": "154,150.50",
            "Cost": "54,575.25",
            "Filename": "test1",
        },
        {
            "Account Number": "ACC-54321",
            "Meter Number": "MTR-09876",
            "From Date": "2025-02-01",
            "To Date": "2025-02-28",
            "Usage": "120,000.00",
            "Cost": "45,000.00",
            "Filename": "test2",
        },
    ]
    save_to_csv(record_dict, Path("output/extracted_data_example.csv"), COLUMNS_TO_EXTRACT)
