from fastapi import FastAPI, HTTPException
from typing import Any
from pydantic import BaseModel
from .env import PromptDebuggerEnv
from .models import PromptDebuggerAction, PromptDebuggerState

app = FastAPI(title="Prompt Debugger Env")
env = PromptDebuggerEnv()

class ResetRequest(BaseModel):
    task_name: str = "fix-output-format"

@app.post("/reset")
async def reset(req: ResetRequest):
    return await env.reset(req.task_name)

@app.post("/step")
async def step(action: PromptDebuggerAction):
    try:
        return await env.step(action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/state")
async def state():
    st = await env.state()
    if not st:
        raise HTTPException(status_code=400, detail="Not initialized")
    return st

@app.get("/health")
async def health():
    return {"status": "ok"}
