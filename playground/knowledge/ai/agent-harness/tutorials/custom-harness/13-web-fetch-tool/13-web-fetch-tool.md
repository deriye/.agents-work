# Give the agent a web-fetch tool

In this tutorial we will build an agent that can reach out to the internet: a
`fetch_url` tool that downloads a page and hands the text back to the model. Web
responses are messy and can be huge, so we cap the size and handle failures
cleanly from the start. We will set up the project, write the fetch tool with
`httpx`, truncate the result, and watch the agent pull a live page and answer a
question about it. Along the way we will encounter an HTTP request, a size cap on
tool output, and network errors returned as results.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL and an API key for it.
- Internet access from your machine.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Set up a fresh project

Create a folder and move into it:

```powershell
mkdir web-agent
cd web-agent
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Notice your prompt now starts with `(.venv)`.

> If PowerShell blocks activation with an execution-policy error, run
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` and try
> again.

Install the pinned libraries (we use `httpx`, which the client already depends on):

```powershell
pip install "openai==1.51.0" "python-dotenv==1.0.1" "httpx==0.27.2" "truststore==0.10.1"
```

## Step 2 — Add your endpoint and key

Create a `.env` file with your real values:

```
LITELLM_BASE_URL=https://litellm.example.com
LITELLM_API_KEY=sk-your-real-key-here
```

## Step 3 — Build the fetch tool

Create `file_agent.py`. The heart of this tutorial is `fetch_url`: it makes an
HTTP request, caps the returned text, and turns any network failure into a plain
result string:

```python
import os
import json
import httpx
import truststore
from dotenv import load_dotenv
from openai import OpenAI

truststore.inject_into_ssl()
load_dotenv()

client = OpenAI(
    base_url=os.environ["LITELLM_BASE_URL"],
    api_key=os.environ["LITELLM_API_KEY"],
)

MODEL = "claude-opus-4-8"
MAX_FETCH_CHARS = 2000


def fetch_url(url):
    if not url.startswith(("http://", "https://")):
        return "ERROR: url must start with http:// or https://"
    try:
        response = httpx.get(url, timeout=10, follow_redirects=True)
    except Exception as error:
        return f"ERROR: {type(error).__name__}: {error}"

    text = response.text
    if len(text) > MAX_FETCH_CHARS:
        text = text[:MAX_FETCH_CHARS] + f"\n...[truncated, page was {len(response.text)} characters]"
    return f"HTTP {response.status_code}\n{text}"
```

Notice three safety touches we build in from the start: we reject anything that
isn't an `http(s)` URL, we wrap the request so a dead host becomes an `ERROR:`
result instead of a crash, and we cap the body at `MAX_FETCH_CHARS` so a giant
page can't swamp the model.

## Step 4 — Register and describe the tool

Add the registry and schema below Step 3:

```python
TOOL_FUNCTIONS = {
    "fetch_url": fetch_url,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "fetch_url",
            "description": "Download a web page and return its text (truncated).",
            "parameters": {
                "type": "object",
                "properties": {"url": {"type": "string"}},
                "required": ["url"],
            },
        },
    },
]
```

## Step 5 — Add the agent loop

Add the standard loop:

```python
def run_agent(user_text, max_turns=10):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a research assistant. Use fetch_url to read web pages. "
                "Complete the user's task, then report what you found."
            ),
        },
        {"role": "user", "content": user_text},
    ]

    for turn in range(max_turns):
        response = client.chat.completions.create(
            model=MODEL, messages=messages, tools=tools
        )
        message = response.choices[0].message
        messages.append(message)

        if not message.tool_calls:
            return message.content

        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"    [turn {turn + 1}] {name}({args})")

            func = TOOL_FUNCTIONS[name]
            result = func(**args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result),
                }
            )

    return "Stopped: reached the turn limit."
```

## Step 6 — Add a runner and fetch a live page

Add a runner that asks the agent to read a real, stable test page:

```python
if __name__ == "__main__":
    task = "Fetch https://example.com and tell me the main heading on the page."
    result = run_agent(task)
    print("bot>", result)
```

Run it:

```powershell
python file_agent.py
```

The agent fetches the page and answers from its content:

```
    [turn 1] fetch_url({'url': 'https://example.com'})
bot> The main heading on https://example.com is "Example Domain".
```

Notice the agent reached outside your machine, pulled a live page, and read its
HTML to find the heading — all on its own.

## Step 7 — Watch a bad URL come back as a clean error

Change the task to a host that doesn't exist:

```python
    task = "Fetch https://this-domain-does-not-exist-zzz.com and tell me what happened."
```

Run it:

```powershell
python file_agent.py
```

The failure returns as a result, not a crash:

```
    [turn 1] fetch_url({'url': 'https://this-domain-does-not-exist-zzz.com'})
bot> That address couldn't be reached — the lookup failed (ConnectError), so there's no page to read.
```

Notice the program stayed alive and the agent explained the failure, because we
turned the exception into an `ERROR:` result inside `fetch_url`.

## Step 8 — Reject a non-web URL and repeat

Change the task to a forbidden scheme:

```python
    task = "Fetch file:///c:/windows/win.ini and show me the contents."
```

Run it:

```powershell
python file_agent.py
```

The scheme check refuses it up front:

```
    [turn 1] fetch_url({'url': 'file:///c:/windows/win.ini'})
bot> I can only fetch http:// or https:// URLs, so I can't open that file path.
```

Notice `httpx` was never called — the guard ran first, keeping the tool to the web
only. Change the task to any `https://` page you like and re-run; it's safe to
repeat.

## What you accomplished

You gave your agent a window to the internet. Its `fetch_url` tool downloads a
page, caps the text so a huge response can't overwhelm the model, refuses anything
that isn't a web URL, and turns network failures into readable results instead of
crashes. You watched it pull a live page, explain a dead host, and reject a file
path — a genuinely useful tool that stays inside sensible limits.

## Next steps

- Explore [Tutorial 14: Generate tool schemas from your functions](../14-tool-registry-from-signature/14-tool-registry-from-signature.md),
  which removes the hand-written JSON schema boilerplate.
- Turning raw HTML into clean text, or restricting which domains may be fetched,
  are how-to topics for later. The capped, guarded fetch is the core tool.
