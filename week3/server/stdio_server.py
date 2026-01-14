#!/usr/bin/env python3
import json
import sys
from typing import Any, Dict

import mcp_core


def run_stdio() -> None:
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            response = mcp_core.json_rpc_error(-32700, "Parse error", None)
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            continue

        if not isinstance(request, dict):
            response: Dict[str, Any] = mcp_core.json_rpc_error(-32600, "Invalid Request", None)
        else:
            response = mcp_core.process_request(request)

        if response is not None and request.get("id") is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


def main() -> None:
    run_stdio()


if __name__ == "__main__":
    main()
