"""Members REST API router — full CRUD."""

from fastapi import APIRouter, Depends, Request
from lxml import etree

from ..auth import require_api_key, require_xml_accept
from ..responses import xml_error_response, xml_response
from ..validators import ValidationError
from ..xml_manager import MemberNotFoundError, XmlManager
from ..xml_responses import element_to_bytes, members_collection_xml

router = APIRouter(prefix="/members", tags=["Members"])
manager = XmlManager()


@router.get("", dependencies=[Depends(require_xml_accept)])
async def list_members(
    membershipType: str | None = None,
    search: str | None = None,
):
    members = manager.get_all_members(
        membership_type=membershipType,
        search=search,
    )
    return xml_response(members_collection_xml(members))


@router.get("/{member_id}", dependencies=[Depends(require_xml_accept)])
async def get_member(member_id: str):
    try:
        member = manager.get_member_by_id(member_id)
        return xml_response(element_to_bytes(member))
    except MemberNotFoundError:
        return xml_error_response(404, "Member not found", f"id={member_id}")


@router.post("", dependencies=[Depends(require_api_key), Depends(require_xml_accept)])
async def create_member(request: Request):
    body = await request.body()
    if not body:
        return xml_error_response(400, "Missing request body")

    try:
        member_element = manager.parse_member_xml(body)
        created = manager.add_member(member_element)
        return xml_response(element_to_bytes(created), status_code=201)
    except ValidationError as exc:
        return xml_error_response(400, str(exc), exc.log[:500] if exc.log else "")
    except ValueError as exc:
        return xml_error_response(400, str(exc))


@router.put("/{member_id}", dependencies=[Depends(require_api_key), Depends(require_xml_accept)])
async def update_member(member_id: str, request: Request):
    body = await request.body()
    if not body:
        return xml_error_response(400, "Missing request body")

    try:
        member_element = manager.parse_member_xml(body)
        updated = manager.update_member(member_id, member_element)
        return xml_response(element_to_bytes(updated))
    except MemberNotFoundError:
        return xml_error_response(404, "Member not found", f"id={member_id}")
    except ValidationError as exc:
        return xml_error_response(400, str(exc), exc.log[:500] if exc.log else "")
    except ValueError as exc:
        return xml_error_response(400, str(exc))


@router.delete("/{member_id}", dependencies=[Depends(require_api_key), Depends(require_xml_accept)])
async def delete_member(member_id: str):
    try:
        manager.delete_member(member_id)
        result = etree.Element("result")
        etree.SubElement(result, "message").text = "Member deleted successfully"
        etree.SubElement(result, "id").text = member_id
        return xml_response(element_to_bytes(result))
    except MemberNotFoundError:
        return xml_error_response(404, "Member not found", f"id={member_id}")
    except ValueError as exc:
        return xml_error_response(400, str(exc))
