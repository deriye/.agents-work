# Tutorial 2 — Search across many documents

In Tutorial 1 we handed the AI one small paragraph. In this tutorial we will
work with **many** pieces of text, and we will teach our program to *find* the
few pieces that matter before it answers. This "find the relevant text first"
step is the **retrieval** in Retrieval-Augmented Generation.

By the end you will have a program that stores several facts, and when you ask a
question it picks out the most relevant fact by *meaning* — not by matching
words — and answers using it. You will see, with your own eyes, the program
choosing the right piece of text.

This tutorial continues from Tutorial 1. You should already have Python, the
`my-rag` folder, and your OpenAI key from last time.

---

## Before we start

Open a terminal (Windows key → type `powershell` → Enter) and go to your
project folder:

```powershell
cd C:\work\playground\rag\tutorials\my-rag
```

Turn the private workspace back on:

```powershell
.\venv\Scripts\Activate.ps1
```

Check that `(venv)` appears at the start of your prompt. Good.

Because you opened a fresh terminal, you need to give it your key again. Type
the following, replacing `PASTE-YOUR-KEY-HERE` with your key:

```powershell
$env:OPENAI_API_KEY = "PASTE-YOUR-KEY-HERE"
```

Let's confirm it is set:

```powershell
echo $env:OPENAI_API_KEY
```

You should see your key (starting with `sk-`). Now we are ready.

---

## Step 1 — A quick idea: turning text into numbers

Here is the one new idea for this tutorial. Computers are good at comparing
numbers, not sentences. So we will turn each piece of text into a list of
numbers that captures its *meaning*. Text with similar meaning gets similar
numbers. These lists of numbers are called **embeddings**.

Once every piece of text is a list of numbers, finding the "most relevant" text
for a question becomes: turn the question into numbers too, then find the text
whose numbers are closest. That's it.

We won't dwell on the mathematics — we will just *use* it and watch it work.

---

## Step 2 — Install one more tool

We need a small tool for comparing lists of numbers, called **numpy**. With
`(venv)` showing, type:

```powershell
pip install numpy
```

Lines scroll by, and it finishes with `Successfully installed numpy-...`. (You
already installed `openai` in Tutorial 1, so we don't need it again.)

---

## Step 3 — Store some facts and turn them into numbers

Let's write a new program. Create a file called `search.py`:

```powershell
notepad search.py
```

Click **Yes** to create it, then paste in the following. Read the comments as
you go, but don't worry about mastering every line.

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

# Our small collection of facts. Each one is a separate piece of text.
facts = [
    "The Eiffel Tower is located in Paris, France.",
    "The Great Barrier Reef is the world's largest coral reef system.",
    "Mount Everest is the highest mountain above sea level.",
    "The blue whale is the largest animal known to have ever existed.",
    "Water is made of two hydrogen atoms and one oxygen atom.",
]

# Turn a piece of text into a list of numbers (an embedding).
def embed(text):
    result = client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return np.array(result.data[0].embedding)

# Turn every fact into numbers, once, and remember them.
print("Turning facts into numbers...")
fact_embeddings = [embed(fact) for fact in facts]
print("Done. We have", len(fact_embeddings), "facts ready to search.")
```

Save and close Notepad, then run it:

```powershell
python search.py
```

You should see:

```
Turning facts into numbers...
Done. We have 5 facts ready to search.
```

Notice there was a short pause before "Done" — that pause is your program
sending each fact to OpenAI and getting its list of numbers back. You now have
five facts stored as numbers, ready to search.

---

## Step 4 — Find the most relevant fact for a question

Now the interesting part: given a question, find which fact is closest in
meaning. Open the file again:

```powershell
notepad search.py
```

Add the following to the **bottom** of the file (below the code you already
have):

```python
# Measure how similar two lists of numbers are.
# A higher score means "more similar in meaning".
def similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Ask a question.
question = "How tall is the tallest mountain on Earth?"
question_embedding = embed(question)

# Score every fact against the question.
scores = [similarity(question_embedding, fe) for fe in fact_embeddings]

# Show every fact with its score, so we can watch it work.
print("\nQuestion:", question)
print("\nScores for each fact:")
for fact, score in zip(facts, scores):
    print(f"  {score:.3f}  {fact}")

# Pick the single best-matching fact.
best_index = int(np.argmax(scores))
print("\nBest matching fact:")
print(" ", facts[best_index])
```

Save, close Notepad, and run:

```powershell
python search.py
```

You should see something like:

```
Question: How tall is the tallest mountain on Earth?

Scores for each fact:
  0.203  The Eiffel Tower is located in Paris, France.
  0.178  The Great Barrier Reef is the world's largest coral reef system.
  0.561  Mount Everest is the highest mountain above sea level.
  0.190  The blue whale is the largest animal known to have ever existed.
  0.155  Water is made of two hydrogen atoms and one oxygen atom.
```

```
Best matching fact:
  Mount Everest is the highest mountain above sea level.
```

Your exact numbers will differ slightly, and that's fine. Look at what
happened: the fact about Mount Everest got the **highest** score, even though
our question never used the words "Everest" or "mountain's name". The program
matched by *meaning*. That is the whole trick.

---

## Step 5 — Repeat with different questions

Let's do this a few times to see the pattern. Open the file, and change the
`question` line to:

```python
question = "What is the biggest animal in history?"
```

Save and run again. This time the **blue whale** fact should get the highest
score and be chosen. Notice again: the question said "biggest animal", the fact
said "largest animal" — different words, same meaning, and the program found it.

Try another:

```python
question = "What is water made of?"
```

Run it. The water fact should win. Each time, watch the scores: the relevant
fact stands out clearly from the rest. Run it a few more times with your own
questions. This repetition is worth it — it builds a feel for how retrieval
behaves.

---

## Step 6 — Answer the question using the fact we found

We can now combine both halves: **retrieve** the best fact, then **ask the AI**
to answer using it — exactly like Tutorial 1, but now the document is chosen
automatically.

Open the file and add this to the very **bottom**:

```python
# Send the best fact and the question to the AI for a final answer.
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "Answer the question using only the fact provided.",
        },
        {
            "role": "user",
            "content": f"Fact: {facts[best_index]}\n\nQuestion: {question}",
        },
    ],
)

print("\nAnswer:")
print(" ", response.choices[0].message.content)
```

Save, close, and run:

```powershell
python search.py
```

Below the scores and the best-matching fact, you now also see a written
**Answer**, for example:

```
Answer:
  Water is made of two hydrogen atoms and one oxygen atom.
```

Run it again with a different `question`. Watch the whole pipeline flow: the
question comes in, every fact gets a score, the best one is chosen, and the AI
answers using it.

---

## What you built

You built a program that does the two core jobs of RAG:

1. **Retrieve** — turn text into numbers, and find the piece whose meaning is
   closest to the question.
2. **Generate** — hand that piece to the AI and get a written answer.

You also saw, in the printed scores, *why* the right piece was chosen. This is
the same machinery that powers systems searching millions of documents — they
just store far more numbers and find the closest ones faster.

---

## Coming up next

Our five facts were typed by hand. Real documents come as files — often PDFs —
and are far too long to paste in. In
**[Tutorial 3 — Chat with your PDFs](03-chat-with-your-pdfs.md)**, we will read a
real PDF from disk, cut it into pieces automatically, and ask questions across
the whole thing.

Leave your terminal open in the `my-rag` folder for the next tutorial.
