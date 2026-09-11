# Tutorial 1 — Chat with your first document

In this tutorial we will build a tiny program that reads one paragraph of text
and answers questions about it. This is the smallest complete version of a
technique called **Retrieval-Augmented Generation (RAG)**. By the end, you will
have run a real AI question-and-answer program on your own computer, and you
will have seen every part of it work.

We will install Python, set up an account key so our program can talk to the
AI, write about fifteen lines of code, and ask it a question. Along the way we
will meet the tools you will use in the next tutorials too.

Take your time. Do each step in order, and check the result before moving on.

---

## Before we start

You need a computer where you can install programs, and an internet
connection. Everything else, we will set up together.

We are working on Windows. When we say "open a terminal", we mean the program
called **PowerShell**:

1. Press the **Windows key** on your keyboard.
2. Type `powershell`.
3. Press **Enter**.

A window with a dark background and a blinking cursor opens. This is your
terminal. This is where we will type commands. Leave it open.

> We use the terminal because it lets us run our program and see its messages
> directly. (There is a longer story about terminals, but we don't need it now.)

---

## Step 1 — Check that Python is installed

Our program is written in **Python**, a popular language for AI work. Let's see
if your computer already has it.

In the terminal, type this exactly, then press **Enter**:

```powershell
python --version
```

You should see something like:

```
Python 3.12.1
```

The exact numbers don't matter, as long as the first number is **3** and the
second is **10 or higher**.

If instead you see an error, or a message about the Microsoft Store, then
Python is not installed yet. Do this:

1. Go to <https://www.python.org/downloads/> in your web browser.
2. Click the big yellow **Download Python** button.
3. Open the file you downloaded.
4. **Important:** on the first screen, tick the box that says
   **"Add python.exe to PATH"** at the bottom. This one tick saves a lot of
   trouble later.
5. Click **Install Now** and wait for it to finish.
6. **Close your terminal and open a new one** (Windows key → type `powershell`
   → Enter), then run `python --version` again.

Keep going once you see a version number.

---

## Step 2 — Make a folder for our work

We will keep everything for these tutorials in one place. In the terminal, type
these two commands, pressing **Enter** after each:

```powershell
cd C:\work\playground\rag\tutorials
```

```powershell
mkdir my-rag
```

The first command moves us into the tutorials folder. The second makes a new
folder called `my-rag` inside it. You will see a short confirmation listing the
new folder.

Now move into that new folder:

```powershell
cd my-rag
```

Notice that the text to the left of your cursor now ends with `my-rag`. That
tells you which folder you are in. We will do all our work here.

---

## Step 3 — Create a private workspace for Python

Python projects each get their own private space for the extra tools they need.
This keeps projects from interfering with each other. Let's create one. Type:

```powershell
python -m venv venv
```

Nothing visible happens for a few seconds, then your cursor returns. A new
folder called `venv` was created. That is the private space.

Now we **activate** it. Type:

```powershell
.\venv\Scripts\Activate.ps1
```

Notice that your prompt now begins with `(venv)`. That little `(venv)` is your
sign that the private space is switched on. It should stay there for the rest of
this tutorial.

> If you see a red error mentioning "running scripts is disabled", run this one
> command, then try the activate command again:
>
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
> ```
>
> This permits scripts just for this terminal window.

---

## Step 4 — Install the tool that talks to the AI

We need one tool: the official OpenAI library. With `(venv)` showing in your
prompt, type:

```powershell
pip install openai
```

You will see several lines of text scroll by as it downloads and installs. This
takes a few moments. When it finishes, the last line says something like
`Successfully installed openai-...`. Your cursor returns.

---

## Step 5 — Get a key so the program is allowed to talk to the AI

The AI runs on OpenAI's computers, not yours. To use it, you need a **key** — a
long secret password that identifies you. Let's get one.

1. In your web browser, go to <https://platform.openai.com/signup> and create an
   account (or log in if you have one).
2. You must add a small amount of billing credit before the key will work. Go to
   <https://platform.openai.com/settings/organization/billing/overview> and add
   a payment method, then add **$5** of credit. This is enough for hundreds of
   questions in these tutorials.
3. Now go to <https://platform.openai.com/api-keys>.
4. Click **Create new secret key**, give it any name, and click **Create**.
5. Click **Copy** to copy the key. It starts with `sk-`.

**Keep this key private**, like a password. Do not share it or post it online.

Now we hand the key to our terminal. In the terminal, type the following, but
replace `PASTE-YOUR-KEY-HERE` with the key you just copied (keep the quotes):

```powershell
$env:OPENAI_API_KEY = "PASTE-YOUR-KEY-HERE"
```

Press **Enter**. Nothing visible happens — that is correct. The key is now
available to programs in this terminal window.

> This setting lasts only as long as this terminal window is open. If you close
> it and come back later, you will run this one line again. We do it this way so
> your secret key never gets written into a file by accident.

Let's check the key was stored. Type:

```powershell
echo $env:OPENAI_API_KEY
```

You should see your key printed back (starting with `sk-`). Good.

---

## Step 6 — Write the program

Now we write our program. We will create a file called `chat.py`.

Open the file in Notepad by typing:

```powershell
notepad chat.py
```

Notepad asks if you want to create a new file — click **Yes**.

Carefully copy the code below and paste it into Notepad. Don't worry about
understanding every line yet — we will look at what each part does *after* we
see it work.

```python
from openai import OpenAI

# This is the document we want to ask questions about.
document = """
The Apollo 11 mission launched on July 16, 1969. Astronauts Neil Armstrong,
Buzz Aldrin, and Michael Collins were on board. On July 20, 1969, Neil
Armstrong became the first person to walk on the Moon. Michael Collins stayed
in orbit around the Moon and did not walk on its surface.
"""

# The question we want answered.
question = "Who was the first person to walk on the Moon?"

# Connect to the AI.
client = OpenAI()

# Give the AI the document and the question together.
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system",
            "content": "Answer the question using only the document provided. "
                       "If the answer is not in the document, say you don't know.",
        },
        {
            "role": "user",
            "content": f"Document:\n{document}\n\nQuestion: {question}",
        },
    ],
)

# Print the AI's answer.
print(response.choices[0].message.content)
```

Now save the file: in Notepad click **File → Save**, then close Notepad.

---

## Step 7 — Run it

Back in the terminal (make sure `(venv)` still shows), type:

```powershell
python chat.py
```

After a moment, you should see an answer something like:

```
Neil Armstrong was the first person to walk on the Moon.
```

**You just ran your first RAG program.** You gave the computer a document and a
question, and it answered using that document.

---

## Step 8 — Repeat, and watch what changes

Learning sticks when we try things and watch the result. Let's change the
question and run again.

Open the file again:

```powershell
notepad chat.py
```

Find the `question` line and change it to:

```python
question = "Who stayed in orbit and did not walk on the Moon?"
```

Save, close Notepad, and run it again:

```powershell
python chat.py
```

This time the answer should mention **Michael Collins**. Notice that we changed
*only the question* — the document stayed the same — and the AI found the right
answer inside the same paragraph.

Now try one more. Change the question to something the document does **not**
answer:

```python
question = "What did the astronauts eat for breakfast?"
```

Save and run again. This time the AI should say it doesn't know, because we told
it in the program to answer *only* from the document. Notice how the AI stayed
honest instead of making something up. That honesty is a big part of why RAG is
useful.

Run the program a few more times with different questions of your own. Watch how
the answer changes with the question but stays grounded in the paragraph.

---

## What you built

Let's admire what you have. You built a small program that:

- holds a **document** (our paragraph about Apollo 11),
- takes a **question**,
- sends both to an AI with an instruction to answer *only from the document*,
- and prints the **answer**.

This is the heart of RAG: **give the AI the right text, then ask your question
about it.** Everything in the next tutorials is about doing this well when you
have *lots* of text and can't just paste it all in at once.

You also learned to open a terminal, check and install Python, create and
activate a private workspace, install a tool with `pip`, keep a secret key, and
run a Python program. You will use all of these again.

---

## Coming up next

Right now we handed the AI the *whole* document every time. That works for one
paragraph, but not for a whole book. In
**[Tutorial 2 — Search across many documents](02-search-across-many-documents.md)**,
we will store many pieces of text and teach the program to *find* the few
relevant pieces before asking its question.

Before you move on, close Notepad and leave your terminal open — we will
continue from the same `my-rag` folder.
