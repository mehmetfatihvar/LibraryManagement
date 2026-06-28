"""Open Library external service integration."""

import logging
import re

import httpx
from lxml import etree

from .validators import validate_or_raise

logger = logging.getLogger(__name__)

OPEN_LIBRARY_BASE = "https://openlibrary.org"
DEFAULT_GENRE = "Classic"
HTTP_HEADERS = {
    "User-Agent": "XMLLibraryManagementSystem/1.0 (Mersin University; academic project)",
    "Accept": "application/json",
}


def normalize_isbn(isbn: str) -> str:
    digits = re.sub(r"[^0-9Xx]", "", isbn)
    if len(digits) == 13:
        return f"{digits[0:3]}-{digits[3:4]}-{digits[4:9]}-{digits[9:12]}-{digits[12]}"
    if len(digits) == 10:
        isbn13 = f"978{digits[:9]}"
        total = sum(
            int(d) * (1 if i % 2 else 3)
            for i, d in enumerate(isbn13)
        )
        check = (10 - (total % 10)) % 10
        full = isbn13 + str(check)
        return f"{full[0:3]}-{full[3:4]}-{full[4:9]}-{full[9:12]}-{full[12]}"
    return isbn


async def fetch_open_library(isbn: str) -> dict:
    """Fetch book metadata from Open Library JSON API."""
    clean = re.sub(r"[^0-9Xx]", "", isbn)
    books_api_url = (
        f"{OPEN_LIBRARY_BASE}/api/books"
        f"?bibkeys=ISBN:{clean}&format=json&jscmd=data"
    )

    async with httpx.AsyncClient(
        timeout=15.0, headers=HTTP_HEADERS, follow_redirects=True
    ) as client:
        response = await client.get(books_api_url)
        response.raise_for_status()
        payload = response.json()

    book_key = f"ISBN:{clean}"
    if book_key not in payload:
        isbn_url = f"{OPEN_LIBRARY_BASE}/isbn/{clean}.json"
        async with httpx.AsyncClient(
            timeout=15.0, headers=HTTP_HEADERS, follow_redirects=True
        ) as client:
            fallback = await client.get(isbn_url)
            if fallback.status_code == 404:
                raise ValueError(f"ISBN not found in Open Library: {isbn}")
            fallback.raise_for_status()
            data = fallback.json()
        return await _parse_isbn_edition(data, isbn)

    data = payload[book_key]
    return _parse_books_api_data(data, isbn)


def _parse_books_api_data(data: dict, isbn: str) -> dict:
    authors = [a.get("name", "Unknown") for a in data.get("authors", [])]
    publishers = data.get("publishers", [])
    publisher = publishers[0].get("name", "Unknown") if publishers else "Unknown"

    publish_year = None
    for date_str in [data.get("publish_date"), str(data.get("publish_year", ""))]:
        if date_str:
            match = re.search(r"\d{4}", str(date_str))
            if match:
                publish_year = int(match.group())
                break

    return {
        "title": data.get("title", "Unknown Title"),
        "authors": authors or ["Unknown Author"],
        "publisher": publisher,
        "publish_year": publish_year,
        "description": _extract_description(data),
        "isbn": normalize_isbn(isbn),
    }


async def _parse_isbn_edition(data: dict, isbn: str) -> dict:
    authors = []
    for author_ref in data.get("authors", []):
        key = author_ref.get("key", "")
        if key:
            async with httpx.AsyncClient(
                timeout=15.0, headers=HTTP_HEADERS, follow_redirects=True
            ) as c:
                author_resp = await c.get(f"{OPEN_LIBRARY_BASE}{key}.json")
                if author_resp.status_code == 200:
                    author_data = author_resp.json()
                    authors.append(author_data.get("name", "Unknown Author"))

    publish_year = None
    for date_str in [data.get("publish_date"), str(data.get("publish_year", ""))]:
        if date_str:
            match = re.search(r"\d{4}", str(date_str))
            if match:
                publish_year = int(match.group())
                break

    return {
        "title": data.get("title", "Unknown Title"),
        "authors": authors or ["Unknown Author"],
        "publisher": data.get("publishers", ["Unknown"])[0]
        if isinstance(data.get("publishers"), list)
        else data.get("publisher", "Unknown"),
        "publish_year": publish_year,
        "description": _extract_description(data),
        "isbn": normalize_isbn(isbn),
    }


def _extract_description(data: dict) -> str:
    desc = data.get("description", "")
    if isinstance(desc, dict):
        return desc.get("value", "")
    return str(desc) if desc else ""


def json_to_enriched_xml(book_data: dict) -> bytes:
    """Convert Open Library JSON response to validated XML."""
    root = etree.Element("enrichedBook")
    root.set("isbn", book_data["isbn"])
    etree.SubElement(root, "title").text = book_data["title"]
    etree.SubElement(root, "author").text = book_data["authors"][0]
    etree.SubElement(root, "publisher").text = str(book_data.get("publisher", "Unknown"))
    if book_data.get("publish_year"):
        etree.SubElement(root, "publicationYear").text = str(book_data["publish_year"])
    if book_data.get("description"):
        etree.SubElement(root, "description").text = book_data["description"][:500]
    categories = etree.SubElement(root, "categories")
    etree.SubElement(categories, "category").text = DEFAULT_GENRE
    etree.SubElement(root, "source").text = "Open Library API"

    validate_or_raise(root)
    return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")


async def enrich_isbn(isbn: str) -> bytes:
    """Full pipeline: fetch JSON, convert to XML, validate, return."""
    data = await fetch_open_library(isbn)
    return json_to_enriched_xml(data)
