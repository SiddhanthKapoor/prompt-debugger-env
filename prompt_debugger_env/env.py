from typing import Any, Dict
from pydantic import BaseModel
import asyncio
from .models import PromptDebuggerAction, PromptDebuggerObservation, PromptDebuggerState
from .tasks import TASKS
from .graders import grade

class ResetResult(BaseModel):
    observation: Dict[str, Any]

class StepResult(BaseModel):
    observation: Dict[str, Any]
    reward: float
    done: bool
    info: Dict[str, Any]

class PromptDebuggerEnv:
    def __init__(self):
        self._state = None

    async def reset(self, task_name: str = "fix-output-format") -> ResetResult:
        if task_name not in TASKS:
            raise ValueError(f"Unknown task: {task_name}")
            
        task_data = TASKS[task_name]
        self._state = PromptDebuggerState(
            task_name=task_name,
            broken_prompt=task_data["broken_prompt"],
            attempts=0,
            max_attempts=task_data.get("max_steps", 5),
            done=False,
            cumulative_score=0.01,
            best_score=0.01
        )
        
        obs = PromptDebuggerObservation(
            broken_prompt=self._state.broken_prompt,
            failure_examples=task_data["failure_examples"],
            task_description=task_data["description"],
            last_score=0.01,
            attempts_remaining=self._state.max_attempts,
            feedback="Ready. Here's your broken prompt and how it's failing."
        )
        
        return ResetResult(observation=obs.model_dump())

    async def step(self, action: PromptDebuggerAction) -> StepResult:
        if self._state is None or self._state.done:
            raise RuntimeError("Environment needs to be reset")
            
        fixed_prompt = action.fixed_prompt
        self._state.attempts += 1
        
        raw_score = await grade(self._state.task_name, fixed_prompt)
        
        reward = raw_score
        
            
        self._state.best_score = max(self._state.best_score, raw_score)
        self._state.cumulative_score += reward
        
        done = raw_score >= 0.85 or self._state.attempts >= self._state.max_attempts
        self._state.done = done
        
        task_data = TASKS[self._state.task_name]
        obs = PromptDebuggerObservation(
            broken_prompt=self._state.broken_prompt,
            failure_examples=task_data["failure_examples"],
            task_description=task_data["description"],
            last_score=raw_score,
            attempts_remaining=self._state.max_attempts - self._state.attempts,
            feedback=f"Score: {raw_score:.2f}. " + ("Great!" if raw_score >= 0.85 else "Still failing some tests.")
        )
        
        return StepResult(
            observation=obs.model_dump(),
            reward=reward,
            done=done,
            info={"raw_score": raw_score}
        )

    async def state(self) -> PromptDebuggerState:
        return self._state

    async def close(self):
        pass
