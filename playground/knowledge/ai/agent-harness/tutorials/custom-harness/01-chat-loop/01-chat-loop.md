# Build an interactive chat loop

In this tutorial we will turn our one-shot script into a real conversation: you
type, the model replies, and it *remembers* what was said before. Along the way
we will encounter the message-history list, the `system` message that sets the
model's behaviour, and a simple read-print loop.

## Prerequisites

- You have finished [Tutorial 0](./00-first-request.md) and `first_request.py`
  runs successfully.
- Your `.venv` is active (your prompt shows `(.venv)`).
- Your `.env` file from Tutorial 0 is in the folder you run scripts from. We
  reuse it here — `load_dotenv()` will read it, so there's nothing to set in the
  terminal.

## Step 1 — Start a new file from what we know

Create a file called `chat_loop.py`. We begin with the same client setup from
Tutorial 0, so this part should feel familiar:

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

MODEL = "claude-opus-4-8"
```

Notice we pulled the model name out into a `MODEL` constant. We'll reuse it many
times, so naming it once keeps things tidy.

## Step 2 — Create the conversation history

The trick to a conversation is simple: we keep every message in a list and send
the *whole list* each time. Add this below the code from Step 1:

```python
messages = [
    {"role": "system", "content": "You are a concise, friendly assistant."},
]
```

That first `system` message is our instruction to the model about how to behave.
Everything the user and model say will get appended after it.

## Step 3 — Write the loop

Now add the loop that reads your input, sends the history, and prints the reply.
Add this below Step 2:

```python
while True:
    user_text = input("you> ")
    if user_text.strip() in {"exit", "quit"}:
        print("Goodbye!")
        break

    messages.append({"role": "user", "content": user_text})

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )
    reply = response.choices[0].message.content

    messages.append({"role": "assistant", "content": reply})
    print("bot>", reply)
```

Read the loop top to bottom: we get your text, stop if you typed `exit`, add
your text to the history as a `user` message, send the whole history, then add
the model's reply back to the history as an `assistant` message before printing
it. That append-the-reply step is what gives the model its memory.

## Step 4 — Run it and have a conversation

```powershell
python chat_loop.py
```

The program waits for you with the prompt:

```
you>
```

Type a message and press Enter:

```
you> My name is Sam.
```

After a moment the bot replies, something like:

```
bot> Nice to meet you, Sam! How can I help?
```

## Step 5 — Prove that it remembers

Now ask it something that only works if it remembered your name:

```
you> What is my name?
```

The bot replies, something like:

```
bot> Your name is Sam.
```

Notice what just happened: the model had no memory of its own, but because we
kept appending to `messages` and sending the whole list, it could see your
earlier message. *That list is the memory.* This is the single most important
idea in the whole series — hold onto it.

## Step 6 — Exit cleanly

Type `exit` and press Enter:

```
you> exit
Goodbye!
```

Notice the program stops and returns you to your shell prompt. Run
`python chat_loop.py` again and repeat the name test as many times as you like —
it's safe to re-run, and each run starts with a fresh, empty memory.

## What you accomplished

You built a stateful chat program. It holds a conversation, obeys a system
instruction, and remembers earlier turns by carrying a growing message list.
You've now seen the core loop that every agent harness sits on top of: read,
append, send the whole history, append the reply, repeat.

## Next steps

- Continue to [Tutorial 2: Give the model its first tool](02-first-tool.md),
  where we let the model *do* something instead of only talking.
- Want to understand the different message roles more deeply? Keep it for later
  and see <https://platform.openai.com/docs/guides/text-generation>.
