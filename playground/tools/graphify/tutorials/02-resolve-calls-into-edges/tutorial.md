# Turn function calls into graph edges (EXTRACTED and INFERRED)

## Where we're going

In this tutorial we will build an extractor that finds the *calls* between Python
functions and turns them into **graph edges** — the connections that make a pile
of nodes into an actual graph. We will handle calls within a single file and
calls that cross from one file to another. Along the way we will encounter
tree-sitter `call` nodes, "raw calls", a two-step resolver, and Graphify's two
confidence tiers: **EXTRACTED** (a call we resolved with certainty) and
**INFERRED** (a call we resolved by name alone). We will also meet the
*ambiguity guard* that stops the graph from inventing false connections.

By the end you will run one command over three source files and watch it emit one
EXTRACTED edge, one INFERRED edge, and deliberately *no* edge for a name that is
too ambiguous to trust.

## Prerequisites

- Python 3.12 installed (`python --version` should print `Python 3.12.x`).
- The ability to run `pip install` and `python` from your terminal.
- A fresh, empty folder. Create and enter one now:

```
mkdir graphify-edges
cd graphify-edges
```

Everything else we build from scratch inside this folder. You do **not** need to
have done any other tutorial.

## Step 1 — Install the parsing packages

Install the tree-sitter runtime and the Python grammar, pinned to exact
versions:

```
pip install tree-sitter==0.26.0 tree-sitter-python==0.25.0
```

The output should end with a line something like:

```
Successfully installed tree-sitter-0.26.0 tree-sitter-python-0.25.0
```

## Step 2 — Create three source files to connect

We need code with calls in it. Create these three files, exactly as shown.

`greetings.py`:

```python
def welcome(name):
    return "hi " + name
```

`app.py`:

```python
def greet(name):
    return welcome(name)


def farewell(name):
    return goodbye(name)
```

`other.py`:

```python
def goodbye(name):
    return "bye " + name


def welcome(guest):
    return "greetings " + guest
```

Notice three deliberate situations. `app.greet` calls `welcome`, which is defined
in *another* file (`greetings.py`) — but the name `welcome` **also** exists in
`other.py`. And `app.farewell` calls `goodbye`, which is defined in exactly one
place (`other.py`). We will watch our resolver treat each case differently.

## Step 3 — Find the calls inside a function

First, let's confirm tree-sitter can spot a call. A function call shows up in the
syntax tree as a `call` node, whose `function` field holds the name being called.

Create `extract.py` with this content:

```python
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def find_calls(node):
    calls = []
    if node.type == "call":
        fnode = node.child_by_field_name("function")
        if fnode is not None and fnode.type == "identifier":
            calls.append((fnode.text.decode(), node.start_point[0] + 1))
    for child in node.children:
        calls.extend(find_calls(child))
    return calls


source = open("app.py", "rb").read()
tree = parser.parse(source)
print(find_calls(tree.root_node))
```

Run it:

```
python extract.py
```

The output should look exactly like this:

```
[('welcome', 2), ('goodbye', 6)]
```

Notice that `find_calls` walks the tree recursively and reports each called name
with the line the call happens on. We only keep plain-identifier calls (like
`welcome(...)`) and ignore attribute calls (like `obj.method(...)`) — the same
conservative choice the real engine makes to avoid guessing.

## Step 4 — Extract nodes and record raw calls per file

A call we *find* is not yet a call we can *connect*: when we first see
`welcome(name)` inside `app.py`, we do not yet know which `welcome` it means. So
we do what Graphify does — record each call as a **raw call** (caller, called
name, location) and resolve it later, once every file's nodes exist.

Replace the entire contents of `extract.py` with this:

```python
import re
import json
import glob
import tree_sitter_python as tspython
from tree_sitter import Language, Parser

PY_LANGUAGE = Language(tspython.language())
parser = Parser(PY_LANGUAGE)


def make_id(*parts):
    raw = ".".join(str(p) for p in parts)
    cleaned = re.sub(r"[^\w]+", "_", raw.casefold(), flags=re.UNICODE)
    return re.sub(r"_+", "_", cleaned).strip("_")


def find_calls(node):
    calls = []
    if node.type == "call":
        fnode = node.child_by_field_name("function")
        if fnode is not None and fnode.type == "identifier":
            calls.append((fnode.text.decode(), node.start_point[0] + 1))
    for child in node.children:
        calls.extend(find_calls(child))
    return calls


def extract_file(source_file):
    source = open(source_file, "rb").read()
    tree = parser.parse(source)
    stem = source_file.rsplit(".", 1)[0]
    nodes = []
    raw_calls = []
    for child in tree.root_node.children:
        if child.type == "function_definition":
            name = child.child_by_field_name("name").text.decode()
            line = child.start_point[0] + 1
            fid = make_id(stem, name)
            nodes.append({
                "id": fid,
                "label": name,
                "file_type": "code",
                "source_file": source_file,
                "source_location": f"L{line}",
            })
            for callee, call_line in find_calls(child):
                raw_calls.append({
                    "caller": fid,
                    "callee": callee,
                    "callee_local_id": make_id(stem, callee),
                    "source_file": source_file,
                    "source_location": f"L{call_line}",
                })
    return nodes, raw_calls


all_nodes = []
all_raw_calls = []
for path in sorted(glob.glob("*.py")):
    if path == "extract.py":
        continue
    nodes, raw_calls = extract_file(path)
    all_nodes.extend(nodes)
    all_raw_calls.extend(raw_calls)

print(f"nodes: {len(all_nodes)}")
print(f"raw calls: {len(all_raw_calls)}")
for rc in all_raw_calls:
    print(f"  {rc['caller']} -> {rc['callee']} (at {rc['source_location']})")
```

Run it:

```
python extract.py
```

The output should look exactly like this:

```
nodes: 5
raw calls: 2
  app_greet -> welcome (at L2)
  app_farewell -> goodbye (at L6)
```

Notice we collected 5 function nodes across all three files, and 2 pending raw
calls. Neither raw call is an edge yet — each is a *question* ("which `welcome`?
which `goodbye`?") we will answer in the next two steps.

## Step 5 — Resolve same-file calls as EXTRACTED

The easiest calls to trust are the ones whose target is defined in the *same
file* as the caller: there is no ambiguity, so we mark them **EXTRACTED** with
full confidence. We detect this case by checking whether the caller's own-file ID
for the callee (`callee_local_id`) actually exists as a node.

Add this resolver function to `extract.py`, just below `extract_file`:

```python
def resolve(all_nodes, all_raw_calls):
    node_ids = {n["id"] for n in all_nodes}
    edges = []
    unresolved = []
    for rc in all_raw_calls:
        if rc["callee_local_id"] in node_ids:
            edges.append({
                "source": rc["caller"],
                "target": rc["callee_local_id"],
                "relation": "calls",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
                "source_file": rc["source_file"],
                "source_location": rc["source_location"],
            })
        else:
            unresolved.append(rc)
    return edges, unresolved
```

Now replace the printing block at the bottom (everything from `print(f"nodes:`
onward) with:

```python
edges, unresolved = resolve(all_nodes, all_raw_calls)
print(f"EXTRACTED edges: {len(edges)}")
for e in edges:
    print(f"  {e['source']} --calls[{e['confidence']}]--> {e['target']}")
print(f"still unresolved: {len(unresolved)}")
```

Run it:

```
python extract.py
```

The output should look exactly like this:

```
EXTRACTED edges: 0
still unresolved: 2
```

Notice that *neither* call resolved here — and that is correct. Both `welcome`
and `goodbye` are called from `app.py` but defined in *other* files, so neither
matches a same-file node. Same-file resolution is the strict, certain case; our
two calls are cross-file, so they fall through to the next step. (If your own
project had a call to a function in the same file, it would appear here as an
EXTRACTED edge with score 1.0.)

## Step 6 — Resolve cross-file calls as INFERRED (with an ambiguity guard)

For the calls that did not resolve locally, we fall back to matching by **name
across the whole project**. This is less certain than a same-file match, so we
mark these edges **INFERRED**. Crucially, we only create the edge when the name
matches *exactly one* definition in the entire project. If two functions share
the name, we cannot know which one is meant — so we create **no** edge rather
than a wrong one. This is the *ambiguity guard*, and it is what keeps a graph
honest.

Extend the `resolve` function so its `else` branch (the `unresolved.append(rc)`
line) is replaced by cross-file name resolution. The full updated function is:

```python
def resolve(all_nodes, all_raw_calls):
    node_ids = {n["id"] for n in all_nodes}
    label_to_ids = {}
    for n in all_nodes:
        label_to_ids.setdefault(n["label"], []).append(n["id"])

    edges = []
    dropped = []
    for rc in all_raw_calls:
        if rc["callee_local_id"] in node_ids:
            edges.append({
                "source": rc["caller"],
                "target": rc["callee_local_id"],
                "relation": "calls",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
                "source_file": rc["source_file"],
                "source_location": rc["source_location"],
            })
            continue

        candidates = label_to_ids.get(rc["callee"], [])
        if len(candidates) == 1:
            edges.append({
                "source": rc["caller"],
                "target": candidates[0],
                "relation": "calls",
                "confidence": "INFERRED",
                "confidence_score": 0.85,
                "source_file": rc["source_file"],
                "source_location": rc["source_location"],
            })
        else:
            dropped.append((rc["callee"], len(candidates)))
    return edges, dropped
```

Replace the printing block at the bottom with this final version:

```python
edges, dropped = resolve(all_nodes, all_raw_calls)
print(json.dumps(edges, indent=2))
print("---")
for name, count in dropped:
    print(f"dropped ambiguous call to '{name}' ({count} candidates)")
```

Run the finished resolver:

```
python extract.py
```

The output should look exactly like this:

```
[
  {
    "source": "app_farewell",
    "target": "other_goodbye",
    "relation": "calls",
    "confidence": "INFERRED",
    "confidence_score": 0.85,
    "source_file": "app.py",
    "source_location": "L6"
  }
]
---
dropped ambiguous call to 'welcome' (2 candidates)
```

Look closely at what happened. The call `app_farewell -> goodbye` resolved to
`other_goodbye`: `goodbye` is defined in exactly one place, so we confidently
emit an **INFERRED** edge with score 0.85. But the call to `welcome` was
**dropped**: because `welcome` is defined in both `greetings.py` and `other.py`,
our guard refused to guess. That single dropped edge is the whole point — the
graph would rather show nothing than show a fabricated connection.

Let's confirm it is stable: run `python extract.py` again. The output is
identical every time, because both resolution and `make_id` are deterministic.

## What you accomplished

You built a two-stage call resolver — the core of a code graph. It records raw
calls while parsing, then resolves them in two tiers: **EXTRACTED** for the
certain same-file case, and **INFERRED** for a cross-file name match — but only
when exactly one candidate exists. You saw the ambiguity guard in action,
refusing to connect a name shared by two functions. These are exactly the
confidence tiers and the god-node guard that the Graphify engine uses to keep its
graphs trustworthy.

## Next steps / further reading

- Continue with **[03 — Build and save graph.json](03-build-and-save-graph-json.md)**
  to combine nodes and edges into a single graph file on disk, with validation.
- The real resolver, with import-evidence promotion (a cross-file call *backed by
  an import* is upgraded from INFERRED to EXTRACTED) and per-language passes,
  lives in `graphify/extract.py`.
- The confidence tiers and their allowed values are defined in
  `graphify/validate.py` (`VALID_CONFIDENCES = {EXTRACTED, INFERRED, AMBIGUOUS}`).
