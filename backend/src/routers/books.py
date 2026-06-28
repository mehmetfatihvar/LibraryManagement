"""Books REST API router — XML-only content negotiation."""

from fastapi import APIRouter, Depends, Request
from lxml import etree

from ..auth import require_api_key, require_xml_accept
from ..responses import xml_error_response, xml_response
from ..validators import ValidationError
from ..xml_manager import BookNotFoundError, XmlManager
from ..xml_responses import books_collection_xml, element_to_bytes

router = APIRouter(prefix="/books", tags=["Books"])
manager = XmlManager()


@router.get("", dependencies=[Depends(require_xml_accept)])
async def list_books(
    request: Request,
    genre: str | None = None,
    search: str | None = None,
    page: int = 1,
    limit: int = 10,
):
    books, total = manager.get_all_books(genre=genre, search=search, page=page, limit=limit)
    content = books_collection_xml(books)
    response = xml_response(content)
    response.headers["X-Total-Count"] = str(total)
    response.headers["X-Page"] = str(page)
    response.headers["X-Limit"] = str(limit)
    return response


@router.get("/{book_id}", dependencies=[Depends(require_xml_accept)])
async def get_book(book_id: str):
    try:
        book = manager.get_book_by_id(book_id)
        return xml_response(element_to_bytes(book))
    except BookNotFoundError:
        return xml_error_response(404, "Book not found", f"id={book_id}")


@router.post("", dependencies=[Depends(require_api_key), Depends(require_xml_accept)])
async def create_book(request: Request):
    body = await request.body()
    if not body:
        return xml_error_response(400, "Missing request body", "POST requires XML book payload")

    try:
        book_element = manager.parse_book_xml(body)
        created = manager.add_book(book_element)
        return xml_response(element_to_bytes(created), status_code=201)
    except ValidationError as exc:
        return xml_error_response(400, str(exc), exc.log[:500] if exc.log else "")
    except ValueError as exc:
        return xml_error_response(400, str(exc))


@router.put("/{book_id}", dependencies=[Depends(require_api_key), Depends(require_xml_accept)])
async def update_book(book_id: str, request: Request):
    body = await request.body()
    if not body:
        return xml_error_response(400, "Missing request body")

    try:
        book_element = manager.parse_book_xml(body)
        updated = manager.update_book(book_id, book_element)
        return xml_response(element_to_bytes(updated))
    except BookNotFoundError:
        return xml_error_response(404, "Book not found", f"id={book_id}")
    except ValidationError as exc:
        return xml_error_response(400, str(exc), exc.log[:500] if exc.log else "")
    except ValueError as exc:
        return xml_error_response(400, str(exc))


@router.delete("/{book_id}", dependencies=[Depends(require_api_key), Depends(require_xml_accept)])
async def delete_book(book_id: str):
    try:
        manager.delete_book(book_id)
        deleted = etree.Element("result")
        etree.SubElement(deleted, "message").text = "Book deleted successfully"
        etree.SubElement(deleted, "id").text = book_id
        return xml_response(element_to_bytes(deleted))
    except BookNotFoundError:
        return xml_error_response(404, "Book not found", f"id={book_id}")
    except ValueError as exc:
        return xml_error_response(400, str(exc))
