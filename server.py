from fastapi import FastAPI, Request
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider
import os

app = FastAPI()

# 🔐 Composio init (Render env)
composio = Composio(
    api_key=os.environ["COMPOSIO_API_KEY"],
    provider=OpenAIAgentsProvider()
)


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

    # =========================================================
    # 1. INITIALIZE (REQUIRED BY AZURE MCP)
    # =========================================================
    if method == "initialize":
        response["result"] = {
            "protocolVersion": "2025-11-25",
            "capabilities": {
                "tools": {}
            }
        }
        return response

    # =========================================================
    # 2. TOOLS LIST (AZURE SAFE FORMAT)
    # =========================================================
    elif method == "tools/list":
        try:
            session = composio.create(user_id="azure_user")
            tools = session.tools()

            mcp_tools = []

            for t in tools:
                name = t.get("name")

                # 🔥 IMPORTANT: Azure-safe schema (prevents silent rejection)
                mcp_tools.append({
                    "name": name,
                    "description": t.get("description", "No description"),
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "input": {
                                "type": "object",
                                "description": "Tool input parameters"
                            }
                        },
                        "required": []
                    }
                })

            print(f"TOOLS SENT TO AZURE: {len(mcp_tools)}")

            response["result"] = {
                "tools": mcp_tools
            }

        except Exception as e:
            print("TOOLS LIST ERROR:", str(e))
            response["error"] = {
                "code": -32000,
                "message": str(e)
            }

        return response

    # =========================================================
    # 3. TOOL EXECUTION (DYNAMIC - NO HARDCODING)
    # =========================================================
    elif method == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        print("TOOL CALL:", tool_name)
        print("ARGS:", arguments)

        session = composio.create(user_id="azure_user")

        try:
            # 🔥 FIX: correct Composio call format
            result = session.execute(
                tool_name,
                arguments
            )

            response["result"] = {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            }

        except Exception as e:
            print("EXECUTION ERROR:", str(e))

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
