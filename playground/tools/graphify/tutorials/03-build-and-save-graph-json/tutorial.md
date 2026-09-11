# Build a complete graph.json from a small project

## Where we're going

In this tutorial we will turn a small two-file Python project into a single,
validated **`graph.json`** on disk — the same graph file the Graphify engine
produces and every one of its tools reads. Along the way we will encounter file
nodes, `contains` edges that connect a file to what it defines, a validation pass
that rejects a malformed graph, and the NetworkX *node-link* JSON layout that
makes the file loadable later.

By the end you will run one command, watch it report the graph it wrote, and open
`graph.json` to see your whole project captured as nodes and edges.

## Prerequisites

- Python 3.12 installed (`python --version` should print `Python 3.12.x`).
- The ability to run `pip install` and `python` from your terminal.
- A fresh, empty folder. Create and enter one now:

```
mkdir graphify-build
cd graphify-build
```

Everything else we build from scratch inside this folder. You do **not** need to
have done any other tutorial.

## Step 1 — Install the packages

Install tree-sitter, the Python grammar, and NetworkX (which we use only to
confirm our file loads correctly), pinned to exact versions:

```
pip install tree-sitter==0.26.0 tree-sitter-python==0.25.0 networkx==3.6.1
```

The output should end with a line something like:

```
Successfully installed networkx-3.6.1 tree-sitter-0.26.0 tree-sitter-python-0.25.0
```

## Step 2 — Create the project we will graph

Create two files, exactly as shown.

`orders.py`:

```python
def place_order(item):
    validate(item)
    return charge(item)


def validate(item):
    return item is not None
```

`billing.py`:

```python
def charge(item):
    return "charged"
```

Notice the three relationships hiding in these seven lines: `orders.py`
*contains* `place_order` and `validate`; `place_order` *calls* `validate` in the
**same file**; and `place_order` *calls* `charge`, which lives in **another
file**. By the end, all three will be edges in our graph.

## Step 3 — Extract a file node and its contents

A graph needs a node for the file itself, so we can connect the file to the
functions it defines with a `contains` edge. Create `build_graph.py` with this
content:

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
    file_id = make_id(stem)
    nodes = [{
        "id": file_id,
        "label": source_file,
        "file_type": "code",
        "source_file": source_file,
        "source_location": "L1",
    }]
    edges = []
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
            edges.append({
                "source": file_id,
                "target": fid,
                "relation": "contains",
                "confidence": "EXTRACTED",
                "confidence_score": 1.0,
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
    return nodes, edges, raw_calls


nodes, edges, raw_calls = extract_file("orders.py")
for n in nodes:
    print("NODE", n["id"])
for e in edges:
    print("EDGE", e["source"], "--" + e["relation"] + "-->", e["target"])
print("raw calls:", [rc["callee"] for rc in raw_calls])
```

Run it:

```
python build_graph.py
```

The output should look exactly like this:

```
NODE orders
NODE orders_place_order
NODE orders_validate
EDGE orders --contains--> orders_place_order
EDGE orders --contains--> orders_validate
raw calls: ['validate', 'charge']
```

Notice that we now have a node for the file (`orders`) and a `contains` edge to
each function it defines. The two calls inside `place_order` are still pending
raw calls — we resolve them next.

## Step 4 — Resolve the calls into edges

We reuse the two-tier resolution rule: a call whose target is defined in the same
file becomes an **EXTRACTED** `calls` edge; a call resolved by a unique name
across the project becomes an **INFERRED** one; an ambiguous name produces no
edge.

Add this resolver to `build_graph.py`, just below `extract_file`:

```python
def resolve_calls(all_nodes, all_raw_calls):
    node_ids = {n["id"] for n in all_nodes}
    label_to_ids = {}
    for n in all_nodes:
        if n["label"].endswith(".py"):
            continue
        label_to_ids.setdefault(n["label"], []).append(n["id"])

    edges = []
    for rc in all_raw_calls:
        if rc["callee_local_id"] in node_ids:
            confidence, score, target = "EXTRACTED", 1.0, rc["callee_local_id"]
        else:
            candidates = label_to_ids.get(rc["callee"], [])
            if len(candidates) != 1:
                continue
            confidence, score, target = "INFERRED", 0.85, candidates[0]
        edges.append({
            "source": rc["caller"],
            "target": target,
            "relation": "calls",
            "confidence": confidence,
            "confidence_score": score,
            "source_file": rc["source_file"],
            "source_location": rc["source_location"],
        })
    return edges
```

Notice we skip file nodes (labels ending in `.py`) when building the name index,
so a call can only resolve to a function, never to a file.

## Step 5 — Validate before saving

A graph is only useful if it is well-formed. Before writing anything to disk, we
check every node has the required fields and a legal `file_type`, every edge has
a legal `confidence`, and — most importantly — no edge points at a node that does
not exist. These are the exact rules the Graphify engine enforces.

Add this validation function to `build_graph.py`, just below `resolve_calls`:

```python
VALID_FILE_TYPES = {"code", "document", "paper", "image", "rationale", "concept"}
VALID_CONFIDENCES = {"EXTRACTED", "INFERRED", "AMBIGUOUS"}
REQUIRED_NODE_FIELDS = {"id", "label", "file_type", "source_file"}
REQUIRED_EDGE_FIELDS = {"source", "target", "relation", "confidence", "source_file"}


def validate(nodes, edges):
    node_ids = {n["id"] for n in nodes}
    for n in nodes:
        assert not (REQUIRED_NODE_FIELDS - n.keys()), f"node {n['id']} missing fields"
        assert n["file_type"] in VALID_FILE_TYPES, f"bad file_type: {n['file_type']}"
    for e in edges:
        assert not (REQUIRED_EDGE_FIELDS - e.keys()), "edge missing fields"
        assert e["confidence"] in VALID_CONFIDENCES, f"bad confidence: {e['confidence']}"
        assert e["source"] in node_ids, f"dangling source {e['source']}"
        assert e["target"] in node_ids, f"dangling target {e['target']}"
```

## Step 6 — Build the whole project and write graph.json

Now we assemble everything: walk every `.py` file, collect nodes and edges,
resolve calls, validate, and write the result in NetworkX's *node-link* format
(a top-level object with `nodes` and `links` arrays) so the graph can be loaded
back later.

Add this final block to the bottom of `build_graph.py` (remove the temporary
print block from Step 3 first — everything from `nodes, edges, raw_calls =
extract_file("orders.py")` down to the `print("raw calls:"...)` line):

```python
def build():
    all_nodes, all_edges, all_raw = [], [], []
    seen = set()
    for path in sorted(glob.glob("*.py")):
        if path == "build_graph.py":
            continue
        nodes, edges, raw = extract_file(path)
        for n in nodes:
            if n["id"] not in seen:
                seen.add(n["id"])
                all_nodes.append(n)
        all_edges.extend(edges)
        all_raw.extend(raw)
    all_edges.extend(resolve_calls(all_nodes, all_raw))
    validate(all_nodes, all_edges)
    graph = {
        "directed": True,
        "multigraph": False,
        "graph": {},
        "nodes": all_nodes,
        "links": all_edges,
    }
    with open("graph.json", "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=2)
    return all_nodes, all_edges


nodes, edges = build()
print(f"wrote graph.json: {len(nodes)} nodes, {len(edges)} edges")
extracted = sum(1 for e in edges if e["confidence"] == "EXTRACTED")
inferred = sum(1 for e in edges if e["confidence"] == "INFERRED")
print(f"  EXTRACTED: {extracted}")
print(f"  INFERRED:  {inferred}")
```

Run the finished builder:

```
python build_graph.py
```

The output should look exactly like this:

```
wrote graph.json: 5 nodes, 5 edges
  EXTRACTED: 4
  INFERRED:  1
```

Notice the tallies. We have 5 nodes (two file nodes plus three functions) and 5
edges. Four are EXTRACTED — three `contains` edges plus the same-file call
`place_order -> validate`. Exactly one is INFERRED — the cross-file call
`place_order -> charge`. The validation pass ran silently, which means the graph
is well-formed; if any edge had pointed at a missing node, the run would have
stopped with an `AssertionError`.

## Step 7 — Look at what you wrote and confirm it loads

Let's inspect the file. Open `graph.json` — the top of it should look like this:

```json
{
  "directed": true,
  "multigraph": false,
  "graph": {},
  "nodes": [
    {
      "id": "billing",
      "label": "billing.py",
      "file_type": "code",
      "source_file": "billing.py",
      "source_location": "L1"
    },
```

Now let's prove the file is a genuine, loadable graph. Create `check.py`:

```python
import json
import networkx as nx
from networkx.readwrite import json_graph

data = json.load(open("graph.json", encoding="utf-8"))
G = json_graph.node_link_graph(data, edges="links")
print("loaded:", G.number_of_nodes(), "nodes,", G.number_of_edges(), "edges")
for source, target, d in G.edges(data=True):
    print(f"  {source} --{d['relation']}[{d['confidence']}]--> {target}")
```

Run it:

```
python check.py
```

The output should look exactly like this:

```
loaded: 5 nodes, 5 edges
  orders --contains[EXTRACTED]--> orders_place_order
  orders --contains[EXTRACTED]--> orders_validate
  orders_place_order --calls[EXTRACTED]--> orders_validate
  orders_place_order --calls[INFERRED]--> billing_charge
  billing --contains[EXTRACTED]--> billing_charge
```

Notice that NetworkX read your file back with no changes needed, and every
relationship is present: the file-to-function `contains` edges, the same-file
EXTRACTED call, and the cross-file INFERRED call. Run `python build_graph.py`
once more to confirm the whole build is repeatable — the reported counts are
identical every time.

## What you accomplished

You built a complete graph builder. It walks a project, creates file and function
nodes, links them with `contains` edges, resolves calls into the EXTRACTED and
INFERRED tiers, validates the whole thing against a real schema, and writes a
loadable `graph.json` in NetworkX's node-link format. That single file is the
finished product of the Graphify extraction pipeline — a project's structure,
captured and ready to query.

## Next steps / further reading

- Continue with **[04 — Query, path, and explain your graph](04-query-path-explain.md)**
  to ask your graph questions: find a symbol, trace a path between two functions,
  and list what a node connects to.
- The real builder (with cross-file deduplication and semantic merging) lives in
  `graphify/build.py`; the schema it enforces is in `graphify/validate.py`.
- NetworkX node-link format:
  https://networkx.org/documentation/stable/reference/readwrite/json_graph.html
