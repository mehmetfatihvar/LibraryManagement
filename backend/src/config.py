"""Application configuration and path constants."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LIBRARY_XML = DATA_DIR / "library.xml"
INVALID_LIBRARY_XML = DATA_DIR / "invalid_library.xml"
SCHEMA_XSD = DATA_DIR / "schema.xsd"
REPORT_XSLT = DATA_DIR / "report.xslt"

API_KEY = "library-api-key-dev-2026"
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]
