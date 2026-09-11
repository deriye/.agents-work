# Build the Graphify core engine, from scratch

These tutorials teach you to build the core of the [Graphify](https://github.com/Graphify-Labs/graphify)
engine by hand: a pipeline that reads Python source, turns it into a graph of
nodes and edges, saves that graph to disk, and answers questions about it.

They are **learning-oriented tutorials** in the [Diátaxis](https://diataxis.fr/)
sense. Each one is a guided, hands-on lesson you can follow start to finish, and
each is designed to *always succeed*: you work in a fresh empty folder, install
pinned package versions, type in the code, and see the exact output printed here.
You do not need to have used Graphify before, and you do not need to read its
source — although pointers to the real implementation are given at the end of
each tutorial.

## What you will build

By the end you will have written, from nothing:

- a parser that extracts **nodes** (files, functions, classes, methods) from
  source code with tree-sitter,
- a resolver that connects them with **edges** (`contains`, `calls`) at two
  confidence tiers, **EXTRACTED** and **INFERRED**,
- a builder that assembles and validates a whole project into a single
  `graph.json`, and
- a query tool that **finds** symbols, traces the **shortest path** between
  functions, and **explains** any node's connections.

Everything targets one language — **Python** — so that every step is reproducible
on any machine.

## The tutorials

Work through them in order. Each builds on the concepts of the one before, but
every tutorial is self-contained: it starts from an empty folder and creates
whatever inputs it needs, so you can also jump straight to the one you care about.

1. **[Parse a Python file into graph nodes with tree-sitter](01-parse-code-into-nodes.md)**
   Install tree-sitter, parse a source file into a syntax tree, and turn every
   function, class, and method into a Graphify node with a stable id.

2. **[Turn function calls into graph edges (EXTRACTED and INFERRED)](02-resolve-calls-into-edges.md)**
   Find the calls between functions, resolve them within and across files, and
   assign each edge a confidence tier — while an ambiguity guard prevents false
   connections.

3. **[Build and save graph.json](03-build-and-save-graph-json.md)**
   Walk a whole project, combine file nodes, `contains` edges, and resolved
   `calls` edges, validate the result against Graphify's schema, and write a
   loadable `graph.json` in NetworkX node-link format.

4. **[Query, path, and explain your graph](04-query-path-explain.md)**
   Load `graph.json` and build a command-line tool that finds a symbol, traces
   the shortest directed path between two functions, and explains any node's
   incoming and outgoing connections.

## Requirements

- **Python 3.12** (`python --version` should print `Python 3.12.x`).
- The ability to run `pip install` and `python` from your terminal.

Each tutorial installs its own pinned dependencies (`tree-sitter`,
`tree-sitter-python`, `networkx`) in its first step, so there is nothing to set
up in advance beyond Python itself.
