"""FastAPI entrypoint for topo editor.

Exposes an API at /api/v1/topox and serves static assets from the sibling
public/ directory.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, TypedDict
import xml.etree.ElementTree as ET

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles


logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Topo Editor API")


class Device(TypedDict):
    name: str
    location: str


class Link(TypedDict):
    start_device: str
    start_port: str
    end_device: str
    end_port: str


class Network(TypedDict):
    device_list: List[Device]
    link_list: List[Link]


class RequestBody(TypedDict):
    network: Network


def _indent(elem: ET.Element, level: int = 0) -> None:
    """Pretty-print XML by indenting in-place."""

    indent_str = "  "
    i = "\n" + level * indent_str
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + indent_str
        for child in elem:
            _indent(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def build_topox(payload: RequestBody) -> str:
    """Convert request payload to topox XML string."""

    network_elem = ET.Element("NETWORK")

    network_section = payload.get("network", {})
    device_list = []
    link_list = []

    if isinstance(network_section, dict):
        device_list = network_section.get("device_list", []) or []
        link_list = network_section.get("link_list", []) or []

    device_list_elem = ET.SubElement(network_elem, "DEVICE_LIST")
    for device in device_list:
        device_elem = ET.SubElement(device_list_elem, "DEVICE")
        prop_elem = ET.SubElement(device_elem, "PROPERTY")
        ET.SubElement(prop_elem, "NAME").text = device.get("name", "")
        ET.SubElement(prop_elem, "TYPE").text = "Simware9"
        ET.SubElement(prop_elem, "ENABLE").text = "TRUE"
        ET.SubElement(prop_elem, "IS_DOUBLE_MCU").text = "FALSE"
        ET.SubElement(prop_elem, "IS_SINGLE_MCU").text = "FALSE"
        ET.SubElement(prop_elem, "IS_SAME_DUT_TYPE").text = "FALSE"
        ET.SubElement(prop_elem, "MAP_PRIORITY").text = "0"
        ET.SubElement(prop_elem, "IS_DUT").text = "true"
        ET.SubElement(prop_elem, "LOCATION").text = device.get("location", "")

    link_list_elem = ET.SubElement(network_elem, "LINK_LIST")
    for link in link_list:
        link_elem = ET.SubElement(link_list_elem, "LINK")
        start_device = link.get("start_device", "")
        end_device = link.get("end_device", "")
        start_port = link.get("start_port", "")
        end_port = link.get("end_port", "")
        for device_name, port_name in (
            (start_device, start_port),
            (end_device, end_port),
        ):
            node_elem = ET.SubElement(link_elem, "NODE")
            ET.SubElement(node_elem, "DEVICE").text = device_name
            port_elem = ET.SubElement(node_elem, "PORT")
            ET.SubElement(port_elem, "NAME").text = port_name
            ET.SubElement(port_elem, "TYPE").text = ""
            ET.SubElement(port_elem, "IPAddr").text = ""
            ET.SubElement(port_elem, "IPv6Addr").text = ""
            ET.SubElement(port_elem, "SLOT_TYPE").text = ""

    _indent(network_elem)
    xml_bytes = ET.tostring(network_elem, encoding="utf-8", xml_declaration=True)
    return xml_bytes.decode("utf-8")


def mount_static(app: FastAPI) -> None:
    """Mount the static files directory if it exists."""

    public_dir = Path(__file__).parent / "public"
    if not public_dir.exists():
        logger.warning(
            "Public directory %s not found; static files will not be served.",
            public_dir,
        )
        return

    app.mount("/", StaticFiles(directory=str(public_dir), html=True), name="public")
    logger.info("Serving static files from %s", public_dir)


@app.get("/api/v1/topox")
async def get_topox() -> JSONResponse:
    logger.info("GET /api/v1/topox received")
    topox_path = Path.home() / "project" / "test_scripts" / "default.topox"

    if topox_path.exists():
        try:
            data = topox_path.read_text(encoding="utf-8")
        except OSError:
            logger.exception("Failed to read %s", topox_path)
            data = ""
    else:
        logger.info("%s not found; returning empty data", topox_path)
        data = ""

    return JSONResponse(content={"status": "ok", "data": data}, status_code=200)


@app.post("/api/v1/topox")
async def post_topox(request: Request) -> JSONResponse:
    payload: RequestBody = await request.json()
    logger.info(
        "POST /api/v1/topox payload: %s", json.dumps(payload, ensure_ascii=False)
    )
    topox_xml = build_topox(payload)
    return JSONResponse(content={"status": "ok", "data": topox_xml}, status_code=200)


@app.get("/healthz")
async def healthz() -> PlainTextResponse:
    logger.info("GET /healthz")
    return PlainTextResponse(content="OK", status_code=200)


mount_static(app)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=False)
