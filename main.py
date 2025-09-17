#!/usr/bin/env python3
import base64
import json
import urllib.parse as urlparse
import xml.etree.ElementTree as ET
import os
import sys
import re
from pathlib import Path


def ensure_folder(items_list, folder_path):
    """Return the 'item' list of the deepest folder in folder_path, creating folders as needed."""
    for folder_name in folder_path:
        found = None
        for it in items_list:
            if it.get("name") == folder_name and "item" in it and "request" not in it:
                found = it
                break
        if not found:
            found = {"name": folder_name, "item": []}
            items_list.append(found)
        items_list = found["item"]
    return items_list


def looks_like_base64(s):
    """Rudimentary check if a string is base64-like (no braces, only base64 alphabet)."""
    if not s or len(s) % 4 != 0:
        return False
    return re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", s) is not None


def parse_raw_request(b64text, is_base64_encoded=False):
    """
    Parse a raw HTTP request blob and return (body, headers_list).
    - Accepts raw text or base64-encoded text (controlled by is_base64_encoded).
    - Splits headers and body robustly (handles \r\n, \n).
    - If the blob begins with JSON ('{') we treat it as body-only.
    """
    if b64text is None:
        return "", []

    raw = b64text
    # decode if explicitly marked base64
    if is_base64_encoded:
        try:
            raw = base64.b64decode(b64text).decode("utf-8", errors="ignore")
        except Exception:
            # fall back to using as-is if decode fails
            raw = b64text
    else:
        # if it *looks* like base64 and contains no HTTP-like chars, try decode (best-effort)
        # but avoid decoding actual JSON or HTTP text.
        snippet = b64text.strip()[:200]
        if looks_like_base64(snippet):
            try:
                decoded = base64.b64decode(b64text).decode("utf-8", errors="ignore")
                # only accept decoded if it contains typical HTTP markers or JSON start
                if (
                    "\n" in decoded
                    or decoded.lstrip().startswith("{")
                    or "HTTP/" in decoded
                ):
                    raw = decoded
            except Exception:
                pass

    raw = raw.replace("\r\n", "\n")  # normalize
    raw = raw.lstrip("\n")  # remove leading blank lines

    # If the raw starts with JSON or XML body directly, return it as body
    if (
        raw.lstrip().startswith("{")
        or raw.lstrip().startswith("[")
        or raw.lstrip().startswith("<")
    ):
        body = raw
        return body, []

    # Split header and body on the first blank line (handles \n\n)
    parts = re.split(r"\n\s*\n", raw, maxsplit=1)
    if len(parts) == 1:
        header_blob = parts[0]
        body = ""
    else:
        header_blob, body = parts[0], parts[1]

    # Parse header lines
    header_lines = header_blob.splitlines()
    headers = []
    # skip the request/status line if present (first line like "POST /... HTTP/1.1" or "OPTIONS ...")
    start_index = (
        1
        if header_lines and re.search(r"^[A-Z]+\s+\/|\s+HTTP\/", header_lines[0])
        else 0
    )
    for line in header_lines[start_index:]:
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            # skip some noisey headers
            if k.lower() in ("host", "content-length", "connection"):
                continue
            headers.append({"key": k, "value": v})
    return body, headers


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file> [output_file]")
        print(
            "Example: python main.py ./burpsuite-file/burpsuite-file.xml ./output/burp_to_postman_nested_collection.json"
        )
        sys.exit(1)

    src = sys.argv[1]
    dst = (
        sys.argv[2]
        if len(sys.argv) > 2
        else "./output/burp_to_postman_nested_collection.json"
    )

    if not os.path.isfile(src):
        print(f"Error: Input file '{src}' not found.")
        sys.exit(1)

    try:
        tree = ET.parse(src)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML file: {str(e)}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

    collection = {
        "info": {
            "name": f"PostmanCollection > Burp - {Path(src).name}",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": [],
    }

    for item in root.findall("item"):
        method = (item.findtext("method") or "GET").strip()
        raw_url = (item.findtext("url") or "").strip()
        if not raw_url:
            continue
        req_node = item.find("request")
        body_raw, headers = ("", [])
        if req_node is not None and (req_node.text or "").strip():
            is_b64 = (req_node.get("base64") or "").lower() == "true"
            body_raw, headers = parse_raw_request(
                req_node.text, is_base64_encoded=is_b64
            )
            # trim trailing nulls or unexpected characters
            if isinstance(body_raw, str):
                body_raw = body_raw.strip()
                if body_raw == "{}":
                    body_raw = ""

        parts = urlparse.urlsplit(raw_url)
        protocol = parts.scheme or item.findtext("protocol") or "https"
        host = parts.hostname or (item.findtext("host") or "").strip()
        port = parts.port
        path_segments = [seg for seg in parts.path.split("/") if seg]
        query = [
            {"key": k, "value": v}
            for k, v in urlparse.parse_qsl(parts.query, keep_blank_values=True)
        ]
        pm_url = {
            "raw": raw_url,
            "protocol": protocol,
            "host": host.split(".") if host else [],
            "path": path_segments,
        }
        if port and (
            (protocol == "http" and port != 80)
            or (protocol == "https" and port != 443)
            or (protocol not in ("http", "https"))
        ):
            pm_url["port"] = str(port)
        if query:
            pm_url["query"] = query
        folder_path = [host] + path_segments[:-1] if path_segments else [host]
        target_list = ensure_folder(collection["item"], folder_path)
        last_seg = path_segments[-1] if path_segments else "/"
        name = f"{last_seg}"
        pm_request = {
            "name": name,
            "request": {"method": method, "header": headers, "url": pm_url},
        }
        if body_raw:
            pm_request["request"]["body"] = {"mode": "raw", "raw": body_raw}
        target_list.append(pm_request)

    try:
        output_dir = os.path.dirname(dst)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        print(f"Successfully converted and saved to {os.path.abspath(dst)}")
    except Exception as e:
        print(f"Error saving output file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
