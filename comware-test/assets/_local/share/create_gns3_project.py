#!/usr/bin/env python3
import argparse
import json
import os
import ssl
import sys
import urllib.error
import urllib.request
from typing import Tuple


def disable_proxies() -> None:
    for key in [
        "http_proxy",
        "https_proxy",
        "ftp_proxy",
        "all_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "FTP_PROXY",
        "ALL_PROXY",
        "NO_PROXY",
    ]:
        os.environ.pop(key, None)


def request_json(url: str, data: dict, headers: dict, timeout: int) -> Tuple[int, str]:
    payload = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url=url, data=payload, headers=headers, method="POST")
    ctx = ssl._create_unverified_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            status = resp.getcode()
            body = resp.read().decode("utf-8", errors="replace")
            return status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return e.code, body
    except Exception as e:
        return -1, str(e)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create GNS3 project and store project_id")
    parser.add_argument("--base-url", default="https://gns3-server.coder-open.h3c.com", help="GNS3 API base URL")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin")
    parser.add_argument("--project-name", required=True)
    parser.add_argument("--project-id-file", required=True)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    disable_proxies()

    auth_url = f"{args.base_url.rstrip('/')}/v3/access/users/authenticate"
    status, body = request_json(
        auth_url,
        {"username": args.username, "password": args.password},
        {"Content-Type": "application/json"},
        timeout=args.timeout,
    )

    if status not in (200, 201):
        sys.stderr.write(f"Auth failed (status {status}): {body}\n")
        return 1

    try:
        token = json.loads(body).get("access_token", "")
    except Exception as e:
        sys.stderr.write(f"Auth response parse error: {e}\nBody: {body}\n")
        return 1

    if not token:
        sys.stderr.write("No access_token in auth response\n")
        return 1

    projects_url = f"{args.base_url.rstrip('/')}/v3/projects"
    status, body = request_json(
        projects_url,
        {"name": args.project_name},
        {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        timeout=args.timeout,
    )

    if status not in (200, 201):
        sys.stderr.write(f"Create project failed (status {status}): {body}\n")
        return 1

    try:
        data = json.loads(body)
        project_id = data.get("project_id") or data.get("project_uuid") or data.get("id")
    except Exception as e:
        sys.stderr.write(f"Project response parse error: {e}\nBody: {body}\n")
        return 1

    if not project_id:
        sys.stderr.write("Project created but no project_id found in response\n")
        return 1

    try:
        with open(args.project_id_file, "w", encoding="utf-8") as f:
            f.write(str(project_id))
    except Exception as e:
        sys.stderr.write(f"Failed to write project_id file: {e}\n")
        return 1

    print(f"GNS3 project created with id: {project_id}")
    print(f"Stored project_id at {args.project_id_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
