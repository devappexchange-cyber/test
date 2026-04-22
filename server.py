from fastapi import FastAPI
from pydantic import BaseModel
from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider

app = FastAPI()

composio = Composio(provider=OpenAIAgentsProvider())


class MCPRequest(BaseModel):
    user_id: str = "azure_user"
    task: str


@app.post("/mcp")
def mcp(req: MCPRequest):
    session = composio.create(user_id=req.user_id)
    result = session.execute(req.task)

    return {
        "result": result
    }
