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


def request_delete(url: str, headers: dict, timeout: int) -> Tuple[int, str]:
    req = urllib.request.Request(url=url, data=None, headers=headers, method="DELETE")
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
    parser = argparse.ArgumentParser(description="Delete GNS3 project by project_id")
    parser.add_argument("--base-url", default="https://gns3-server.coder-open.h3c.com", help="GNS3 API base URL")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin")
    parser.add_argument("--project-id-file", required=True)
    parser.add_argument("--timeout", type=int, default=30)
    args = parser.parse_args()

    disable_proxies()

    if not os.path.isfile(args.project_id_file):
        print("project_id file not found; skipping", file=sys.stderr)
        return 0

    project_id = open(args.project_id_file, encoding="utf-8").read().strip()
    if not project_id:
        print("project_id file empty; skipping", file=sys.stderr)
        return 0

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

    delete_url = f"{args.base_url.rstrip('/')}/v3/projects/{project_id}"
    status, body = request_delete(
        delete_url,
        {"Authorization": f"Bearer {token}"},
        timeout=args.timeout,
    )

    if status in (200, 204, 404):
        try:
            os.remove(args.project_id_file)
        except Exception:
            pass
        if status == 404:
            print(f"GNS3 project {project_id} not found (already deleted?)")
        else:
            print(f"GNS3 project {project_id} deleted")
        return 0

    sys.stderr.write(f"Delete project failed (status {status}): {body}\n")
    return 1


if __name__ == "__main__":
    sys.exit(main())
