# Tutorial 3 — Chat with your PDFs

In Tutorials 1 and 2 we typed our text by hand. In this tutorial we will point
our program at a **real PDF file** and ask questions about it. This is the kind
of thing people actually want from RAG: "here is a document I don't have time to
read — answer my questions about it."

By the end you will have a program that reads a PDF from your computer, breaks
it into pieces, finds the pieces relevant to your question, and answers using
them. We will build it step by step, checking the result each time.

This tutorial continues from Tutorials 1 and 2. You should already have your
`my-rag` folder, your private workspace, and your OpenAI key.

---

## Before we start

Open a terminal (Windows key → type `powershell` → Enter) and go to your
project folder:

```powershell
cd C:\work\playground\rag\tutorials\my-rag
```

Turn the private workspace on:

```powershell
.\venv\Scripts\Activate.ps1
```

Check for `(venv)` at the start of your prompt. Then set your key again
(replace with your real key):

```powershell
$env:OPENAI_API_KEY = "PASTE-YOUR-KEY-HERE"
```

Confirm it:

```powershell
echo $env:OPENAI_API_KEY
```

You should see your key. Ready.

---

## Step 1 — Install a tool that reads PDFs

PDFs are not plain text, so we need a tool to pull the words out of them. It is
called **pypdf**. Type:

```powershell
pip install pypdf
```

Lines scroll by, ending with `Successfully installed pypdf-...`.

---

## Step 2 — Get a PDF to work with

We already have a PDF nearby from earlier experiments. Let's copy it into our
folder so it's easy to reach. Type this as a single line:

```powershell
copy ..\..\wipo_pub_rn2021_18e.pdf document.pdf
```

You should see `1 file(s) copied.`

Let's confirm it's here:

```powershell
dir document.pdf
```

You should see a line listing `document.pdf` with a size. Good — that is the
file we will ask questions about.

> Want to use your own PDF instead? Copy any PDF into this `my-rag` folder and
> rename it to `document.pdf`. The rest of the tutorial works the same. For now,
> we suggest sticking with the provided file so your results match ours.

---

## Step 3 — Read the words out of the PDF

Let's make sure we can get text out of the file before doing anything clever.
Create a new program called `pdf.py`:

```powershell
notepad pdf.py
```

Click **Yes**, then paste:

```python
from pypdf import PdfReader

# Open the PDF and read every page into one big string of text.
reader = PdfReader("document.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text() + "\n"

# Show how much text we got, and a small preview.
print("The PDF has", len(reader.pages), "pages.")
print("We extracted", len(text), "characters of text.")
print("\nFirst 300 characters:\n")
print(text[:300])
```

Save, close, and run:

```powershell
python pdf.py
```

You should see the number of pages, the number of characters extracted, and a
preview of the first bit of text, something like:

```
The PDF has 16 pages.
We extracted 42137 characters of text.

First 300 characters:

...
```

The exact numbers depend on the PDF. The important thing: you extracted many
thousands of characters, and the preview shows real words. You have turned a PDF
into text your program can work with.

---

## Step 4 — Cut the text into bite-sized pieces

The whole PDF is far too long to send to the AI at once, and we don't need all
of it to answer one question anyway. So we cut the text into smaller
**chunks**. Then, just like in Tutorial 2, we can find the few chunks relevant
to a question.

Open the file:

```powershell
notepad pdf.py
```

Add this to the **bottom**:

```python
# Cut the text into chunks of about 800 characters each.
chunk_size = 800
chunks = []
for start in range(0, len(text), chunk_size):
    chunks.append(text[start:start + chunk_size])

print("\nWe cut the text into", len(chunks), "chunks.")
print("\nHere is chunk number 2:\n")
print(chunks[1])
```

Save, close, and run:

```powershell
python pdf.py
```

Below the earlier output you now see how many chunks were made, and the contents
of one chunk, for example:

```
We cut the text into 53 chunks.

Here is chunk number 2:

...
```

Notice each chunk is a manageable slice of the document. We now have a
collection of pieces — much like the list of facts in Tutorial 2, except this
list came from a real file automatically.

---

## Step 5 — Turn the chunks into numbers and search them

This part should feel familiar: it is exactly the retrieval idea from
Tutorial 2, now applied to our PDF chunks. Open the file and add this to the
**bottom**:

```python
from openai import OpenAI
import numpy as np

client = OpenAI()

# Turn a piece of text into a list of numbers (an embedding).
def embed(piece):
    result = client.embeddings.create(
        model="text-embedding-3-small",
        input=piece,
    )
    return np.array(result.data[0].embedding)

# Turn every chunk into numbers. This may take a little while.
print("\nTurning", len(chunks), "chunks into numbers...")
chunk_embeddings = [embed(chunk) for chunk in chunks]
print("Done.")

# Measure similarity between two lists of numbers.
def similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# Ask a question and find the most relevant chunks.
question = "What is this document about?"
question_embedding = embed(question)

scores = [similarity(question_embedding, ce) for ce in chunk_embeddings]

# Pick the three best-matching chunks.
best_indexes = list(np.argsort(scores)[-3:][::-1])
print("\nThe 3 most relevant chunks are numbers:", best_indexes)
```

Save, close, and run:

```powershell
python pdf.py
```

After a pause (while every chunk is turned into numbers), you should see
something like:

```
Turning 53 chunks into numbers...
Done.

The 3 most relevant chunks are numbers: [0, 4, 1]
```

The specific numbers will vary. What matters: your program looked across the
*whole* PDF and picked out the handful of chunks most relevant to the question.
That pause you noticed was the program preparing the entire document for
searching.

---

## Step 6 — Answer the question using the chunks we found

Now we finish the pipeline: gather the best chunks and ask the AI to answer
using them. Open the file and add this to the **bottom**:

```python
# Join the best chunks together into the context we give the AI.
context = "\n\n".join(chunks[i] for i in best_indexes)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "Answer the question using only the context provided. "
                       "If the answer is not in the context, say you don't know.",
        },
        {
            "role": "user",
            "content": f"Context:\n{context}\n\nQuestion: {question}",
        },
    ],
)

print("\nAnswer:")
print(response.choices[0].message.content)
```

Save, close, and run:

```powershell
python pdf.py
```

At the end of the output you now see a written **Answer** to "What is this
document about?", drawn from the chunks the program selected. You just asked a
real PDF a question and got an answer grounded in its actual contents.

---

## Step 7 — Ask your own questions, and repeat

This is the payoff — use it. Open the file, find the `question` line:

```python
question = "What is this document about?"
```

Change it to something you're curious about, for example:

```python
question = "What are the main recommendations in this document?"
```

Save and run again. Watch the same pipeline flow: extract, chunk, turn into
numbers, find the relevant chunks, answer.

Try several different questions. Notice that:

- Questions whose answers are in the document get grounded, specific answers.
- Questions the document doesn't cover get an honest "I don't know", because we
  told the AI to answer only from the context.

Run it as many times as you like. Each run reminds you that the same steps,
every time, produce a reliable result — that is the feeling of a working RAG
system.

---

## What you built

You built a program that:

- **reads** a real PDF from your computer,
- **extracts** its text,
- **cuts** that text into chunks,
- **turns** each chunk into numbers,
- **finds** the chunks most relevant to your question,
- and **answers** using only those chunks.

That is a complete, honest-to-goodness RAG application — the same shape as the
"chat with your documents" tools people use every day. The difference between
yours and a big commercial one is mostly *scale and polish*, not *idea*. You
understand the idea now, because you built each part and watched it work.

---

## Where to go from here

You have finished the RAG tutorials. You have a working program and, more
importantly, a feel for how the pieces fit together. When you are ready to go
further, here are directions worth exploring later (these are topics to *learn
about* next, not steps to do now):

- **Storing the numbers** so you don't recompute them every run (this is what a
  "vector database" does).
- **Smarter chunking** that splits on paragraphs or sentences instead of a fixed
  character count.
- **Showing sources**, so each answer says which part of the document it came
  from.
- **A chat loop**, so you can ask many questions without re-running the program.

Congratulations — you built a RAG system from nothing, one small, reliable step
at a time.
