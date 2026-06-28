"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .auth import XmlHttpException
from .responses import xml_error_response
from .config import CORS_ORIGINS, INVALID_LIBRARY_XML, LIBRARY_XML, SCHEMA_XSD
from .routers import books, borrowings, external, members, reports
from .validators import validate_file_pair, validate_xml
from .xml_manager import XmlManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    manager = XmlManager()
    valid, log = validate_xml(LIBRARY_XML)
    logger.info("library.xml validation: %s", "PASS" if valid else f"FAIL — {log}")

    demo = validate_file_pair(LIBRARY_XML, INVALID_LIBRARY_XML)
    logger.info("Valid file check: %s", demo["valid_result"])
    logger.info("Invalid file check (expected fail): %s", not demo["invalid_result"])

    count = manager.count_books_streaming()
    logger.info("Streaming book count via iterparse: %d", count)
    yield


app = FastAPI(
    title="XML Library Management System API",
    description=(
        "REST API for managing a library catalog stored in XML. "
        "All endpoints consume and return `application/xml` unless noted. "
        "POST, PUT, DELETE require `X-API-Key` header."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_PREFIX = "/api/v1"
app.include_router(books.router, prefix=API_PREFIX)
app.include_router(members.router, prefix=API_PREFIX)
app.include_router(borrowings.router, prefix=API_PREFIX)
app.include_router(reports.router, prefix=API_PREFIX)
app.include_router(external.router, prefix=API_PREFIX)


@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "version": "1.0.0"})


@app.get("/api/v1/validation/demo")
async def validation_demo():
    """Demonstrate XSD validation on valid and invalid XML files."""
    result = validate_file_pair(LIBRARY_XML, INVALID_LIBRARY_XML)
    return JSONResponse(result)


@app.exception_handler(XmlHttpException)
async def xml_http_exception_handler(request: Request, exc: XmlHttpException):
    return xml_error_response(exc.status_code, exc.message, exc.detail)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error: %s", exc)
    accept = request.headers.get("accept", "")
    if "application/xml" in accept or request.url.path.startswith("/api/v1"):
        return xml_error_response(500, "Internal server error", str(exc))
    return JSONResponse(status_code=500, content={"detail": str(exc)})
