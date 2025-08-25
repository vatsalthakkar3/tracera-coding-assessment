from typing import List, Union, Optional
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
    usage: Optional[Union[float, str]] = Field(
        ...,
        description="The total usage for the billing period as a number (e.g., kWh, Therms). Extract only the numeric value.",
        alias="Usage",
    )
    cost: Optional[Union[float, str]] = Field(
        ...,
        description="The total cost or amount due for the billing period. Extract only the numeric value.",
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
