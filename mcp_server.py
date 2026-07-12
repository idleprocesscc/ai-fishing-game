#!/usr/bin/env python3
"""Dependency-free stdio MCP adapter for World Waters Field Journal."""
import json
import sys

import engine


SCHEMA = json.load(open(__file__.replace("mcp_server.py", "tool-schema.json"), encoding="utf-8"))


def _command(args):
    action = args.get("action", "status")
    if action == "language":
        return "language " + args.get("language", "zh")
    if action == "cast":
        parts = ["cast"]
        if args.get("bait_id"):
            parts.append(args["bait_id"])
        if args.get("times"):
            parts.append(str(int(args["times"])))
        if args.get("stop_on"):
            parts.append("stop=" + ",".join(args["stop_on"]))
        return " ".join(parts)
    if action == "buy":
        return "buy %s %d" % (args.get("bait_id", ""), int(args.get("qty", 1)))
    if action == "goto":
        return "goto" + ((" " + args["location_id"]) if args.get("location_id") else "")
    if action == "sell":
        return "sell " + args.get("target", "")
    if action == "identify":
        command = "identify " + args.get("fish_id", "")
        return command + ((" " + str(int(args["choice"]))) if args.get("choice") else "")
    if action in ("look", "threads"):
        return action + ((" " + args["id"]) if args.get("id") else "")
    if action == "connect":
        return "connect %s %s %s" % (args.get("from_id", ""), args.get("relation_type", "link"), args.get("to_id", ""))
    if action == "batch":
        return ";".join(_command(step) for step in args.get("steps", []))
    return action


def _reply(message):
    request_id = message.get("id")
    method = message.get("method")
    if method == "initialize":
        result = {"protocolVersion": "2025-06-18", "capabilities": {"tools": {}},
                  "serverInfo": {"name": "world-waters", "version": "3.0.0"}}
    elif method == "tools/list":
        result = {"tools": [{"name": SCHEMA["name"], "description": SCHEMA["description"],
                              "inputSchema": SCHEMA["parameters"]}]}
    elif method == "tools/call":
        params = message.get("params", {})
        if params.get("name") != SCHEMA["name"]:
            return {"jsonrpc": "2.0", "id": request_id,
                    "error": {"code": -32602, "message": "Unknown tool"}}
        try:
            result = {"content": [{"type": "text", "text": engine.cmd(_command(params.get("arguments", {})))}]}
        except Exception as exc:
            result = {"content": [{"type": "text", "text": "World Waters error: %s" % exc}], "isError": True}
    else:
        if request_id is None:
            return None
        return {"jsonrpc": "2.0", "id": request_id,
                "error": {"code": -32601, "message": "Method not found"}}
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def main():
    for line in sys.stdin:
        try:
            response = _reply(json.loads(line))
            if response is not None:
                print(json.dumps(response, ensure_ascii=False), flush=True)
        except Exception as exc:
            print(json.dumps({"jsonrpc": "2.0", "id": None,
                              "error": {"code": -32700, "message": str(exc)}}), flush=True)


if __name__ == "__main__":
    main()
