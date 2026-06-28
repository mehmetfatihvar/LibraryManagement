"""XSLT transformation module for HTML dashboard reports."""

from lxml import etree

from .config import LIBRARY_XML, REPORT_XSLT


def transform_to_html() -> str:
    """Transform library.xml into styled HTML using report.xslt."""
    xml_doc = etree.parse(str(LIBRARY_XML))
    xslt_doc = etree.parse(str(REPORT_XSLT))
    transform = etree.XSLT(xslt_doc)
    result = transform(xml_doc)
    return str(result)
