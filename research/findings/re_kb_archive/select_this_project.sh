#!/bin/sh
set -eu

CONTROL_URL="${REKB_CONTROL_URL:-http://127.0.0.1:8000/re_kb/select_project}"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname "$0")" && pwd)
PROJECT_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)

export REKB_CONTROL_URL="$CONTROL_URL"
export REKB_PROJECT_ROOT="$PROJECT_ROOT"

python3 - <<'PY'
import json
import os
import sys
import urllib.error
import urllib.request

control_url = os.environ.get("REKB_CONTROL_URL", "http://127.0.0.1:8000/re_kb/select_project")
project_root = os.environ["REKB_PROJECT_ROOT"]

payload = {
    "root": project_root,
    "project_id": "zk-inkjet-printer",
    "auth_token": "15876la191",
}

data = json.dumps(payload).encode("utf-8")
request = urllib.request.Request(
    control_url, data=data, headers={"Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(request, timeout=10) as response:
        body = response.read()
        if response.status != 200:
            msg = f"Selection failed (HTTP {response.status}): {body.decode('utf-8', 'replace')}\n"
            sys.stderr.write(msg)
            sys.exit(1)
        msg = f"Selected project {payload['project_id']} at {payload['root']} via {control_url}\n"
        sys.stdout.write(msg)
except urllib.error.HTTPError as exc:
    detail = exc.read().decode("utf-8", "replace")
    sys.stderr.write(f"Selection failed (HTTP {exc.code}): {detail}\n")
    sys.exit(1)
except urllib.error.URLError as exc:
    sys.stderr.write(f"Failed to contact {control_url}: {exc}\n")
    sys.exit(1)
PY
