import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser

from src.schemas import DocumentExtractionResult
from src.config import OPENAI_API_KEY, LLM_MODEL_NAME, GEMINI_API_KEY


class LLMService:
    """
    A service class for interacting with a LLM
    to perform structured data extraction and consolidation.
    """

    EXTRACTION_PROMPT_TEMPLATE = """
    You are an expert AI assistant for extracting structured data from utility bills.
    Your task is to extract the specified fields from the document text provided below.

    Follow these instructions carefully:
    1.  Extract all records present in the document. A single document may contain multiple billing periods or accounts.
    2.  For dates, normalize them to a standard 'YYYY-MM-DD' format.
    3.  For 'Usage' and 'Cost', extract only the numerical values, removing any currency symbols or units.
    4.  If a value for a field is not found in a record, you MUST represent it with a hyphen '-'. Do not leave it null or empty.
    5.  Pay attention to regional differences in number and date formats (e.g., DD/MM/YYYY vs MM/DD/YYYY, or 1,000.00 vs 1.000,00) and normalize them.
    6.  US-style number formatting is expected (e.g., 1,234.56). Use comma as thousand separator. Do not use periods as thousand separators.
    7.  Ensure that the extracted data adheres to the schema provided in the format instructions.

    Document Text:
    ---
    {document_text}
    ---

    {format_instructions}
    """

    CONSOLIDATION_PROMPT_TEMPLATE = """
    You are an expert data consolidation AI. You will be given a list of data records extracted from a single document.
    These records may be duplicated, incomplete, or contain slight variations because they were extracted from different parts of the same document.

    Your task is to analyze all the records and produce a final, clean, and unique list.
    Follow these rules precisely:
    1.  **Final Output Format:** Final Output should include all the files present in the input list, but without duplicates and with merged information where applicable. Use '-' for any missing fields.
    2.  **Merge Duplicates:** Combine records that clearly refer to the same billing period or item. Use clues like account numbers, meter numbers, and overlapping dates to identify duplicates.
    3.  **Prioritize Completeness:** When merging, create a single consolidated record. For each field, use the value that is most complete and accurate. For example, prefer '5356338-03' over '535633803'. Always prefer an actual value over a hyphen ('-').
    4.  **Discard Noise:** Remove any records that are completely empty or contain no meaningful information (e.g., all fields are '-').
    5.  **Maintain Structure:** The final output must be a clean list of unique records.
    
    Here is the list of raw, extracted records:
    ---
    {raw_records_json}
    ---

    {format_instructions}
    """

    def __init__(
        self,
        model_name: str = LLM_MODEL_NAME,
        gemini_api_key: str = GEMINI_API_KEY,
        openai_api_key: str = OPENAI_API_KEY,
    ):
        """
        Initializes the LLMService.

        Args:
            model_name (str): The name of the OpenAI model to use.
            gemini_api_key (str): The Gemini API key.
            openai_api_key (str): The OpenAI API key.
        """
        self.output_parser = PydanticOutputParser(pydantic_object=DocumentExtractionResult)

        if gemini_api_key:
            print("Using Gemini LLM")
            self.llm = ChatGoogleGenerativeAI(
                model=model_name, google_api_key=gemini_api_key, temperature=0.1
            )
        elif openai_api_key:
            print("Using OpenAI LLM as fallback")
            self.llm = ChatOpenAI(model=model_name, openai_api_key=openai_api_key, temperature=0.1)
        else:
            raise ValueError(
                "No API key provided for either Gemini or OpenAI.  Please set GEMINI_API_KEY or OPENAI_API_KEY in .env"
            )

    def extract_structured_data(self, text_content: str) -> DocumentExtractionResult:
        """
        Extracts structured data from text content using the LLM.

        Args:
            text_content (str): The text content of a document.

        Returns:
            DocumentExtractionResult: A Pydantic object containing the extracted records.
        """
        prompt = ChatPromptTemplate.from_template(
            template=self.EXTRACTION_PROMPT_TEMPLATE,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
        )

        chain = prompt | self.llm | self.output_parser

        try:
            response = chain.invoke({"document_text": text_content})
            return response
        except Exception as e:
            print(f"An error occurred during LLM invocation: {e}")
            return DocumentExtractionResult(records=[])

    def consolidate_records(self, records: DocumentExtractionResult) -> DocumentExtractionResult:
        """
        Uses an LLM call to clean, merge, and deduplicate a list of extracted records.

        Args:
            records (list[ExtractedRecord]): A list of extracted records to consolidate.

        Returns:
            DocumentExtractionResult: A Pydantic object containing the consolidated records.
        """
        if not records:
            return DocumentExtractionResult(records=[])

        # Convert the list of Pydantic models to a JSON string for the prompt
        raw_records_json = json.dumps([r.model_dump(by_alias=False) for r in records], indent=2)

        prompt = ChatPromptTemplate.from_template(
            template=self.CONSOLIDATION_PROMPT_TEMPLATE,
            partial_variables={"format_instructions": self.output_parser.get_format_instructions()},
        )

        chain = prompt | self.llm | self.output_parser

        print("   Calling LLM to consolidate results...")
        try:
            response = chain.invoke({"raw_records_json": raw_records_json})
            return response
        except Exception as e:
            print(f"An error occurred during LLM invocation: {e}")
            return DocumentExtractionResult(records=[])


if __name__ == "__main__":
    # Example usage
    llm_service = LLMService()
    sample_text = """
    BEHR PROCESS CORPORATION / Page 1 of 4

    # Your electricity bill

    For billing and service inquiries: 1-800-990-7788

    Website: www.sce.com

    # Customer account

    Account Number: 7851218574918

    Rotating outage: Group A028

    Amount due: $4,582.36

    # Service account

    Service Account Number: 8111757581

    POD-ID: 101760940005199198

    Address: 33 Tsim Sha Tsui Road, Kowloon, Hong

    Date bill prepared: 02/21/23

    # Your account summary

    | Previous Balance                 | $25,677.53  |
    | -------------------------------- | ----------- |
    | Payment Received 02/03/23        | -$25,383.24 |
    | Payment Received 02/17/23        | -$22,970.21 |
    | Credit balance                   | -$22,675.92 |
    | Your new charges                 | $27,256.52  |
    | Late payment charge              | $1.67       |
    | UUT Consolidated Charges         | $0.09       |
    | Total amount you owe by 03/13/23 | $4,582.36   |

    # Your cost varies by time of day

    # Winter cost periods (Oct 01-May 31)

    |                | Weekdays   | Weekends & Holidays |
    | -------------- | ---------- | ------------------- |
    | Mid peak       | 4pm - 9pm  | 4pm - 9pm           |
    | Off peak       | 12am - 8am | 12am - 8am          |
    |                | 9pm - 12am | 9pm - 12am          |
    | Super off peak | 8am - 4pm  | 8am - 4pm           |

    Please return the payment stub below with your payment and make your check payable to Southern California Edison.

    (14-574) Tear here

    If you want to pay in person, call 1-800-747-8908 for locations, or you can pay online at www.sce.com.

    Tear here

    # Payment Stub

    Customer account: 7851218574918

    Amount due by 03/13/23: $4,582.36

    Please write this number on the memo line of your check. Make your check payable to:

    Amount enclosed: $

    Southern California Edison.

    STMT 02212023 P

    33 Tsim Sha Tsui Road, Kowloon, Hong

    P.O. BOX 300

    ROSEMEAD, CA 91772-0002
    """
    result = llm_service.extract_structured_data(sample_text)
    for record in result.records:
        print(record.model_dump(by_alias=True, exclude_none=True))

    consolidated_result = llm_service.consolidate_records(result.records)
    print("Consolidated Records:")
    for record in consolidated_result.records:
        print(record.model_dump(by_alias=True, exclude_none=True))
