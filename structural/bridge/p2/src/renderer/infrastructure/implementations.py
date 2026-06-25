"""Concrete Implementations — output format renderers.

Each renderer knows HOW to serialize PageContent; it is unaware of
the page type that produced it.
"""

from __future__ import annotations

import json
import xml.etree.ElementTree as ET
from xml.dom import minidom

from jinja2 import Environment, PackageLoader, TemplateNotFound, select_autoescape

from renderer.domain.entities import PageContent
from renderer.domain.interfaces import ContentRenderer


class HTMLRenderer(ContentRenderer):
    """Renders pages as HTML using Jinja2 templates."""

    def __init__(self) -> None:
        self._env = Environment(
            loader=PackageLoader("renderer", "templates"),
            autoescape=select_autoescape(["html"]),
        )

    @property
    def content_type(self) -> str:
        return "text/html; charset=utf-8"

    def render_page(self, content: PageContent) -> str:
        template_name = f"pages/{content.page_type}.html"
        try:
            template = self._env.get_template(template_name)
        except TemplateNotFound:
            # Fall back to generic template when specific one is missing.
            template = self._env.get_template("pages/generic.html")
        return template.render(title=content.title, data=content.data)


class JSONRenderer(ContentRenderer):
    """Renders pages as structured JSON."""

    @property
    def content_type(self) -> str:
        return "application/json"

    def render_page(self, content: PageContent) -> str:
        payload = {
            "title": content.title,
            "page_type": content.page_type,
            "data": content.data,
            "metadata": content.metadata,
        }
        return json.dumps(payload, ensure_ascii=False, indent=2)


class XMLRenderer(ContentRenderer):
    """Renders pages as XML."""

    @property
    def content_type(self) -> str:
        return "application/xml"

    def render_page(self, content: PageContent) -> str:
        root = ET.Element("page")
        ET.SubElement(root, "title").text = content.title
        ET.SubElement(root, "pageType").text = content.page_type

        data_el = ET.SubElement(root, "data")
        self._dict_to_xml(data_el, content.data)

        meta_el = ET.SubElement(root, "metadata")
        self._dict_to_xml(meta_el, content.metadata)

        raw = ET.tostring(root, encoding="unicode")
        return minidom.parseString(raw).toprettyxml(indent="  ")  # noqa: S318

    def _dict_to_xml(self, parent: ET.Element, data: dict[str, object]) -> None:
        for key, value in data.items():
            child = ET.SubElement(parent, str(key))
            if isinstance(value, list):
                for item in value:
                    ET.SubElement(child, "item").text = str(item)
            elif isinstance(value, dict):
                self._dict_to_xml(child, value)
            else:
                child.text = str(value)
