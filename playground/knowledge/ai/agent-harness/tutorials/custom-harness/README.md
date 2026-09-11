# Build Your Own Agent Harness — Tutorial Series

This is a hands-on, learn-by-doing series. By the end you will have written,
from scratch and in plain Python, a small but real **agent harness**: a program
that talks to a language model, gives it tools, and lets it work autonomously
across multiple steps to finish a task.

We build it up one tutorial at a time. Each tutorial produces a working program
you can run, and each one adds exactly one new capability on top of the last.

## The path

| # | Tutorial | What you build |
| --- | --- | --- |
| 0 | [Send your first message to the model](./00-first-request/00-first-request.md) | A one-shot script that gets a reply from your LiteLLM endpoint |
| 1 | [Build an interactive chat loop](./01-chat-loop/01-chat-loop.md) | A back-and-forth chat that remembers the conversation |
| 2 | [Give the model its first tool](./02-first-tool/02-first-tool.md) | The model calls a calculator function you wrote |
| 3 | [Build the agent loop](./03-agent-loop/03-agent-loop.md) | The model uses tools by itself, repeatedly, until done |
| 4 | [Complete a multi-step task](./04-multi-step-task/04-multi-step-task.md) | The agent reads and writes files to finish a real job |
| 5 | [Handle tool errors gracefully](./05-graceful-tool-errors/05-graceful-tool-errors.md) | The agent turns a failing tool into a result instead of a crash |
| 6 | [Stream the response as it arrives](./06-streaming-responses/06-streaming-responses.md) | The final answer prints token by token |
| 7 | [Persist the conversation](./07-persist-the-conversation/07-persist-the-conversation.md) | The chat is saved to and loaded from a JSON file |
| 8 | [Guard the input](./08-input-guardrails/08-input-guardrails.md) | The agent rejects oversized or wrong-type input up front |
| 9 | [Gate risky actions behind approval](./09-approval-gates/09-approval-gates.md) | Dangerous tool calls pause for a yes/no before running |
| 10 | [Cap the agent's resources](./10-resource-guardrails/10-resource-guardrails.md) | Tool-call and output limits keep a run bounded |
| 11 | [Scrub the output](./11-output-guardrails/11-output-guardrails.md) | Secrets are redacted from tool results before the model sees them |
| 12 | [Give the agent a shell command tool](./12-shell-command-tool/12-shell-command-tool.md) | The agent runs allow-listed shell commands on your machine |
| 13 | [Give the agent a web-fetch tool](./13-web-fetch-tool/13-web-fetch-tool.md) | The agent downloads a live web page and reads it |
| 14 | [Generate tool schemas from your functions](./14-tool-registry-from-signature/14-tool-registry-from-signature.md) | Tool JSON schemas are built automatically from type hints |
| 15 | [Keep the conversation from growing forever](./15-context-management/15-context-management.md) | A trim step holds the message history to a fixed window |
| 16 | [Delegate work to a sub-agent](./16-sub-agents/16-sub-agents.md) | A planner agent hands focused tasks to a worker agent |
| 17 | [Give the agent a plan it follows](./17-structured-planning-react/17-structured-planning-react.md) | The agent drafts a numbered plan, then works through it (ReAct) |

Tutorials 0 through 4 build on each other — start at Tutorial 0 and work straight
through them in order, since each assumes the file you built in the one before it.

Tutorials 5 onward are each **standalone**: every one starts from an empty folder
and builds a complete, runnable agent from scratch, adding a single new capability.
Open any of them on its own and follow it start to finish — no earlier tutorial
required.

## What you need before you start

- Python 3.10 or newer installed.
- A LiteLLM endpoint URL and an API key for it.
- A terminal (PowerShell on Windows is assumed in the examples).

Everything else is installed and explained inside Tutorial 0.
