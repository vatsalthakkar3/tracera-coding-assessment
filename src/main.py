import time
from src.config import DOCUMENTS_DIR, OUTPUT_CSV_PATH, COLUMNS_TO_EXTRACT
from src.utils.data_extractor import DataExtractor
from src.utils.file_handler import get_pdf_files, save_to_csv


def main():
    """
    Main function to run the end-to-end data extraction pipeline.
    """
    print("--- Starting ESG Flo Data Extraction Process ---")
    start_time = time.time()

    pdf_files = get_pdf_files(DOCUMENTS_DIR)
    if not pdf_files:
        print(f"No PDF files found in {DOCUMENTS_DIR}. Exiting.")
        return

    print(f"Found {len(pdf_files)} documents to process.")

    # ----------------------------- Initialize the extractor -----------------------------
    # For standard documents:
    extractor = DataExtractor()

    # For long documents that might exceed context limits (Experimental):
    # extractor = AdvancedDataExtractor(chunk_size=4000, chunk_overlap=300)
    # -------------------------------------------------------------------------------------

    all_extracted_records = []
    for file_path in pdf_files:
        try:
            records = extractor.extract_from_file(file_path)
            all_extracted_records.extend(records)
        except Exception as e:
            print(f"!! An unexpected error occurred while processing {file_path.name}: {e}")

    if all_extracted_records:
        save_to_csv(all_extracted_records, OUTPUT_CSV_PATH, COLUMNS_TO_EXTRACT)
    else:
        print("Extraction process finished, but no records were extracted.")

    end_time = time.time()
    print(f"--- Process finished in {end_time - start_time:.2f} seconds ---")


if __name__ == "__main__":
    main()
