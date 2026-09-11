# Agent Harness

Building the runtime that wraps an LLM into an agent: the chat loop, tool calling, guardrails,
context management, and sub-agents.

## Contents

| Path | What's inside |
|------|---------------|
| [tutorials/custom-harness](./tutorials/custom-harness/) | An 18-step build (`00-first-request` → `17-structured-planning-react`): first request, chat loop, tools, agent loop, streaming, persistence, input/approval/resource/output guardrails, shell & web-fetch tools, context management, and sub-agents. |
| [tutorials/deepseek-harness](./tutorials/deepseek-harness/) | Planned: a DeepSeek-specific harness walkthrough. |
| [projects/pi](./projects/pi/) | A full coding-agent harness (multi-package: agent, ai, coding-agent, orchestrator, tui). |
| [projects/opencode-sdk](./projects/opencode-sdk/) | SDK for driving the OpenCode agent. |

## Convention

Sequential lessons live under `tutorials/`; runnable, self-contained builds live under `projects/`.
See the [playground README](../../README.md).
