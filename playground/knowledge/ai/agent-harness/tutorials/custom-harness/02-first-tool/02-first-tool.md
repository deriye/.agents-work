# Give the model its first tool

In this tutorial we will give the model a tool it can call: a small calculator
function we write in Python. We will ask a math question, watch the model
*request* our function, run it ourselves, hand back the result, and see the
model use that result in its answer. Along the way we will encounter tool
schemas, the `tool_calls` field on a response, and the `tool` message role.

This is the moment a chatbot becomes an agent.

## Prerequisites

- You have finished [Tutorial 1](01-chat-loop.md) and `chat_loop.py` works.
- Your `.venv` is active and your `.env` file from Tutorial 0 is in the folder
  you run scripts from. `load_dotenv()` reads it for us.

## Step 1 — Start the file with a real Python tool

Create a file called `tool_call.py`. First we write the actual function the
model will be allowed to call. Put this at the top:

```python
import os
import json
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


def calculator(a, b, op):
    if op == "add":
        return a + b
    if op == "subtract":
        return a - b
    if op == "multiply":
        return a * b
    if op == "divide":
        return a / b
    return "unknown operation"
```

Notice this is ordinary Python — nothing AI-specific. The model will never run
this code itself; *we* run it when the model asks us to.

## Step 2 — Describe the tool to the model

The model can't see our Python. We describe the tool to it with a schema. Add
this below the function:

```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Do arithmetic on two numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                    "op": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                    },
                },
                "required": ["a", "b", "op"],
            },
        },
    }
]
```

Notice the schema names the function, explains what it does, and lists its
arguments. This description is the *only* thing the model knows about our tool.

## Step 3 — Send a question and offer the tool

Now we ask a math question and pass `tools=` so the model is allowed to use it.
Add this below Step 2:

```python
messages = [
    {"role": "user", "content": "What is 347 multiplied by 29?"},
]

response = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tools,
)

message = response.choices[0].message
print("tool_calls:", message.tool_calls)
```

## Step 4 — Run it and see the model ask for the tool

```powershell
python tool_call.py
```

You will see the model did *not* answer in plain text. Instead it asked to call
our function. The output looks something like:

```
tool_calls: [ChatCompletionMessageToolCall(id='call_abc123', function=Function(arguments='{"a": 347, "b": 29, "op": "multiply"}', name='calculator'), type='function')]
```

Notice there's no answer to the math yet — just a *request* to run `calculator`
with `a=347, b=29, op=multiply`. The model is asking us to do the work. If you
instead see plain text with the answer, that's fine too on some models, but most
will request the tool as shown.

## Step 5 — Run the tool and hand back the result

Now we do the work the model asked for and give it the result. Add this below
the code from Step 3:

```python
tool_call = message.tool_calls[0]
args = json.loads(tool_call.function.arguments)

result = calculator(args["a"], args["b"], args["op"])
print("we computed:", result)

# Record the model's request, then our answer to it.
messages.append(message)
messages.append(
    {
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": str(result),
    }
)

# Ask the model to continue now that it has the result.
followup = client.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=tools,
)
print("bot>", followup.choices[0].message.content)
```

Read what we just did: we parsed the arguments, ran our own `calculator`,
appended the model's request and then a `tool` message carrying the result,
using the same `tool_call_id` so the model knows which request it answers. Then
we called the model again.

## Step 6 — Run it again and see the finished answer

```powershell
python tool_call.py
```

Now the output shows the whole round trip:

```
tool_calls: [ChatCompletionMessageToolCall(...)]
we computed: 10063
bot> 347 multiplied by 29 is 10,063.
```

Notice the final `bot>` line uses the number *we* computed. The model didn't do
the arithmetic — it delegated to our tool, we ran it, and it wove our result
into a natural answer. That hand-off is the heartbeat of an agent.

If you see a `KeyError` on `messages` when calling the model back, check that
you appended both the `message` and the `tool` message in Step 5, in that order.

## Step 7 — Change the question and repeat

Edit the question in Step 3 to something else, like `"Divide 100 by 8."`, save,
and run again:

```powershell
python tool_call.py
```

You'll see the model request `op=divide` and the bot answer `12.5`. Try a few
different questions — it's safe to repeat, and watching the arguments change
each time makes the pattern stick.

## What you accomplished

You gave a model a real capability. You described a tool, saw the model choose
to call it, ran the call yourself, and fed the result back so the model could
finish. You now understand the four moving parts of tool use: the schema, the
`tool_calls` request, running the function, and the `tool` result message.

## Next steps

- Continue to [Tutorial 3: Build the agent loop](./03-agent-loop.md), where the
  model calls tools *by itself, repeatedly*, without us hand-holding each call.
- Want the full tool-calling reference for later? See
  <https://platform.openai.com/docs/guides/function-calling>.
