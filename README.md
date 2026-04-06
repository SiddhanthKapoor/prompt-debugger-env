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

# Prompt Debugger Env

**Prompt Debugger Env** is an interactive, rigorous OpenEnv environment designed to test and evaluate AI agents acting as **Prompt Engineers**. In real-world production systems, LLM prompts routinely fail under edge-case pressures—for example, hallucinating grounded specs, generating invalidly formatted outputs, or falling prey to adversarial jailbreaks. 

This environment challenges the AI agent to actively debug and repair these failing system prompts. Given failing test inputs and a plain-English description of the expected behavior, the agent must iteratively revise the prompt until it passes deterministic, robust evaluation graders.

## Why This Matters
- **Evaluation of Meta-Reasoning:** Testing an LLM's ability to evaluate and repair system instructions tests deep reasoning over prompt injection and instructional boundaries.
- **Real-World Scenarios:** The environment mirrors real challenges across Output Structure constraints, Uncertainty mapping (reducing Hallucination), and Adversarial robustness in Content Moderation.
- **Deterministic Graders:** The environment executes deterministic API tests (temperature=0) ensuring grading consistency and unbiased scoring.

## Observation Space

| Field | Type | Description |
|---|---|---|
| `broken_prompt` | string | The original broken system prompt the agent must fix |
| `failure_examples` | list[dict] | Examples containing `input`, `actual_output`, and `what_went_wrong` |
| `task_description` | string | Plain English description of what the prompt SHOULD do |
| `last_score` | float | Execution score from the last task attempt (0.0 to 1.0) |
| `attempts_remaining`| int | Number of attempts left for the current task (max 5 attempts) |
| `feedback` | string | Actionable human-readable feedback indicating if tests are still failing |

## Action Space

| Field | Type | Description |
|---|---|---|
| `fixed_prompt` | string | The agent's updated and repaired system prompt |

## Available Tasks

| Task Name | Difficulty | What's Broken | Success Criteria |
|---|---|---|---|
| `fix-output-format` | easy | Randomly returns plain text instead of structured JSON | Consistently return valid JSON with `answer` (string) and `confidence` (float 0.0-1.0) |
| `fix-hallucination` | medium | Prompt confidently hallucinates ungrounded product specs | Include uncertainty markers and never fabricate arbitrary spec numbers |
| `fix-adversarial-robustness` | hard | Jailbreakable and vulnerable to manipulation | Retain evaluation criteria over the content, maintain JSON response, ignore jailbreak intent |

## Run using Docker

To host the evaluation environment locally, build and run the Docker image:

```bash
docker build -t prompt-debugger-env .
docker run -p 7860:7860 prompt-debugger-env
```

## Running Local Inference

To test an autonomous agent against the tasks in this environment smoothly, provide your specific API configurations. Here is an example leveraging the Groq API:

```bash
export API_BASE_URL="https://api.groq.com/openai/v1"
export MODEL_NAME="llama-3.3-70b-versatile"
export HF_TOKEN="<your_groq_api_key>"

python3 inference.py
```

## Baseline Scores

The baseline performance evaluations confirm the validity of this environment:

| Task | Model | Score |
|---|---|---|
| `fix-output-format` | llama-3.3-70b-versatile | 1.00 |
| `fix-hallucination` | llama-3.3-70b-versatile | 1.00 |
| `fix-adversarial-robustness`| llama-3.3-70b-versatile | 0.86 |
