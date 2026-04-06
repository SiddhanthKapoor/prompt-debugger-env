from fastapi import FastAPI, HTTPException
from typing import Any, Optional
from pydantic import BaseModel
from prompt_debugger_env.env import PromptDebuggerEnv
from prompt_debugger_env.models import PromptDebuggerAction, PromptDebuggerState

app = FastAPI(title="Prompt Debugger Env")
env = PromptDebuggerEnv()

class ResetRequest(BaseModel):
    task_name: Optional[str] = "fix-output-format"

@app.get("/")
async def root():
    return {
        "app": "Prompt Debugger Env",
        "message": "Welcome! The environment is running.",
        "description": "An OpenEnv environment for debugging and repairing LLM system prompts.",
        "endpoints": ["/reset (POST)", "/step (POST)", "/state (GET)", "/health (GET)", "/debug (GET)"]
    }

@app.post("/reset")
async def reset(request: Optional[ResetRequest] = None):
    task = request.task_name if request else "fix-output-format"
    result = await env.reset(task)
    return result

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

@app.get("/debug")
async def debug():
    import os
    return {
        "HF_TOKEN_set": bool(os.getenv("HF_TOKEN")),
        "API_BASE_URL": os.getenv("API_BASE_URL"),
        "MODEL_NAME": os.getenv("MODEL_NAME")
    }
