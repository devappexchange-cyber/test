from fastapi import FastAPI, Request
import json
import time

app = FastAPI()


@app.post("/mcp")
async def mcp(request: Request):

    start = time.time()

    body = await request.json()

    print("\n================ MCP REQUEST ================\n")
    print(json.dumps(body, indent=2))
    print("\n=============================================\n")

    method = body.get("method")

    response = {
        "jsonrpc": "2.0",
        "id": body.get("id")
    }

    # TOOL LIST
    if method == "tools/list":
        response["result"] = {
            "tools": [
                {
                    "name": "demo_tool",
                    "description": "A test tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task": {"type": "string"}
                        }
                    }
                }
            ]
        }

    # TOOL CALL
    elif method == "tools/call":
        params = body.get("params", {})
        args = params.get("arguments", {})

        response["result"] = {
            "content": [
                {
                    "type": "text",
                    "text": f"Executed task: {args}"
                }
            ]
        }

    else:
        response["error"] = {
            "message": f"Unknown method: {method}"
        }

    print("Response time:", time.time() - start)

    return response
