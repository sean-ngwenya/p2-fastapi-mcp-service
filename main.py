import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pydantic_ai import Agent
from pydantic_ai.capabilities.mcp import MCP

load_dotenv()


class ClassifyRequest(BaseModel):
    message: str


class ClassifyResponse(BaseModel):
    request_type: str
    parameters: dict
    confidence: float


class ExecuteRequest(BaseModel):
    message: str


class ExecuteResponse(BaseModel):
    result: str
    tool_used: str


classify_agent = Agent(
    "openai:gpt-4o-mini",
    output_type=ClassifyResponse,
    system_prompt=(
        "You are a message classifier. Given a user message, classify it as one of: "
        "'file_read' (if the user wants to read a file), "
        "'calculation' (if the user wants to perform a math calculation), "
        "or 'unknown' (if it doesn't fit either category). "
        "For 'file_read', set parameters to {'path': '<the file path>'}. "
        "For 'calculation', set parameters to "
        "{'a': <number>, 'b': <number>, 'operation': '<add|subtract|multiply|divide>'}. "
        "Set confidence as a float between 0 and 1."
    ),
)

execute_agent = Agent(
    "openai:gpt-4o-mini",
    capabilities=[MCP("http://127.0.0.1:8001/sse")],
    output_type=ExecuteResponse,
    system_prompt=(
        "You have access to two tools: read_file (reads a local text file) "
        "and calculate (performs add/subtract/multiply/divide). "
        "Use the appropriate tool to fulfill the user's request. "
        "Return the result and the name of the tool you used."
    ),
)

app = FastAPI(title="Client Agent Service")
router = APIRouter(prefix="/client-agent")


@router.post("/classify")
async def classify(req: ClassifyRequest):
    result = await classify_agent.run(req.message)
    return result.output


@router.post("/execute")
async def execute(req: ExecuteRequest):
    try:
        async with httpx.AsyncClient() as client:
            await client.get("http://127.0.0.1:8001/", timeout=2)
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503, detail={"error": "mcp_server_unreachable"}
        )
    result = await execute_agent.run(req.message)
    return result.output


@router.get("/health")
async def health():
    return {"status": "ok", "service": "client-agent"}


app.include_router(router)


@app.exception_handler(httpx.ConnectError)
async def mcp_connect_error(request, exc):
    return JSONResponse(
        status_code=503,
        content={"error": "mcp_server_unreachable"},
    )


@app.exception_handler(RuntimeError)
async def mcp_runtime_error(request, exc):
    if "Client failed to connect" in str(exc):
        return JSONResponse(
            status_code=503,
            content={"error": "mcp_server_unreachable"},
        )
    raise exc
