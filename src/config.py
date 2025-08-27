import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- API Keys ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", default="")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", default="")
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

# --- Project Paths ---
BASE_DIR = Path(__file__).resolve().parent.parent
DOCUMENTS_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_CSV_PATH = OUTPUT_DIR / "extracted_data.csv"
CACHE_DIR = BASE_DIR / "cache"

# --- LLM Configuration ---
if GEMINI_API_KEY:
    LLM_MODEL_NAME = "gemini-2.5-flash"  # "gemini-2.5-pro"
elif OPENAI_API_KEY:
    LLM_MODEL_NAME = "gpt-4o"
else:
    raise ValueError(
        "No API key provided for either Gemini or OpenAI.  Please set GEMINI_API_KEY or OPENAI_API_KEY in .env"
    )

# --- Fields to Extract ---
COLUMNS_TO_EXTRACT = [
    "Account Number",
    "Meter Number",
    "From Date",
    "To Date",
    "Usage",
    "Cost",
]

if __name__ == "__main__":
    print(f"Base Directory      : {BASE_DIR}")
    print(f"Documents Directory : {DOCUMENTS_DIR}")
    print(f"Output Directory    : {OUTPUT_DIR}")
    print(f"Output CSV Path     : {OUTPUT_CSV_PATH}")
    print(f"GEMINI API Key      : {'Set' if GEMINI_API_KEY else 'Not Set'}")
    print(f"OpenAI API Key      : {'Set' if OPENAI_API_KEY else 'Not Set'}")
    print(f"Llama Cloud API Key : {'Set' if LLAMA_CLOUD_API_KEY else 'Not Set'}")
    print(f"LLM Model Name      : {LLM_MODEL_NAME}")
    print(f"Columns to Extract  : {COLUMNS_TO_EXTRACT}")
