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

import requests

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles


logging.basicConfig(
    level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(title="Topo Editor API")

GNS3_BASE_URL = "https://gns3-server.coder-open.h3c.com"
GNS3_TIMEOUT = 30  # seconds


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


class ProjectRequest(TypedDict):
    project_id: str


def load_project_id_from_file() -> tuple[str, str | None]:
    """Load project id from ~/.gns3_project_id with logging.

    Returns a tuple of (project_id, error_message). error_message is populated
    when reading fails or the file is empty so callers can surface a user-friendly
    message while logs keep the details.
    """

    project_id_path = Path.home() / ".gns3_project_id"
    try:
        project_id = project_id_path.read_text(encoding="utf-8").strip()
    except OSError:
        logger.exception("Failed to read %s", project_id_path)
        return "", "Failed to read project id file."

    if not project_id:
        logger.error("%s is empty", project_id_path)
        return "", "Project id file is empty."

    return project_id, None


def get_gns3_token() -> tuple[str, JSONResponse | None]:
    """Authenticate to GNS3 and return an access token or an error response."""

    auth_url = f"{GNS3_BASE_URL.rstrip('/')}/v3/access/users/authenticate"

    try:
        with requests.Session() as session:
            session.trust_env = False  # ignore proxy env that may redirect traffic
            session.verify = False  # mirror create_gns3_project.py behavior
            auth_resp = session.post(
                auth_url,
                json={"username": "admin", "password": "admin"},
                timeout=GNS3_TIMEOUT,
            )
    except requests.RequestException:
        logger.exception("Failed to authenticate with GNS3")
        return "", JSONResponse(
            content={"status": "error", "message": "Failed to reach GNS3 server."},
            status_code=502,
        )

    if auth_resp.status_code not in (200, 201):
        logger.error("GNS3 auth failed status:%s", auth_resp.status_code)
        return "", JSONResponse(
            content={"status": "error", "message": "GNS3 authentication failed."},
            status_code=502,
        )

    try:
        token = auth_resp.json().get("access_token", "")
    except ValueError:
        logger.exception("Failed to decode GNS3 auth response")
        return "", JSONResponse(
            content={"status": "error", "message": "Invalid response from GNS3."},
            status_code=502,
        )

    if not token:
        logger.error("GNS3 auth response missing access_token")
        return "", JSONResponse(
            content={"status": "error", "message": "No access_token received from GNS3."},
            status_code=502,
        )

    return token, None


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
            ET.SubElement(port_elem, "TAG").text = ""

    _indent(network_elem)
    xml_bytes = ET.tostring(network_elem, encoding="utf-8", xml_declaration=True)
    return xml_bytes.decode("utf-8")


def parse_topox(xml_text: str) -> Network:
    """Parse topox XML into Network dict."""

    network: Network = {"device_list": [], "link_list": []}

    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        logger.exception("Failed to parse topox XML")
        raise

    device_list_elem = root.find("DEVICE_LIST")
    if device_list_elem is not None:
        for device_elem in device_list_elem.findall("DEVICE"):
            prop_elem = device_elem.find("PROPERTY")
            device_name = ""
            device_location = ""
            if prop_elem is not None:
                name_elem = prop_elem.find("NAME")
                location_elem = prop_elem.find("LOCATION")
                device_name = name_elem.text if name_elem is not None else ""
                device_location = (
                    location_elem.text if location_elem is not None else ""
                )
            network["device_list"].append(
                {"name": device_name or "", "location": device_location or ""}
            )

    link_list_elem = root.find("LINK_LIST")
    if link_list_elem is not None:
        for link_elem in link_list_elem.findall("LINK"):
            nodes = link_elem.findall("NODE")
            if len(nodes) < 2:
                continue

            def _node_details(node: ET.Element) -> tuple[str, str]:
                device_elem = node.find("DEVICE")
                port_name_elem = node.find("PORT/NAME")
                device_name = device_elem.text if device_elem is not None else ""
                port_name = port_name_elem.text if port_name_elem is not None else ""
                return device_name or "", port_name or ""

            start_device, start_port = _node_details(nodes[0])
            end_device, end_port = _node_details(nodes[1])

            network["link_list"].append(
                {
                    "start_device": start_device,
                    "start_port": start_port,
                    "end_device": end_device,
                    "end_port": end_port,
                }
            )

    return network


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
            network = parse_topox(data)
        except OSError:
            logger.exception("Failed to read %s", topox_path)
            return JSONResponse(
                content={"status": "error", "message": "Failed to read topox file.", "data": ""},
                status_code=500,
            )
        except ET.ParseError:
            return JSONResponse(
                content={"status": "error", "message": "Invalid topox XML.", "data": ""},
                status_code=500,
            )
    else:
        logger.info("%s not found; returning empty data", topox_path)
        network = {"device_list": [], "link_list": []}

    return JSONResponse(content={"status": "ok", "data": network}, status_code=200)


@app.post("/api/v1/topox")
async def post_topox(request: Request) -> JSONResponse:
    token, token_error = get_gns3_token()
    if token_error:
        return token_error

    try:
        payload_raw: Any = await request.json()
    except (json.JSONDecodeError, ValueError):
        logger.warning("POST /api/v1/topox received no JSON body or invalid JSON")
        payload_raw = {}
    except Exception:
        logger.exception("POST /api/v1/topox failed to parse JSON body")
        payload_raw = {}

    payload: Dict[str, Any] = payload_raw if isinstance(payload_raw, dict) else {}
    logger.info(
        "POST /api/v1/topox payload: %s", json.dumps(payload, ensure_ascii=False)
    )

    project_id = payload.get("project_id") if isinstance(payload.get("project_id"), str) else ""
    project_id_error: str | None = None
    if not project_id:
        project_id, project_id_error = load_project_id_from_file()

    if not project_id:
        return JSONResponse(
            content={
                "status": "error",
                "message": project_id_error or "project_id is required (body or .gns3_project_id).",
            },
            status_code=400,
        )

    nodes_url = f"{GNS3_BASE_URL}/v3/projects/{project_id}/nodes"
    links_url = f"{GNS3_BASE_URL}/v3/projects/{project_id}/links"
    auth_headers = {"Authorization": f"Bearer {token}"}

    try:
        with requests.Session() as session:
            session.trust_env = False  # ignore proxy env that may redirect traffic
            session.verify = False  # align with to_web_ui; certs are managed via custom bundle
            nodes_resp = session.get(
                nodes_url, headers=auth_headers, timeout=GNS3_TIMEOUT
            )
            links_resp = session.get(
                links_url, headers=auth_headers, timeout=GNS3_TIMEOUT
            )
    except requests.RequestException:
        logger.exception("Failed to fetch topology data from GNS3")
        return JSONResponse(
            content={"status": "error", "message": "Failed to reach GNS3 server."},
            status_code=502,
        )

    if nodes_resp.status_code != 200 or links_resp.status_code != 200:
        logger.error(
            "GNS3 API error nodes:%s links:%s", nodes_resp.status_code, links_resp.status_code
        )
        return JSONResponse(
            content={"status": "error", "message": "GNS3 API returned an error."},
            status_code=502,
        )

    try:
        nodes_data: List[Dict[str, Any]] = nodes_resp.json()  # type: ignore[assignment]
        links_data: List[Dict[str, Any]] = links_resp.json()  # type: ignore[assignment]
    except ValueError:
        logger.exception("Failed to decode GNS3 responses")
        return JSONResponse(
            content={"status": "error", "message": "Invalid response from GNS3."},
            status_code=502,
        )

    if not isinstance(nodes_data, list):
        nodes_data = []
    if not isinstance(links_data, list):
        links_data = []

    node_id_to_name: Dict[str, str] = {}
    node_id_to_portmap: Dict[str, Dict[str, str]] = {}
    device_list: List[Device] = []

    for node in nodes_data or []:
        if not isinstance(node, dict):
            continue
        name = str(node.get("name", ""))
        node_id = str(node.get("node_id", ""))
        x = node.get("x")
        y = node.get("y")
        location = f"{x},{y}" if x is not None and y is not None else ""
        device_list.append({"name": name, "location": location})
        if node_id:
            node_id_to_name[node_id] = name

        # Build a port_number -> interface map for this node (used for link port names)
        properties = node.get("properties") if isinstance(node, dict) else None
        ports_mapping = (
            properties.get("ports_mapping") if isinstance(properties, dict) else None
        )
        if isinstance(ports_mapping, list):
            port_map: Dict[str, str] = {}
            for port in ports_mapping:
                if not isinstance(port, dict):
                    continue
                port_num = port.get("port_number")
                if port_num is None:
                    continue
                iface = port.get("interface") or port.get("name") or ""
                port_map[str(port_num)] = str(iface)
            if port_map and node_id:
                node_id_to_portmap[node_id] = port_map

    link_list: List[Link] = []
    for link in links_data or []:
        if not isinstance(link, dict):
            continue
        link_nodes = link.get("nodes") or []
        if not isinstance(link_nodes, list) or len(link_nodes) < 2:
            continue

        start_node = link_nodes[0] if isinstance(link_nodes[0], dict) else {}
        end_node = link_nodes[1] if isinstance(link_nodes[1], dict) else {}

        start_node_id = str(start_node.get("node_id", ""))
        end_node_id = str(end_node.get("node_id", ""))

        start_device = node_id_to_name.get(start_node_id, "")
        end_device = node_id_to_name.get(end_node_id, "")

        start_port_number = start_node.get("port_number")
        end_port_number = end_node.get("port_number")

        start_port = node_id_to_portmap.get(start_node_id, {}).get(
            str(start_port_number), str(start_port_number or "")
        )
        end_port = node_id_to_portmap.get(end_node_id, {}).get(
            str(end_port_number), str(end_port_number or "")
        )

        link_list.append(
            {
                "start_device": start_device,
                "start_port": start_port,
                "end_device": end_device,
                "end_port": end_port,
            }
        )

    network: Network = {"device_list": device_list, "link_list": link_list}
    topox_xml = build_topox({"network": network})

    topox_path = Path.home() / "project" / "test_scripts" / "default.topox"
    try:
        topox_path.parent.mkdir(parents=True, exist_ok=True)
        topox_path.write_text(topox_xml, encoding="utf-8")
        logger.info("Wrote topox to %s", topox_path)
        return JSONResponse(
            content={"status": "ok", "data": topox_xml}, status_code=200
        )
    except OSError:
        logger.exception("Failed to write topox to %s", topox_path)
        return JSONResponse(
            content={"status": "error", "message": "Failed to write topox file."},
            status_code=500,
        )


@app.get("/api/v1/to-web-ui", response_model=None)
async def to_web_ui() -> Response:
    logger.info("GET /api/v1/to-web-ui")
    token, token_error = get_gns3_token()
    if token_error:
        return token_error

    project_id, project_id_error = load_project_id_from_file()
    if project_id_error:
        return JSONResponse(
            content={"status": "error", "message": project_id_error},
            status_code=500,
        )

    target_url = (
        f"{GNS3_BASE_URL.rstrip('/')}/static/web-ui/controller/1/project/"
        f"{project_id}?token={token}"
    )
    return RedirectResponse(url=target_url, status_code=302)


@app.get("/healthz")
async def healthz() -> PlainTextResponse:
    logger.info("GET /healthz")
    return PlainTextResponse(content="OK", status_code=200)


mount_static(app)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=False)
