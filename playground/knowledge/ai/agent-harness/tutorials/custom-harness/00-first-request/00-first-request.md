# Send your first message to the model

In this tutorial we will set up a clean Python project and send a single message
to your language model through your LiteLLM endpoint, then print its reply. Along
the way we will encounter Python virtual environments, the `openai` client
library, a `.env` file for configuration, and the shape of a
chat-completions request.

This is the foundation every later tutorial builds on.

## Prerequisites

- Python 3.10 or newer, available as `python` in your terminal.
- Your LiteLLM endpoint URL (something like `https://litellm.example.com`).
- An API key for that endpoint.
- PowerShell (the examples use Windows PowerShell).

## Step 1 — Create the project folder

First, create a folder for the whole series and move into it.

```powershell
mkdir agent-harness
cd agent-harness
```

Now that you're inside `agent-harness`, everything from here on lives in this
folder. Notice that your prompt now shows the `agent-harness` directory.

## Step 2 — Create and activate a virtual environment

We keep our packages isolated in a virtual environment so nothing leaks into
your system Python.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

After you activate it, your prompt changes to start with `(.venv)`:

```
(.venv) PS C:\...\agent-harness>
```

Notice that `(.venv)` prefix. It tells you the environment is active. If you
don't see it, the activation didn't work — re-run the second command above.

> If PowerShell blocks the activation script with an execution-policy error,
> run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` in the
> same window and try activating again.

## Step 3 — Install the client library

We will talk to LiteLLM using the `openai` library, because LiteLLM speaks the
same API. We also install `python-dotenv` (loads settings from a `.env` file),
`truststore` (lets Python trust your machine's certificate store, which corporate
networks need), and we pin `httpx` (the library `openai` uses under the hood) to
a version they agree on. We pin every version so this tutorial works the same for
everyone.

```powershell
pip install "openai==1.51.0" "python-dotenv==1.0.1" "httpx==0.27.2" "truststore==0.10.1"
```

This prints several lines ending in something like:

```
Successfully installed httpx-0.27.2 openai-1.51.0 python-dotenv-1.0.1 truststore-0.10.1 ...
```

Let's check the install worked:

```powershell
python -c "import openai, dotenv, truststore; print(openai.__version__)"
```

The output should be exactly:

```
1.51.0
```

## Step 4 — Put your endpoint and key in a `.env` file

We keep secrets out of our code by storing them in a `.env` file that lives next
to our script. Create a file called `.env` in the `agent-harness` folder with
exactly this content, substituting your real values:

```
LITELLM_BASE_URL=https://litellm.example.com
LITELLM_API_KEY=sk-your-real-key-here
```

Notice there are no quotes and no spaces around the `=` sign — that's the `.env`
format.

Let's check the file is there and correct:

```powershell
type .env
```

The output should be the two lines you just wrote:

```
LITELLM_BASE_URL=https://litellm.example.com
LITELLM_API_KEY=sk-your-real-key-here
```

Remember that this `.env` file holds a secret. Never commit it to version
control — if you use git, add a line containing `.env` to a `.gitignore` file.

## Step 5 — Write the first request script

Now we write the actual program. Create a file called `first_request.py` with
exactly this content:

```python
import os
import truststore
from dotenv import load_dotenv
from openai import OpenAI

truststore.inject_into_ssl()
load_dotenv()

client = OpenAI(
    base_url=os.environ["LITELLM_BASE_URL"],
    api_key=os.environ["LITELLM_API_KEY"],
)

response = client.chat.completions.create(
    model="claude-opus-4-8",
    messages=[
        {"role": "user", "content": "Say hello in exactly five words."}
    ],
)

print(response.choices[0].message.content)
```

Notice the five things this script does: `truststore.inject_into_ssl()` makes
Python trust your system's certificates (so corporate networks don't break the
connection), `load_dotenv()` reads your `.env` file into the environment, it
builds a `client` pointed at your endpoint, it sends one `user` message, and it
prints the model's reply text out of `response.choices[0].message.content`. That
path into the response object is worth remembering — we use it again and again.

## Step 6 — Run it

```powershell
python first_request.py
```

After a moment, the model responds and you see a single line, something like:

```
Hello there, nice to meet!
```

The exact five words will vary — the model writes them fresh each time. What
matters is that you got a reply back from your endpoint.

If you instead see a `KeyError`, your `.env` file is missing, is not in the same
folder as `first_request.py`, or has a typo in a variable name — recheck Step 4.
If you see an authentication or connection error, double-check the URL and key
values in `.env`. If you see `TypeError: Client.__init__() got an unexpected
keyword argument 'proxies'`, your `httpx` is too new — re-run the install command
in Step 3, which pins it to `httpx==0.27.2`. If you see `SSL:
CERTIFICATE_VERIFY_FAILED`, the `truststore` line is missing or your machine
doesn't trust the endpoint's certificate — confirm the script has
`truststore.inject_into_ssl()` near the top. If you see a `403` with
`team_model_access_denied`, the model name is wrong for your endpoint; use one
your team is allowed, such as `claude-opus-4-8`.

## Step 7 — Run it again

Run the exact same command a second time.

```powershell
python first_request.py
```

Notice that the reply is different this time. That's the model generating a new
answer on every call. Feel free to run it a few more times — it's completely
safe to repeat, and it's good to *feel* the request/response rhythm.

## What you accomplished

You built a working pipeline from your machine to a language model and back: a
virtual environment, the client library, a `.env` file for secure configuration,
and a script that sends a message and prints the reply. That small
`first_request.py` is the seed of everything else — a harness is really just this
request, made cleverer.

## Next steps

- Continue to [Tutorial 1: Build an interactive chat loop](./01-chat-loop.md),
  where we turn this one-shot script into a real conversation.
- Curious *why* the message has a `role`? That's the chat-message format;
  we'll keep using it, and you can read the reference at
  <https://platform.openai.com/docs/api-reference/chat> when you want the full
  picture.
