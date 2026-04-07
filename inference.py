import os
import json
import asyncio
from openai import AsyncOpenAI
from prompt_debugger_env.env import PromptDebuggerEnv
from prompt_debugger_env.models import PromptDebuggerAction

API_KEY = os.getenv("API_KEY") or os.getenv("HF_TOKEN")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.groq.com/openai/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "llama-3.3-70b-versatile")

AGENT_SYSTEM_PROMPT = """You are an expert prompt engineer. You will receive:
1. A broken LLM system prompt
2. Examples of how it's failing
3. A description of what it should do

Your job: rewrite the system prompt to fix all the failures shown.

Rules:
- Output ONLY the fixed system prompt text. No explanation. No preamble. No markdown.
- Keep the same general purpose as the original
- Make it robust, specific, and unambiguous
- Add explicit output format instructions if needed
- Add constraint statements to prevent the failure modes shown"""

async def run_task(task_name: str, client: AsyncOpenAI, env: PromptDebuggerEnv):
    print(f"[START] task={task_name} env=prompt-debugger-env model={MODEL_NAME}")
    
    reset_result = await env.reset(task_name)
    obs = reset_result.observation
    
    rewards = []
    done = False
    step_count = 0
    score = 0.0
    
    while not done and step_count < 5:
        step_count += 1
        
        user_prompt = f"""Broken Prompt:
{obs['broken_prompt']}

Description:
{obs['task_description']}

Failures:
{json.dumps(obs['failure_examples'], indent=2)}

Feedback on last attempt:
{obs['feedback']}
"""
        
        error_msg = "null"
        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                temperature=0.0,
                messages=[
                    {"role": "system", "content": AGENT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ]
            )
            fixed_prompt = response.choices[0].message.content.strip()
            
            # Remove markdown logic if it tries to wrap in markdown backticks
            if fixed_prompt.startswith("```") and fixed_prompt.endswith("```"):
                lines = fixed_prompt.split('\n')
                if len(lines) >= 3:
                    fixed_prompt = '\n'.join(lines[1:-1]).strip()
        except Exception as e:
            error_msg = str(e).replace('\n', ' ')
            print(f"[STEP] step={step_count} action= reward=0.00 done=false error={error_msg}")
            break
            
        action = PromptDebuggerAction(fixed_prompt=fixed_prompt)
        try:
            step_result = await env.step(action)
            obs = step_result.observation
            reward = step_result.reward
            done = step_result.done
            score = obs['last_score']
            rewards.append(reward)
            
            action_text = fixed_prompt.replace('\n', '\\n')
            print(f"[STEP] step={step_count} action={action_text} reward={reward:.2f} done={str(done).lower()} error=null")
        except Exception as e:
            error_msg = str(e).replace('\n', ' ')
            action_text = fixed_prompt.replace('\n', '\\n')
            print(f"[STEP] step={step_count} action={action_text} reward=0.00 done=false error={error_msg}")
            break
            
    success = score >= 0.700
    rewards_str = ",".join([f"{r:.2f}" for r in rewards])
    print(f"[END] success={str(success).lower()} steps={step_count} score={score:.3f} rewards={rewards_str}")

async def main():
    if not API_KEY:
        print("API_KEY or HF_TOKEN environment variable not set. Evaluator exiting.")
        return
        
    client = AsyncOpenAI(api_key=API_KEY, base_url=API_BASE_URL)
    env = PromptDebuggerEnv()
    
    tasks = ["fix-output-format", "fix-hallucination", "fix-adversarial-robustness"]
    for i, task in enumerate(tasks):
        await run_task(task, client, env)
        if i < len(tasks) - 1:
            print()

if __name__ == "__main__":
    asyncio.run(main())
