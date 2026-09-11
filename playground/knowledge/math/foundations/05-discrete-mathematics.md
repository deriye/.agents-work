# Tutorial: Your first steps with Discrete Mathematics for Machine Learning

In this tutorial, we will work with the discrete building blocks that computers
and ML algorithms are made of: sets, counting, logic, and graphs. We will do it
all with our own hands in Python, and finish by walking a graph — the same
structure behind social networks, recommendation systems, and knowledge graphs.

By the end, you will have run set operations, counted combinations, evaluated
logic, and traversed a graph.

This tutorial should take about 30 minutes.

> This is a learning exercise. Type and run each step. Discrete mathematics
> clicks when you watch small, exact examples behave.

## Before we start

You need Python 3. Almost everything here uses the standard library. Check
Python is available:

```bash
python --version
```

You should see something like:

```
Python 3.11.5
```

One step uses NumPy; if you already did the earlier tutorials you have it. If
not, run `pip install numpy`.

Open a new file called `discrete_math.py`.

## Step 1 — Sets and set operations

A set is a collection with no duplicates and no order. Type this into the file:

```python
ml_students = {"ana", "ben", "cara", "dan"}
stats_students = {"cara", "dan", "eve", "finn"}

print("in both classes:", ml_students & stats_students)
print("in either class:", ml_students | stats_students)
print("only in ML:", ml_students - stats_students)
```

Run it:

```bash
python discrete_math.py
```

You should see (the order inside the braces may vary):

```
in both classes: {'cara', 'dan'}
in either class: {'ana', 'ben', 'cara', 'dan', 'eve', 'finn'}
only in ML: {'ana', 'ben'}
```

Notice the three operations: `&` finds the intersection (people in both), `|`
finds the union (everyone), and `-` finds the difference (ML-only). Sets are how
ML tools track things like unique words in a text or unique categories in a
column.

## Step 2 — Counting: permutations and combinations

Counting the number of possible arrangements is a core discrete-math skill. Add:

```python
import math

# How many ways to pick a 3-person team from 5 people?
combinations = math.comb(5, 3)

# How many ways to arrange 3 people in 1st, 2nd, 3rd place?
permutations = math.perm(5, 3)

print("combinations (order does not matter):", combinations)
print("permutations (order matters):", permutations)
```

Run the file. You should see:

```
combinations (order does not matter): 10
permutations (order matters): 60
```

Notice permutations (`60`) is larger than combinations (`10`), because
permutations count `ana-ben-cara` and `cara-ben-ana` as different, while
combinations treat them as the same team. Counting like this tells you how large
a search space a model faces.

## Step 3 — Boolean logic and truth tables

Discrete logic underlies every decision a program makes. Let's build a truth
table for `AND`, `OR`, and `IMPLIES`. Add:

```python
print(f"{'A':>5} {'B':>5} {'A and B':>8} {'A or B':>7} {'A=>B':>6}")
for a in (False, True):
    for b in (False, True):
        implies = (not a) or b
        print(f"{str(a):>5} {str(b):>5} {str(a and b):>8}"
              f" {str(a or b):>7} {str(implies):>6}")
```

Run the file. You should see:

```
    A     B  A and B  A or B   A=>B
False False    False   False   True
False  True    False    True   True
 True False    False    True  False
 True  True     True    True   True
```

Notice the one surprising row: when `A` is `True` and `B` is `False`, `A => B`
("A implies B") is `False` — a true premise with a false conclusion breaks the
implication. Every other combination holds. Decision trees, a core ML model, are
built entirely from chains of logic like this.

## Step 4 — Build a graph

A graph is a set of nodes joined by edges. We will represent one as a
dictionary. Add:

```python
graph = {
    "A": ["B", "C"],
    "B": ["A", "D"],
    "C": ["A", "D"],
    "D": ["B", "C", "E"],
    "E": ["D"],
}

for node, neighbors in graph.items():
    print(f"{node} is connected to {neighbors}")
```

Run the file. You should see:

```
A is connected to ['B', 'C']
B is connected to ['A', 'D']
C is connected to ['A', 'D']
D is connected to ['B', 'C', 'E']
E is connected to ['D']
```

Notice each node lists its direct neighbours. This tiny structure is exactly how
a social network stores "who follows whom" or how a recommendation system links
"users to items." Take a moment to trace by eye that you can get from `A` to `E`
by going `A → B → D → E`.

## Step 5 — Walk the graph

Now let's have the computer find a path from `A` to `E` on its own, using a
breadth-first search. Add:

```python
from collections import deque

def shortest_path(graph, start, goal):
    queue = deque([[start]])
    visited = set()
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        if node not in visited:
            visited.add(node)
            for neighbor in graph[node]:
                queue.append(path + [neighbor])
    return None

print("shortest path A to E:", shortest_path(graph, "A", "E"))
```

Run the file. You should see exactly:

```
shortest path A to E: ['A', 'B', 'D', 'E']
```

Notice the algorithm found the same 4-node path you traced by eye — and it is
the *shortest* one. Breadth-first search explores a graph level by level, so the
first time it reaches the goal, it has used the fewest possible hops. This exact
algorithm powers "degrees of separation," routing, and graph-based
recommendation in ML systems.

Run this step two or three more times. You should get `['A', 'B', 'D', 'E']`
every time. Then add a new edge by changing `"A": ["B", "C"]` to
`"A": ["B", "C", "E"]` and run again — notice the path becomes the direct
`['A', 'E']`. You have just changed the graph and watched the algorithm adapt.
Set it back when you are done.

## What we did

You have, with your own hands:

- performed intersection, union, and difference on sets
- counted combinations and permutations
- built a truth table for boolean logic
- represented a graph as connections between nodes
- run a breadth-first search to find the shortest path

Discrete mathematics gives ML its exact, countable structures: unique
categories (sets), decision logic (booleans), and the relationships (graphs)
that connect data together.

## Where to go next

- You have finished the Math Foundations track. Head back to the
  [tutorial index](README.md) to see the whole series.
- For understanding *why* ML needs both discrete and continuous mathematics, and
  where sets, logic, and graphs fit into real systems, read
  [About discrete structures in machine learning](explanations/about-discrete-structures-in-ml.md).
- The roadmap's next stop is Python — and you have already been writing it
  throughout these five tutorials.
- Rerun Step 5 with your own graphs whenever you want to strengthen your feel
  for traversal.
