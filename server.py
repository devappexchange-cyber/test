from fastapi import FastAPI, Request
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider
import os

app = FastAPI()

# Initialize Composio
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

    # ✅ 1. Initialize
    if method == "initialize":
        response["result"] = {
            "protocolVersion": "2025-11-25",
            "capabilities": {
                "tools": {}
            }
        }
        return response

    # ✅ 2. List tools (from Composio)
    elif method == "tools/list":
        session = composio.create(user_id="azure_user")

        tools = session.tools()

        mcp_tools = []

        for t in tools:
            mcp_tools.append({
                "name": t.get("name"),
                "description": t.get("description", ""),
                "inputSchema": t.get("input_schema", {
                    "type": "object",
                    "properties": {}
                })
            })

        print("TOOLS SENT TO AZURE:", mcp_tools)

        response["result"] = {
            "tools": mcp_tools
        }
        return response

    # ✅ 3. Call tool (🔥 FIXED HERE)
    elif method == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        print("TOOL CALL:", tool_name)
        print("ARGUMENTS:", arguments)

        session = composio.create(user_id="azure_user")

        try:
            # 🔥 IMPORTANT FIX: pass STRING, not object
            result = session.execute(
                tool_name,
                arguments
            )

            print("TOOL RESULT:", result)

            response["result"] = {
                "content": [
                    {
                        "type": "text",
                        "text": str(result)
                    }
                ]
            }

        except Exception as e:
            print("ERROR:", str(e))

            response["error"] = {
                "code": -32000,
                "message": str(e)
            }

        return response

    # ❌ Unknown method
    response["error"] = {
        "code": -32601,
        "message": f"Unknown method: {method}"
    }
    return response
