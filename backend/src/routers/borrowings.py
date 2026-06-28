"""Borrowings REST API router — circulation (checkout, return, CRUD)."""

from fastapi import APIRouter, Depends, Request
from lxml import etree

from ..auth import require_api_key, require_xml_accept
from ..responses import xml_error_response, xml_response
from ..validators import ValidationError
from ..xml_manager import (
    BookNotFoundError,
    BorrowingNotFoundError,
    MemberNotFoundError,
    XmlManager,
)
from ..xml_responses import borrowings_collection_xml, element_to_bytes

router = APIRouter(prefix="/borrowings", tags=["Borrowings"])
manager = XmlManager()


@router.get("", dependencies=[Depends(require_xml_accept)])
async def list_borrowings(
    status: str | None = None,
    memberRef: str | None = None,
    bookRef: str | None = None,
):
    borrowings = manager.get_all_borrowings(
        status=status,
        member_ref=memberRef,
        book_ref=bookRef,
    )
    return xml_response(borrowings_collection_xml(borrowings, total=len(borrowings)))


@router.get("/{borrowing_id}", dependencies=[Depends(require_xml_accept)])
async def get_borrowing(borrowing_id: str):
    try:
        borrowing = manager.get_borrowing_by_id(borrowing_id)
        return xml_response(element_to_bytes(borrowing))
    except BorrowingNotFoundError:
        return xml_error_response(404, "Borrowing not found", f"id={borrowing_id}")


@router.post("", dependencies=[Depends(require_api_key), Depends(require_xml_accept)])
async def checkout_book(request: Request):
    """Check out a book (circulation checkout)."""
    body = await request.body()
    if not body:
        return xml_error_response(400, "Missing request body")

    try:
        borrowing_element = manager.parse_borrowing_xml(body)
        created = manager.checkout_book(borrowing_element)
        return xml_response(element_to_bytes(created), status_code=201)
    except (BookNotFoundError, MemberNotFoundError) as exc:
        return xml_error_response(404, str(exc))
    except ValidationError as exc:
        return xml_error_response(400, str(exc), exc.log[:500] if exc.log else "")
    except ValueError as exc:
        return xml_error_response(400, str(exc))


@router.put("/{borrowing_id}/return", dependencies=[Depends(require_api_key), Depends(require_xml_accept)])
async def return_book(borrowing_id: str):
    """Return a borrowed book and restore inventory."""
    try:
        returned = manager.return_book(borrowing_id)
        return xml_response(element_to_bytes(returned))
    except BorrowingNotFoundError:
        return xml_error_response(404, "Borrowing not found", f"id={borrowing_id}")
    except ValueError as exc:
        return xml_error_response(400, str(exc))


@router.put("/{borrowing_id}", dependencies=[Depends(require_api_key), Depends(require_xml_accept)])
async def update_borrowing(borrowing_id: str, request: Request):
    body = await request.body()
    if not body:
        return xml_error_response(400, "Missing request body")

    try:
        borrowing_element = manager.parse_borrowing_xml(body)
        updated = manager.update_borrowing(borrowing_id, borrowing_element)
        return xml_response(element_to_bytes(updated))
    except (BookNotFoundError, MemberNotFoundError, BorrowingNotFoundError) as exc:
        code = 404
        return xml_error_response(code, str(exc))
    except ValueError as exc:
        return xml_error_response(400, str(exc))


@router.delete("/{borrowing_id}", dependencies=[Depends(require_api_key), Depends(require_xml_accept)])
async def delete_borrowing(borrowing_id: str):
    try:
        manager.delete_borrowing(borrowing_id)
        result = etree.Element("result")
        etree.SubElement(result, "message").text = "Borrowing record deleted"
        etree.SubElement(result, "id").text = borrowing_id
        return xml_response(element_to_bytes(result))
    except BorrowingNotFoundError:
        return xml_error_response(404, "Borrowing not found", f"id={borrowing_id}")
    except ValueError as exc:
        return xml_error_response(400, str(exc))
