"""External service integration router."""

import httpx
from fastapi import APIRouter, Depends

from ..auth import require_xml_accept
from ..responses import xml_error_response, xml_response
from ..external_service import enrich_isbn
from ..validators import ValidationError

router = APIRouter(prefix="/external", tags=["External"])


@router.get("/enrich/{isbn}", dependencies=[Depends(require_xml_accept)])
async def enrich_book(isbn: str):
    """Fetch book data from Open Library, convert JSON to XML, validate and return."""
    try:
        xml_bytes = await enrich_isbn(isbn)
        return xml_response(xml_bytes)
    except ValueError as exc:
        return xml_error_response(404, str(exc), f"isbn={isbn}")
    except httpx.HTTPError as exc:
        return xml_error_response(502, "External service unavailable", str(exc))
    except ValidationError as exc:
        return xml_error_response(400, "Enriched data failed validation", exc.log[:500])
