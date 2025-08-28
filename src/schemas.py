from typing import List, Optional
from pydantic import BaseModel, Field


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
        description="The meter registration number for the utility service. Should be a string.",
        alias="Meter Number",
    )
    from_date: Optional[str] = Field(
        ...,
        description="The start date of the billing period (for which the usage and cost are calculated) in YYYY-MM-DD format. This is not the due date.",
        alias="From Date",
    )
    to_date: Optional[str] = Field(
        ...,
        description="The end date of the billing period (for which the usage and cost are calculated) in YYYY-MM-DD format. This is not the due date.",
        alias="To Date",
    )
    usage: Optional[str] = Field(
        ...,
        description="""
        The total consumption or usage for the billing period for particular utility service as a string with US-style number formatting. (e.g., kWh, Therms, kL, MJ etc). Extract only the numeric value. This is not amount of money .
        US-style number formatting is expected (e.g., 1,234.56). Use comma as thousand separator. Do not use periods as thousand separators.
        """,
        alias="Usage",
    )
    cost: Optional[str] = Field(
        ...,
        description="""
        The total cost or amount due for the billing period as a string with US-style number formatting.
        Extract only the numeric value, removing any currency symbols or units.
        US-style number formatting is expected (e.g., 1,234.56). Use comma as thousand separator. Do not use periods as thousand separators.
        """,
        alias="Cost",
    )


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
