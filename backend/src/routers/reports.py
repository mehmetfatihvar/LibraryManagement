"""Reports and XPath demo router."""

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse

from ..auth import require_xml_accept
from ..responses import xml_response
from ..xpath_queries import run_all_queries
from ..xslt_transformer import transform_to_html

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/dashboard")
async def dashboard_report():
    """XSLT-transformed HTML dashboard."""
    html = transform_to_html()
    return HTMLResponse(content=html)


@router.get("/xpath", dependencies=[Depends(require_xml_accept)])
async def xpath_demo():
    """Run all XPath queries and return results as XML."""
    from lxml import etree

    results = run_all_queries()
    root = etree.Element("xpathResults")
    for query_name, items in results.items():
        section = etree.SubElement(root, "query")
        section.set("name", query_name)
        section.set("count", str(len(items)))
        for item in items:
            item_el = etree.SubElement(section, "result")
            for key, value in item.items():
                child = etree.SubElement(item_el, key)
                child.text = str(value) if value is not None else ""

    from ..xml_responses import element_to_bytes
    return xml_response(element_to_bytes(root))
