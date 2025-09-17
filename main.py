import base64
import json
import urllib.parse as urlparse
import xml.etree.ElementTree as ET
import os
import sys
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

def parse_raw_request(b64text):
    if not b64text:
        return "", []
    raw = base64.b64decode(b64text).decode(errors="ignore")
    if "\r\n\r\n" in raw:
        header_blob, body = raw.split("\r\n\r\n", 1)
    else:
        header_blob, body = raw, ""
    header_lines = header_blob.split("\r\n")
    headers = []
    for line in header_lines[1:]:
        if ":" in line:
            k, v = line.split(":", 1)
            k = k.strip()
            v = v.strip()
            if k.lower() in ("host", "content-length", "connection"):
                continue
            headers.append({"key": k, "value": v})
    return body, headers

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_file> [output_file]")
        print("Example: python main.py ./burpsuite-file/burpsuite-file.xml ./output/burp_to_postman_nested_collection.json")
        sys.exit(1)

    src = sys.argv[1]
    dst = sys.argv[2] if len(sys.argv) > 2 else "./output/burp_to_postman_nested_collection.json"

    if not os.path.isfile(src):
        print(f"Error: Input file '{src}' not found.")
        print("Please make sure:")
        print(f"1. The file exists at {os.path.abspath(src)}")
        print("2. The file has the correct extension (.xml)")
        print("3. The file was exported from Burp Suite with Base64 encoding disabled")
        sys.exit(1)

    try:
        tree = ET.parse(src)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML file: {str(e)}")
        print("Please make sure the file is a valid XML export from Burp Suite")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        sys.exit(1)

    collection = {
        "info": {
            "name": f"Burp Export - {Path(src).stem}",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
        },
        "item": []
    }

    for item in root.findall("item"):
        method = (item.findtext("method") or "GET").strip()
        raw_url = (item.findtext("url") or "").strip()
        if not raw_url:
            continue
        req_node = item.find("request")
        body_raw, headers = ("", [])
        if req_node is not None and (req_node.text or "").strip():
            body_raw, headers = parse_raw_request(req_node.text)
        parts = urlparse.urlsplit(raw_url)
        protocol = parts.scheme or item.findtext("protocol") or "https"
        host = parts.hostname or item.findtext("host") or ""
        port = parts.port
        path_segments = [seg for seg in parts.path.split("/") if seg]
        query = [{"key": k, "value": v} for k, v in urlparse.parse_qsl(parts.query, keep_blank_values=True)]
        pm_url = {
            "raw": raw_url,
            "protocol": protocol,
            "host": host.split(".") if host else [],
            "path": path_segments
        }
        if port and ((protocol == "http" and port != 80) or (protocol == "https" and port != 443) or (protocol not in ("http","https"))):
            pm_url["port"] = str(port)
        if query:
            pm_url["query"] = query
        folder_path = [host] + path_segments[:-1] if path_segments else [host]
        target_list = ensure_folder(collection["item"], folder_path)
        last_seg = path_segments[-1] if path_segments else "/"
        name = f"{method} {last_seg}"
        pm_request = {
            "name": name,
            "request": {
                "method": method,
                "header": headers,
                "url": pm_url
            }
        }
        if body_raw:
            pm_request["request"]["body"] = {"mode": "raw", "raw": body_raw}
        target_list.append(pm_request)

    try:
        output_dir = os.path.dirname(dst)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        with open(dst, "w", encoding="utf-8") as f:
            json.dump(collection, f, indent=2, ensure_ascii=False)
        print(f"Successfully converted and saved to {os.path.abspath(dst)}")
    except Exception as e:
        print(f"Error saving output file: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
