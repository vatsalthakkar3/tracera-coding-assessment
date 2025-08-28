import pandas as pd
from typing import Dict, Any
from collections import Counter


def _normalize_value(value):
    """A helper to clean and standardize values for comparison."""
    if value is None or pd.isna(value):
        return ""
    # Convert to string, remove leading/trailing spaces, and convert to lowercase
    s_value = str(value).strip().lower()
    # Remove characters that can cause comparison issues in numeric strings
    s_value = s_value.replace(",", "").replace("$", "")
    return s_value


def _normalize_dates(series):
    """Attempt to parse dates and convert to a standard YYYY-MM-DD format."""
    # Try parsing to datetime
    parsed_dates = pd.to_datetime(series, errors="coerce")
    # For successfully parsed dates, format them. For others, keep original (normalized) string.
    return parsed_dates.dt.strftime("%Y-%m-%d").fillna(series)


def calculate_metrics(ground_truth_path: str, extracted_data_path: str) -> Dict[str, Any]:
    """
    Compares the extracted data with the ground truth and calculates accuracy.

    Args:
        ground_truth_path (str): Path to the ground truth CSV file.
        extracted_data_path (str): Path to the extracted data CSV file.

    Returns:
        Dict[str, Any]: A dictionary containing the accuracy report.
    """
    try:
        gt_df = pd.read_csv(ground_truth_path, dtype=str)
        extracted_df = pd.read_csv(extracted_data_path, dtype=str)
    except FileNotFoundError as e:
        return {"error": f"File not found: {e.filename}"}

    # --- Data Normalization ---
    # The columns to compare
    comparison_cols = [
        "Account Number",
        "Meter Number",
        "From Date",
        "To Date",
        "Usage",
        "Cost",
    ]
    date_cols = ["From Date", "To Date"]

    for col in comparison_cols:
        # Apply general normalization to all columns
        gt_df[col] = gt_df[col].apply(_normalize_value)
        if col in extracted_df.columns:
            extracted_df[col] = extracted_df[col].apply(_normalize_value)

        # Apply specific date normalization to date columns
        if col in date_cols:
            gt_df[col] = _normalize_dates(gt_df[col])
            if col in extracted_df.columns:
                extracted_df[col] = _normalize_dates(extracted_df[col])

    # --- Comparison Logic ---
    results = {
        "overall_accuracy": 0,
        "field_accuracies": {},
        "mismatches": [],
        "total_fields": 0,
        "total_correct_fields": 0,
    }

    # Initialize counters
    for col in comparison_cols:
        results["field_accuracies"][col] = {"correct": 0, "total": 0}

    # Ensure 'Filename' is treated as a string and normalized
    gt_df["Filename"] = gt_df["Filename"].astype(str).apply(_normalize_value)
    extracted_df["Filename"] = extracted_df["Filename"].astype(str).apply(_normalize_value)

    common_filenames = set(gt_df["Filename"]) & set(extracted_df["Filename"])

    for filename in sorted(list(common_filenames)):
        gt_records = gt_df[gt_df["Filename"] == filename]
        extracted_records = extracted_df[extracted_df["Filename"] == filename]

        for col in comparison_cols:
            gt_values = Counter(gt_records[col].tolist())

            if col not in extracted_records.columns:
                extracted_values = Counter()
            else:
                extracted_values = Counter(extracted_records[col].tolist())

            # Calculate intersection of the multisets
            correct_count = sum((gt_values & extracted_values).values())
            total_count = len(gt_records)

            results["field_accuracies"][col]["correct"] += correct_count
            results["field_accuracies"][col]["total"] += total_count
            results["total_correct_fields"] += correct_count
            results["total_fields"] += total_count

            # --- Detailed Mismatch Logging ---
            if gt_values != extracted_values:
                mismatch_info = {
                    "filename": filename,
                    "field": col,
                    "ground_truth": gt_records[col].tolist(),
                    "extracted": extracted_records[col].tolist()
                    if col in extracted_records.columns
                    else [],
                }
                results["mismatches"].append(mismatch_info)

    # --- Calculate Final Percentages ---
    if results["total_fields"] > 0:
        results["overall_accuracy"] = (
            results["total_correct_fields"] / results["total_fields"]
        ) * 100

    final_field_accuracies = {}
    for col, data in results["field_accuracies"].items():
        if data["total"] > 0:
            accuracy = (data["correct"] / data["total"]) * 100
            final_field_accuracies[col] = f"{accuracy:.2f}% ({data['correct']}/{data['total']})"
        else:
            final_field_accuracies[col] = "N/A"
    results["field_accuracies"] = final_field_accuracies

    return results


def display_report(report: Dict[str, Any]):
    """Prints a formatted report to the console."""
    if "error" in report:
        print(f"Error generating report: {report['error']}")
        return

    print("-- Extraction Accuracy Report --")
    print(f"Overall Field Accuracy: {report['overall_accuracy']:.2f}%")
    print(f"({report['total_correct_fields']} / {report['total_fields']} correct fields)\n")

    print("Accuracy per Field:")
    for field, acc in report["field_accuracies"].items():
        print(f"- {field:<15}: {acc}")

    if report["mismatches"]:
        print("\n--- Mismatches Detected ---")
        for mismatch in report["mismatches"]:
            print(f"\nFile  : {mismatch['filename']}")
            print(f"Field : {mismatch['field']}")
            print(f"  - Ground Truth: {mismatch['ground_truth']}")
            print(f"  - Extracted   : {mismatch['extracted']}")


if __name__ == "__main__":
    # This allows the script to be run directly for evaluation.
    # Make sure the paths are correct relative to the project root.
    from pathlib import Path

    PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
    GROUND_TRUTH_CSV = PROJECT_ROOT / "data" / "ground_truth.csv"
    EXTRACTED_DATA_CSV = PROJECT_ROOT / "output" / "extracted_data.csv"

    print(
        f"Comparing '{EXTRACTED_DATA_CSV.relative_to(PROJECT_ROOT)}' with '{GROUND_TRUTH_CSV.relative_to(PROJECT_ROOT)}'"
    )

    if not EXTRACTED_DATA_CSV.exists():
        print(f"\nError: Extracted data file not found at '{EXTRACTED_DATA_CSV}'")
        print("Please run the main extraction process first with 'make run'.")
    else:
        report = calculate_metrics(str(GROUND_TRUTH_CSV), str(EXTRACTED_DATA_CSV))
        display_report(report)
