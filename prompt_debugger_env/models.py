from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class PromptDebuggerAction(BaseModel):
    fixed_prompt: str

class TestCase(BaseModel):
    user_input: str
    expected_behavior: str
    expected_format: Optional[str] = None

class PromptDebuggerObservation(BaseModel):
    broken_prompt: str
    failure_examples: List[Dict[str, Any]]
    task_description: str
    last_score: float
    attempts_remaining: int
    feedback: str

class PromptDebuggerState(BaseModel):
    task_name: str
    broken_prompt: str
    attempts: int
    max_attempts: int
    done: bool
    cumulative_score: float
    best_score: float
