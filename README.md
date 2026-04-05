---
title: Prompt Debugger Env
emoji: 🔧
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
tags:
  - openenv
---

# prompt-debugger-env

**prompt-debugger-env** is an OpenEnv environment where an AI agent acts as a prompt engineer to debug and repair broken LLM system prompts. With system prompts routinely failing gracefully under pressure (hallucinating, producing invalid formats, or failing to prompt injection), this environment presents failing inputs alongside descriptions of what the prompt *should* do, automatically grading the agent's updated prompts using rigorous adversarial evaluation checklists.

## Observation Space

| Field | Type | Description |
|---|---|---|
| `broken_prompt` | string | The original broken system prompt |
| `failure_examples` | list[dict] | List of examples containing `input`, `actual_output`, and `what_went_wrong` |
| `task_description` | string | Plain English description of what the prompt SHOULD do |
| `last_score` | float | Execution score from the last step (0.0 initially) |
| `attempts_remaining`| int | Number of attempts left for the current task (max 5) |
| `feedback` | string | Human-readable feedback indicating if score improved or tests are still failing |

## Action Space

| Field | Type | Description |
|---|---|---|
| `fixed_prompt` | string | The agent's repaired version of the system prompt |

## Tasks

| Task Name | Difficulty | What's Broken | Success Criteria |
|---|---|---|---|
| `fix-output-format` | easy | Randomly returns plain text instead of structured JSON | Consistently return valid JSON with `answer` (string) and `confidence` (float 0.0-1.0) |
| `fix-hallucination` | medium | Prompt confidently hallucinates ungrounded product specs | Include uncertainty markers and never fabricate arbitrary spec numbers |
| `fix-adversarial-robustness` | hard | Jailbreakable and vulnerable to manipulation | Retain evaluation criteria over the content, maintain JSON response, ignore jailbreak intent |

## Run using Docker

```bash
docker build -t prompt-debugger-env .
docker run -p 7860:7860 prompt-debugger-env
```

## Running Local Inference

To test an autonomous agent against the tasks in this environment:
```bash
export API_BASE_URL="https://api-inference.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="<your_huggingface_token>"

python inference.py
```

## Baseline Scores

| Task | Model | Score |
|---|---|---|
| `fix-output-format` | Qwen/Qwen2.5-72B-Instruct | TBD |
| `fix-hallucination` | Qwen/Qwen2.5-72B-Instruct | TBD |
| `fix-adversarial-robustness`| Qwen/Qwen2.5-72B-Instruct | TBD |
