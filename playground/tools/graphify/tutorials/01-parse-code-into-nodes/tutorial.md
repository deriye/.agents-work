# Parse a Python file into graph nodes with tree-sitter

## Where we're going

In this tutorial we will build a small program that reads a real Python source
file, parses it with tree-sitter, and turns every function, class, and method it
finds into a **graph node** — the same kind of node the Graphify engine stores.
Along the way we will encounter tree-sitter's parser and syntax tree, node
"fields", a stable node-ID scheme, and the node record shape Graphify uses
(`id`, `label`, `file_type`, `source_file`, `source_location`).

By the end you will run one command and watch your own code print a clean list of
nodes extracted from a file you wrote seconds earlier.

## Prerequisites

- Python 3.12 installed (`python --version` should print `Python 3.12.x`).
- The ability to run `pip install` and `python` from your terminal.
- A fresh, empty folder to work in. Create and enter one now:

```
mkdir graphify-nodes
cd graphify-nodes
```

Everything else we build from scratch inside this folder.

## Step 1 — Install the two parsing packages

First, install the tree-sitter runtime and the pre-built Python grammar, pinned
to exact versions so your output matches this tutorial:

```
pip install tree-sitter==0.26.0 tree-sitter-python==0.25.0
```

The output should end with a line something like:

```
Successfully installed tree-sitter-0.26.0 tree-sitter-python-0.25.0
```

If instead you see `ERROR: Could not find a version that satisfies...`, your
Python is older than 3.9 — check `python --version` before continuing.

## Step 2 — Create a sample file to parse

We need something to extract from. Create a file called `sample.py` with exactly
this content:

```python
def greet(name):
    return welcome(name)


class Dog:
    def bark(self):
        return "woof"


def welcome(name):
    return "hi " + name
```

Notice that `sample.py` has two top-level functions (`greet`, `welcome`), one
class (`Dog`), and one method (`bark`). We will turn each of these four things
into a node.

## Step 3 — Parse the file and print the syntax tree

Now let's confirm tree-sitter can read our file. Create a file called
`extract.py` with this content:

```python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

source = open("sample.py", "rb").read()
tree = parser.parse(source)

for child in tree.root_node.children:
    print(child.type)
```

Run it:

```
python extract.py
```

The output should look exactly like this:

```
function_definition
class_definition
function_definition
```

Notice that tree-sitter reports the *type* of each top-level construct.
`greet` and `welcome` are `function_definition`; `Dog` is `class_definition`.
The method `bark` does not appear yet — it lives *inside* the class node, and
we will reach into it in Step 5.

If you see `ModuleNotFoundError: No module named 'tree_sitter_python'`, Step 1
did not complete — re-run the install command.

## Step 4 — Read a node's name and line number

A node type alone is not useful; we need the *name* of each function and *where*
it lives. tree-sitter exposes named parts of a construct as **fields**. The name
of a function or class is the `name` field.

Replace the whole body of `extract.py` with this:

```python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)

source = open("sample.py", "rb").read()
tree = parser.parse(source)

for child in tree.root_node.children:
    if child.type in ("function_definition", "class_definition"):
        name_node = child.child_by_field_name("name")
        name = name_node.text.decode()
        line = child.start_point[0] + 1
        print(f"{child.type}: {name} (line {line})")
```

Run it again:

```
python extract.py
```

The output should look exactly like this:

```
function_definition: greet (line 1)
class_definition: Dog (line 5)
function_definition: welcome (line 10)
```

Notice two things. First, `child_by_field_name("name")` pulled the identifier
out for us. Second, `start_point[0]` is a **zero-based** row, so we add 1 to get
the human line number you see in an editor.

## Step 5 — Reach inside the class to find its method

The method `bark` is a `function_definition` nested inside the `Dog` class node.
To find it, we look at the class node's `body` field and walk its children.

Replace the loop at the bottom of `extract.py` (everything from `for child` to
the end) with this:

```python
for child in tree.root_node.children:
    if child.type == "function_definition":
        name = child.child_by_field_name("name").text.decode()
        line = child.start_point[0] + 1
        print(f"function: {name} (line {line})")
    elif child.type == "class_definition":
        class_name = child.child_by_field_name("name").text.decode()
        class_line = child.start_point[0] + 1
        print(f"class: {class_name} (line {class_line})")
        body = child.child_by_field_name("body")
        for member in body.children:
            if member.type == "function_definition":
                method = member.child_by_field_name("name").text.decode()
                method_line = member.start_point[0] + 1
                print(f"  method: {method} (line {method_line})")
```

Run it:

```
python extract.py
```

The output should look exactly like this:

```
function: greet (line 1)
class: Dog (line 5)
  method: bark (line 6)
function: welcome (line 10)
```

Notice that `bark` now appears, indented, under `Dog`. We have successfully
reached *inside* the class node and pulled out its method. The two top-level
functions (`greet`, `welcome`) print flush-left, while `bark` is nested under
its class — exactly the containment structure we will turn into edges next.

## Step 6 — Give every node a stable ID

Graphify identifies each node with a normalized string ID so the same symbol
always gets the same ID everywhere it is referenced. The rule: lowercase the
text, then replace every run of non-word characters with a single underscore,
and trim stray underscores from the ends.

Add this helper near the top of `extract.py`, right after the `parser = ...`
line:

```python
import re


def make_id(*parts):
    raw = ".".join(str(p) for p in parts)
    lowered = raw.casefold()
    cleaned = re.sub(r"[^\w]+", "_", lowered, flags=re.UNICODE)
    cleaned = re.sub(r"_+", "_", cleaned)
    return cleaned.strip("_")
```

Let's check it does what we expect. Add these two lines temporarily at the very
end of the file:

```python
print(make_id("sample", "greet"))
print(make_id("sample", "Dog", "bark"))
```

Run it:

```
python extract.py
```

Among the earlier output you should now also see these two final lines:

```
sample_greet
sample_dog_bark
```

Notice how `make_id` combined the file stem, the class, and the method into one
predictable ID, and how `Dog` was lowered to `dog`. A top-level function is
keyed by *file + name*; a method is keyed by *file + class + name*. Now delete
those two temporary `print(make_id(...))` lines — we are about to build the real
node records.

## Step 7 — Emit real node records

Now we assemble the four Graphify-shaped node records. Each record has an `id`, a
human `label`, a `file_type` (our source is code), a `source_file`, and a
`source_location` written as `L<line>`.

Replace the *entire* contents of `extract.py` with this final version:

```python
import re
import json
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def make_id(*parts):
    raw = ".".join(str(p) for p in parts)
    cleaned = re.sub(r"[^\w]+", "_", raw.casefold(), flags=re.UNICODE)
    return re.sub(r"_+", "_", cleaned).strip("_")


def node_record(node_id, label, source_file, line):
    return {
        "id": node_id,
        "label": label,
        "file_type": "code",
        "source_file": source_file,
        "source_location": f"L{line}",
    }


def extract_nodes(source_file):
    source = open(source_file, "rb").read()
    tree = parser.parse(source)
    stem = source_file.rsplit(".", 1)[0]
    nodes = []
    for child in tree.root_node.children:
        if child.type == "function_definition":
            name = child.child_by_field_name("name").text.decode()
            line = child.start_point[0] + 1
            nodes.append(node_record(make_id(stem, name), name, source_file, line))
        elif child.type == "class_definition":
            class_name = child.child_by_field_name("name").text.decode()
            class_line = child.start_point[0] + 1
            class_id = make_id(stem, class_name)
            nodes.append(node_record(class_id, class_name, source_file, class_line))
            body = child.child_by_field_name("body")
            for member in body.children:
                if member.type == "function_definition":
                    method = member.child_by_field_name("name").text.decode()
                    method_line = member.start_point[0] + 1
                    method_id = make_id(stem, class_name, method)
                    nodes.append(
                        node_record(method_id, method, source_file, method_line)
                    )
    return nodes


nodes = extract_nodes("sample.py")
print(json.dumps(nodes, indent=2))
```

Run the finished extractor:

```
python extract.py
```

The output should look exactly like this:

```
[
  {
    "id": "sample_greet",
    "label": "greet",
    "file_type": "code",
    "source_file": "sample.py",
    "source_location": "L1"
  },
  {
    "id": "sample_dog",
    "label": "Dog",
    "file_type": "code",
    "source_file": "sample.py",
    "source_location": "L5"
  },
  {
    "id": "sample_dog_bark",
    "label": "bark",
    "file_type": "code",
    "source_file": "sample.py",
    "source_location": "L6"
  },
  {
    "id": "sample_welcome",
    "label": "welcome",
    "file_type": "code",
    "source_file": "sample.py",
    "source_location": "L10"
  }
]
```

Notice that all four constructs are present — the two top-level functions, the
class, and its method — each with a stable ID, a label, and the exact line it was
defined on. This is precisely the node shape the Graphify engine builds before it
starts connecting anything together.

Let's confirm it really is repeatable: run `python extract.py` a second time.
The output is byte-for-byte identical. Because `make_id` is deterministic, the
same file always produces the same IDs.

## What you accomplished

You built a working code extractor. It parses a real Python file with
tree-sitter, walks the syntax tree, reaches inside a class to find its methods,
and emits clean, stably-identified node records in Graphify's own format. That
list of nodes is the raw material of a code knowledge graph — every function,
class, and method now has an identity the rest of the engine can point at.

## Next steps / further reading

- Continue with **[02 — Resolve calls into graph edges](02-resolve-calls-into-edges.md)**
  to connect these nodes: turn `greet` calling `welcome` into a real edge, and
  meet Graphify's EXTRACTED vs. INFERRED confidence tiers.
- tree-sitter Python bindings: https://github.com/tree-sitter/py-tree-sitter
- The Graphify node schema this mirrors lives in `graphify/validate.py`
  (`REQUIRED_NODE_FIELDS`, `VALID_FILE_TYPES`) and the ID rule in
  `graphify/ids.py` (`make_id`).
