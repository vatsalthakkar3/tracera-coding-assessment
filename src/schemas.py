from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import re


class ExtractedRecord(BaseModel):
    """
    A Pydantic model representing a single extracted record from a document.
    It corresponds to one row in the final CSV.
    """

    account_number: str = Field(
        ...,
        description="The account number associated with the utility bill. Should be a string.",
        alias="Account Number",
    )
    meter_number: str = Field(
        ...,
        description="The meter number for the utility service. Should be a string.",
        alias="Meter Number",
    )
    from_date: Optional[str] = Field(
        ...,
        description="The start date of the billing period in YYYY-MM-DD format.",
        alias="From Date",
    )
    to_date: Optional[str] = Field(
        ...,
        description="The end date of the billing period in YYYY-MM-DD format.",
        alias="To Date",
    )
    usage: Optional[str] = Field(
        ...,
        description="The total usage for the billing period as a string with US-style number formatting. (e.g., kWh, Therms). Extract only the numeric value.",
        alias="Usage",
    )
    cost: Optional[str] = Field(
        ...,
        description="The total cost or amount due for the billing period as a string with US-style number formatting.",
        alias="Cost",
    )

    @field_validator("usage", "cost")
    def validate_us_number_format(cls, v):
        """
        Validates that the string is a number with US-style commas and up to two decimal places.
        """
        # Regex to match: optional thousands separators, optional decimal with up to two digits.
        # This pattern also allows numbers without commas or decimals (e.g., '123' or '1,234').
        pattern = r"^\d{1,3}(,\d{3})*(\.\d{1,2})?$"

        if not re.match(pattern, v):
            raise ValueError(f"'{v}' is not in a valid US number format (e.g., '1,234.56').")

        return v


class DocumentExtractionResult(BaseModel):
    """
    A Pydantic model to structure the output from the LLM for a single document.
    A document can contain one or more records (e.g., multiple billing periods).
    """

    records: List[ExtractedRecord] = Field(
        description="A list of all records extracted from the document."
    )


if __name__ == "__main__":
    # Example usage
    sample_record = ExtractedRecord.model_validate(
        {
            "Account Number": "ACC-12345",
            "Meter Number": "MTR-67890",
            "From Date": "2023-01-01",
            "To Date": "2023-01-31",
            "Usage": "154,150.50",
            "Cost": "54,575.25",
        }
    )
    print(sample_record)
