from fastapi import FastAPI, Request
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider
import os
import json

app = FastAPI()

composio = Composio(
    api_key=os.environ["COMPOSIO_API_KEY"],
    provider=OpenAIAgentsProvider()
)


def log(title, data):
    print(f"\n===== {title} =====")
    print(json.dumps(data, indent=2, default=str))
    print("====================\n")


@app.post("/mcp")
async def mcp(request: Request):
    body = await request.json()

    log("INCOMING MCP REQUEST", body)

    method = body.get("method")
    request_id = body.get("id")

    response = {
        "jsonrpc": "2.0",
        "id": request_id
    }

    # =========================================================
    # INIT
    # =========================================================
    if method == "initialize":
        response["result"] = {
            "protocolVersion": "2025-11-25",
            "capabilities": {"tools": {}}
        }

        log("INITIALIZE RESPONSE", response)
        return response

    # =========================================================
    # TOOLS LIST DEBUG (MOST IMPORTANT STEP)
    # =========================================================
    elif method == "tools/list":
        session = composio.create(user_id="azure_user")

        tools = session.tools()

        log("RAW COMPOSIO TOOLS", tools)

        mcp_tools = []

        for t in tools:
            mcp_tools.append({
                "name": t.get("name"),
                "description": t.get("description", ""),
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "limit": {"type": "number"}
                    }
                }
            })

        log("TOOLS SENT TO AZURE", mcp_tools)

        response["result"] = {"tools": mcp_tools}

        return response

    # =========================================================
    # TOOL CALL DEBUG (CRITICAL)
    # =========================================================
    elif method == "tools/call":
        params = body.get("params", {})

        log("TOOL CALL RECEIVED FROM AZURE", params)

        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        log("EXTRACTED TOOL NAME", tool_name)
        log("EXTRACTED ARGUMENTS", arguments)

        session = composio.create(user_id="azure_user")

        try:
            result = session.execute(tool_name, arguments)

            log("COMPOSIO RESULT", result)

            response["result"] = {
                "content": [{
                    "type": "text",
                    "text": str(result)
                }]
            }

        except Exception as e:
            log("EXECUTION ERROR", str(e))

            response["error"] = {
                "code": -32000,
                "message": str(e)
            }

        return response

    # =========================================================
    # UNKNOWN METHOD
    # =========================================================
    response["error"] = {
        "code": -32601,
        "message": f"Unknown method: {method}"
    }

    return response
