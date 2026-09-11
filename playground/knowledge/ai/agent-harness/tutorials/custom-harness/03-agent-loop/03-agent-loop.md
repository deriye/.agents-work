# Build the agent loop

In this tutorial we will build the real agent loop: instead of us handling one
tool call by hand, the program keeps calling the model and running whichever
tools it asks for, over and over, until the model is satisfied and gives a final
answer. Along the way we will encounter a tool registry, a dispatch step, and
the "keep going until there are no more tool calls" loop that defines a harness.

## Prerequisites

- You have finished [Tutorial 2](./02-first-tool.md) and `tool_call.py` works.
- Your `.venv` is active and your `.env` file from Tutorial 0 is in the folder
  you run scripts from.

## Step 1 — Set up the client and two tools

Create a file called `agent_loop.py`. We give the agent two tools this time so
it has a real choice to make. Start with:

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
    ops = {
        "add": a + b,
        "subtract": a - b,
        "multiply": a * b,
        "divide": a / b if b != 0 else "cannot divide by zero",
    }
    return ops.get(op, "unknown operation")


def word_count(text):
    return len(text.split())
```

Notice both tools are plain functions. The agent will pick between them.

## Step 2 — Build a registry so we can look tools up by name

When the model asks for a tool by name, we need to find the matching function.
A dictionary does this cleanly. Add:

```python
TOOL_FUNCTIONS = {
    "calculator": calculator,
    "word_count": word_count,
}

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
    },
    {
        "type": "function",
        "function": {
            "name": "word_count",
            "description": "Count the number of words in a piece of text.",
            "parameters": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        },
    },
]
```

Notice the `TOOL_FUNCTIONS` dictionary maps a name to the real function. This is
how we turn `"calculator"` from the model into an actual call.

## Step 3 — Write the agent loop

This is the heart of the harness. Add this function below Step 2:

```python
def run_agent(user_text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Use tools when they help."},
        {"role": "user", "content": user_text},
    ]

    while True:
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )
        message = response.choices[0].message
        messages.append(message)

        # No tool calls means the model gave its final answer.
        if not message.tool_calls:
            return message.content

        # Otherwise, run every tool the model asked for.
        for call in message.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            print(f"  [running tool: {name}({args})]")

            func = TOOL_FUNCTIONS[name]
            result = func(**args)

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.id,
                    "content": str(result),
                }
            )
```

Read the loop carefully, because this *is* the harness:

1. Call the model with the current history and the tools.
2. Append its message to the history.
3. If it asked for **no** tools, it's done — return the answer.
4. If it asked for tools, run each one, append each result, and loop again.

The `while True` is what makes the agent autonomous: it keeps going by itself
until the model stops asking for tools.

## Step 4 — Add a small runner at the bottom

```python
if __name__ == "__main__":
    question = "How many words are in the sentence 'the quick brown fox jumps', and what is that count multiplied by 10?"
    answer = run_agent(question)
    print("bot>", answer)
```

Notice this question needs *two* tools in sequence: count the words, then
multiply. We're deliberately forcing the loop to run more than once.

## Step 5 — Run it and watch the loop turn

```powershell
python agent_loop.py
```

You'll see the tools run one after another, then the final answer:

```
  [running tool: word_count({'text': 'the quick brown fox jumps'})]
  [running tool: calculator({'a': 5, 'b': 10, 'op': 'multiply'})]
bot> The sentence has 5 words, and 5 multiplied by 10 is 50.
```

Notice the order: the model first called `word_count`, saw the result `5`, and
only *then* asked for `calculator` with `a=5`. It used the output of one tool as
the input to the next — and our loop handled both turns without any special
code. That is the whole point of the agent loop.

If you see only one `[running tool: ...]` line and a confused answer, your model
may have tried to do it in one shot; re-run it, as models sometimes vary.

## Step 6 — Ask your own questions and repeat

Change the `question` in Step 4 to anything you like — for example
`"What is 12 times 12?"` (one tool) or a multi-part question (several tools).
Save and run again:

```powershell
python agent_loop.py
```

Notice that simple questions make the loop turn once, and compound questions
make it turn several times, all with the same code. Re-run freely; it's safe.

## What you accomplished

You built a genuine agent loop — the defining piece of an agent harness. It
calls the model, runs any requested tools through a name-to-function registry,
feeds results back, and repeats until the model finishes. You watched the agent
chain one tool's output into another tool's input entirely on its own.

## Next steps

- Continue to [Tutorial 4: Complete a multi-step task](./04-multi-step-task.md),
  where we give the agent file-reading and file-writing tools and set it loose
  on a real job.
- Want to reason about why loops like this can misbehave or loop forever? Save
  that for an explanation piece later; for now, the concrete loop is enough.
