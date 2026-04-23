from fastapi import FastAPI, Request

app = FastAPI()


@app.post("/mcp")
async def mcp(request: Request):
    body = await request.json()

    print("\n=== MCP REQUEST ===")
    print(body)

    method = body.get("method")
    request_id = body.get("id")

    response = {
        "jsonrpc": "2.0",
        "id": request_id
    }

    # ✅ REQUIRED: initialize
    if method == "initialize":
        response["result"] = {
            "protocolVersion": "2025-11-25",
            "capabilities": {
                "tools": {}
            }
        }
        return response

    # ✅ REQUIRED: tools/list
    elif method == "tools/list":
        response["result"] = {
            "tools": [
                {
                    "name": "demo_tool",
                    "description": "Test tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string"}
                        },
                        "required": ["task"]
                    }
                }
            ]
        }
        return response

    # ✅ REQUIRED: tools/call
    elif method == "tools/call":
        params = body.get("params", {})
        args = params.get("arguments", {})

        response["result"] = {
            "content": [
                {
                    "type": "text",
                    "text": f"Executed: {args}"
                }
            ]
        }
        return response

    # ❌ fallback
    response["error"] = {
        "code": -32601,
        "message": f"Unknown method: {method}"
    }
    return response
