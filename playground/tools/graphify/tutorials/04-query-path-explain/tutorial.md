# Query, path, and explain your graph

## Where we're going

In the previous tutorials you built a `graph.json` — a file full of nodes and
edges describing a small Python project. A graph you cannot ask questions of is
just a file. In this tutorial we will build a small command-line tool that
**loads that graph and answers three kinds of question about it**, exactly the
way the Graphify engine does:

- **find** — locate a symbol by name, using a tiered matcher (exact, then
  prefix, then substring).
- **path** — trace the shortest directed route from one function to another and
  print each hop with its relation and confidence.
- **explain** — show a single node together with everything it points to and
  everything that points at it.

By the end you will type `python query.py path place_order charge` and watch your
own tool draw the call chain across two files.

## Prerequisites

- Python 3.12 installed (`python --version` should print `Python 3.12.x`).
- The ability to run `pip install` and `python` from your terminal.
- A fresh, empty folder to work in. Create and enter one now:

```
mkdir graphify-query
cd graphify-query
```

Everything else we build from scratch inside this folder. You do **not** need to
have completed the earlier tutorials — we will create the graph file we query in
Step 2.

## Step 1 — Install NetworkX

We need one package: NetworkX, the graph library Graphify uses to hold and
traverse graphs in memory. Pin the exact version so your output matches this
tutorial:

```
pip install networkx==3.6.1
```

The output should end with a line something like:

```
Successfully installed networkx-3.6.1
```

## Step 2 — Create the graph to query

Normally this file is produced by the extractor you build in tutorials 1–3. So
this tutorial stands on its own, we will write a small, ready-made `graph.json`
by hand. It describes two files — `orders.py` and `billing.py` — with three
functions and five relationships between them.

Create `graph.json` with exactly this content:

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
    {
      "id": "billing_charge",
      "label": "charge",
      "file_type": "code",
      "source_file": "billing.py",
      "source_location": "L1"
    },
    {
      "id": "orders",
      "label": "orders.py",
      "file_type": "code",
      "source_file": "orders.py",
      "source_location": "L1"
    },
    {
      "id": "orders_place_order",
      "label": "place_order",
      "file_type": "code",
      "source_file": "orders.py",
      "source_location": "L1"
    },
    {
      "id": "orders_validate",
      "label": "validate",
      "file_type": "code",
      "source_file": "orders.py",
      "source_location": "L5"
    }
  ],
  "links": [
    {
      "source": "orders",
      "target": "orders_place_order",
      "relation": "contains",
      "confidence": "EXTRACTED",
      "source_file": "orders.py"
    },
    {
      "source": "orders",
      "target": "orders_validate",
      "relation": "contains",
      "confidence": "EXTRACTED",
      "source_file": "orders.py"
    },
    {
      "source": "orders_place_order",
      "target": "orders_validate",
      "relation": "calls",
      "confidence": "EXTRACTED",
      "source_file": "orders.py"
    },
    {
      "source": "orders_place_order",
      "target": "billing_charge",
      "relation": "calls",
      "confidence": "INFERRED",
      "source_file": "orders.py"
    },
    {
      "source": "billing",
      "target": "billing_charge",
      "relation": "contains",
      "confidence": "EXTRACTED",
      "source_file": "billing.py"
    }
  ]
}
```

This is the same node-link shape the builder writes: a top-level object with a
`nodes` array and a `links` array. Each node carries an `id`, a human-readable
`label`, and where it came from; each link records its `relation` (`contains` or
`calls`) and its `confidence` (`EXTRACTED` for a certain fact, `INFERRED` for a
cross-file guess resolved by name).

## Step 3 — Load the graph

Create `query.py` and start it by loading the file into a NetworkX directed
graph. NetworkX has a reader for exactly this node-link format; we tell it the
edges live under the `links` key:

```python
import sys
import json
import networkx as nx
from networkx.readwrite import json_graph


def load_graph(path="graph.json"):
    data = json.load(open(path, encoding="utf-8"))
    return json_graph.node_link_graph(data, edges="links")
```

`json_graph.node_link_graph` returns a `DiGraph` (because our JSON says
`"directed": true`), with every node attribute and every edge attribute
preserved. That directedness matters: a `calls` edge runs from caller to callee,
and we will rely on that direction when we trace paths.

## Step 4 — Find a node by name

When you ask about `place_order`, the tool must map that loose text to a specific
node id like `orders_place_order`. The Graphify engine does this with a **tiered
matcher**: it prefers an exact match, falls back to a prefix match, and only then
accepts a substring match — so the closest match always wins.

Add this function to `query.py`:

```python
def find_node(G, term):
    term = term.lower()
    exact, prefix, substring = [], [], []
    for nid, d in G.nodes(data=True):
        label = (d.get("label") or "").lower()
        if term == label or term == nid.lower():
            exact.append(nid)
        elif label.startswith(term) or nid.lower().startswith(term):
            prefix.append(nid)
        elif term in label or term in nid.lower():
            substring.append(nid)
    return exact + prefix + substring
```

We check both the node's `label` and its `id`, so either `place_order` or
`orders_place_order` will find the same node. The three tiers are concatenated in
order of preference, so the caller can simply take the first result as the best
match.

Now add a command that prints every match:

```python
def cmd_find(G, term):
    matches = find_node(G, term)
    if not matches:
        print(f"No node matching '{term}' found.")
        return
    print(f"Matches for '{term}':")
    for nid in matches:
        d = G.nodes[nid]
        print(f"  {d.get('label', nid)}  (id: {nid}, {d.get('source_file')})")
```

Finally, add a dispatcher at the bottom of the file so we can call commands from
the terminal:

```python
def main():
    G = load_graph()
    cmd = sys.argv[1]
    if cmd == "find":
        cmd_find(G, sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")


main()
```

Run it against a name that matches exactly one node:

```
python query.py find place
```

The output should look exactly like this:

```
Matches for 'place':
  place_order  (id: orders_place_order, orders.py)
```

Now try a looser term that touches several nodes:

```
python query.py find order
```

The output should look exactly like this:

```
Matches for 'order':
  orders.py  (id: orders, orders.py)
  place_order  (id: orders_place_order, orders.py)
  validate  (id: orders_validate, orders.py)
```

Notice the ranking at work. `orders.py` matched by prefix (its label starts with
"order"), while `place_order` and `validate` matched by substring (their ids
contain "order"). The prefix match is listed first because it is the stronger
tier.

## Step 5 — Trace the shortest path

Now the interesting question: *how does one function reach another?* We answer it
by asking NetworkX for the shortest path through the directed graph, then
printing each hop with the relation and confidence stored on that edge.

Add this command to `query.py`:

```python
def cmd_path(G, source, target):
    src = find_node(G, source)
    tgt = find_node(G, target)
    if not src:
        print(f"No node matching source '{source}' found.")
        return
    if not tgt:
        print(f"No node matching target '{target}' found.")
        return
    src_nid, tgt_nid = src[0], tgt[0]
    if src_nid == tgt_nid:
        print(f"'{source}' and '{target}' resolved to the same node '{src_nid}'.")
        return
    dg = nx.DiGraph()
    dg.add_nodes_from(sorted(G.nodes))
    dg.add_edges_from(sorted((u, v) for u, v in G.edges()))
    try:
        path_nodes = nx.shortest_path(dg, src_nid, tgt_nid)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        print(f"No directed path found between '{source}' and '{target}'.")
        return
    hops = len(path_nodes) - 1
    segments = [G.nodes[path_nodes[0]].get("label", path_nodes[0])]
    for i in range(hops):
        u, v = path_nodes[i], path_nodes[i + 1]
        d = G.get_edge_data(u, v)
        rel = d.get("relation", "related")
        conf = d.get("confidence")
        conf_str = f" [{conf}]" if conf else ""
        segments.append(f"--{rel}{conf_str}--> {G.nodes[v].get('label', v)}")
    print(f"Shortest path ({hops} hops):")
    print("  " + " ".join(segments))
```

Two details are worth pausing on. First, we resolve both endpoints with the same
`find_node` matcher and take the best match (`[0]`), so you can name endpoints
loosely. Second, we rebuild the graph from **sorted** nodes and edges before
searching. When several paths are equally short, that sort makes the chosen path
deterministic — you get the same answer every run, which is exactly what the real
engine guarantees.

Wire the new command into `main`. Replace the `main` function with this version:

```python
def main():
    G = load_graph()
    cmd = sys.argv[1]
    if cmd == "find":
        cmd_find(G, sys.argv[2])
    elif cmd == "path":
        cmd_path(G, sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {cmd}")


main()
```

Trace the cross-file call from `place_order` to `charge`:

```
python query.py path place_order charge
```

The output should look exactly like this:

```
Shortest path (1 hops):
  place_order --calls [INFERRED]--> charge
```

The tool followed the `calls` edge across the file boundary and told you the
relationship is `INFERRED` — a name-matched guess, not a certainty. Now trace the
same-file call:

```
python query.py path place_order validate
```

The output should look exactly like this:

```
Shortest path (1 hops):
  place_order --calls [EXTRACTED]--> validate
```

This hop is `EXTRACTED`: `place_order` and `validate` live in the same file, so
the call could be resolved with certainty. Finally, try tracing *against* the
direction of the call:

```
python query.py path charge place_order
```

The output should look exactly like this:

```
No directed path found between 'charge' and 'place_order'.
```

`charge` never calls `place_order`, and because our graph is directed, no route
exists backward. The tool reports that honestly rather than inventing a path.

## Step 6 — Explain a node

The last question is the simplest and often the most useful: *what is this node,
and what does it connect to?* We find the node, then list its outgoing edges
(what it points to) and incoming edges (what points at it).

Add this command:

```python
def cmd_explain(G, term):
    matches = find_node(G, term)
    if not matches:
        print(f"No node matching '{term}' found.")
        return
    nid = matches[0]
    d = G.nodes[nid]
    print(f"{d.get('label', nid)}  (id: {nid})")
    print(f"  source_file: {d.get('source_file')}")
    print(f"  location:    {d.get('source_location')}")
    out = list(G.successors(nid))
    inc = list(G.predecessors(nid))
    print(f"  outgoing ({len(out)}):")
    for v in out:
        e = G.get_edge_data(nid, v)
        print(f"    --{e['relation']}[{e['confidence']}]--> {G.nodes[v].get('label', v)}")
    print(f"  incoming ({len(inc)}):")
    for u in inc:
        e = G.get_edge_data(u, nid)
        print(f"    <--{e['relation']}[{e['confidence']}]-- {G.nodes[u].get('label', u)}")
```

`G.successors` and `G.predecessors` are the two halves of a directed node's
neighborhood: successors are where its arrows go, predecessors are where arrows
into it come from. Wire the command into `main` one more time — replace `main`
with this final version:

```python
def main():
    G = load_graph()
    cmd = sys.argv[1]
    if cmd == "find":
        cmd_find(G, sys.argv[2])
    elif cmd == "path":
        cmd_path(G, sys.argv[2], sys.argv[3])
    elif cmd == "explain":
        cmd_explain(G, sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")


main()
```

Explain the busiest node in the graph:

```
python query.py explain place_order
```

The output should look exactly like this:

```
place_order  (id: orders_place_order)
  source_file: orders.py
  location:    L1
  outgoing (2):
    --calls[EXTRACTED]--> validate
    --calls[INFERRED]--> charge
  incoming (1):
    <--contains[EXTRACTED]-- orders.py
```

In one view you can see everything about `place_order`: it lives in `orders.py`,
it calls two functions (one certainly, one inferred), and it is contained by its
file. Now explain a leaf function that calls nothing:

```
python query.py explain charge
```

The output should look exactly like this:

```
charge  (id: billing_charge)
  source_file: billing.py
  location:    L1
  outgoing (0):
  incoming (2):
    <--calls[INFERRED]-- place_order
    <--contains[EXTRACTED]-- billing.py
```

`charge` points at nothing (`outgoing (0)`), but two things point at it: the
cross-file call from `place_order` and the `contains` edge from its own file.
That incoming call is the same edge you traced in Step 5, now seen from the other
end.

## What you accomplished

You built a working query tool over a Graphify graph. It loads the node-link
`graph.json`, resolves loose names to nodes with a tiered matcher, traces the
shortest directed path between two functions while reporting each edge's relation
and confidence, and explains any node by listing its outgoing and incoming
connections. These are the same three operations the Graphify engine exposes — a
graph you can finally interrogate, not just store.

## Next steps / further reading

- Revisit **[03 — Build and save graph.json](03-build-and-save-graph-json.md)**
  to regenerate this graph from real source instead of writing it by hand, then
  point `query.py` at the result.
- The real query, path, and node-lookup logic lives in `graphify/serve.py`
  (`_find_node`, `_shortest_path_text`), where the matcher also handles
  diacritics, punctuation, and ambiguity across files.
- NetworkX shortest-path algorithms:
  https://networkx.org/documentation/stable/reference/algorithms/shortest_paths.html
```
