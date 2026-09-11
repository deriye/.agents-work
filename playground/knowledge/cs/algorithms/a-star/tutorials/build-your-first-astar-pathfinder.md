# Build your first A* pathfinder

In this tutorial we will build a working A* pathfinder that finds the shortest
route across a small grid, stepping around walls to reach a goal. Along the way
we will encounter grids, neighbours, the *g*, *h*, and *f* scores, a priority
queue, and the moment the path lights up on screen.

By the end you will have a single Python file you can run over and over, watching
your pathfinder carve a route through the maze.

## Prerequisites

Before step 1, make sure you have:

- **Python 3.10 or newer** installed. Check it with:

  ```
  python --version
  ```

  The output should look something like:

  ```
  Python 3.11.5
  ```

  If you don't see a version number here, Python is not installed or not on your
  path, and the later steps will not run.

- A plain text editor and a terminal open in a folder you can write files to.

That's all. A* needs nothing beyond Python's standard library.

## Step 1 — Draw the world

First, let's give our pathfinder a world to walk through. Create a new file
called `astar.py` and type in this grid:

```python
GRID = [
    "S....",
    ".###.",
    "...#.",
    ".#.#.",
    ".#..G",
]

for row in GRID:
    print(row)
```

Now run it:

```
python astar.py
```

The output should look something like:

```
S....
.###.
...#.
.#.#.
.#..G
```

Notice the `S` in the top-left and the `G` in the bottom-right. Those are our
**start** and **goal**. The `#` characters are walls, and the `.` characters are
open floor. This little map is the whole world our pathfinder will explore.

## Step 2 — Find the start and the goal

Our pathfinder needs to know where it begins and where it's headed. Let's have
the program locate `S` and `G` for us. Replace the whole contents of `astar.py`
with this:

```python
GRID = [
    "S....",
    ".###.",
    "...#.",
    ".#.#.",
    ".#..G",
]

def find(symbol):
    for r, row in enumerate(GRID):
        for c, cell in enumerate(row):
            if cell == symbol:
                return (r, c)

start = find("S")
goal = find("G")

print("start:", start)
print("goal:", goal)
```

Run it again:

```
python astar.py
```

The output should look something like:

```
start: (0, 0)
goal: (4, 4)
```

Notice that each position is a `(row, column)` pair. The start sits at row 0,
column 0; the goal at row 4, column 4. From now on, every place our pathfinder
visits will be one of these pairs.

## Step 3 — Ask "how far, roughly?"

A* is fast because it guesses how far the goal is and heads that way first. Let's
write that guess. It's called the **heuristic**. We will use the number of
grid steps ignoring walls — the Manhattan distance.

Add this function just below `find`, and add the two `print` lines at the bottom:

```python
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

print("guess from start to goal:", heuristic(start, goal))
print("guess from (4,0) to goal:", heuristic((4, 0), goal))
```

Run it:

```
python astar.py
```

The output should look something like:

```
start: (0, 0)
goal: (4, 4)
guess from start to goal: 8
guess from (4,0) to goal: 4
```

Notice that the corner far from the goal scores `8`, while a spot closer scores
`4`. A smaller number means "probably closer." This is the compass our
pathfinder will follow.

> We use Manhattan distance because our pathfinder only moves up, down, left, and
> right. For why the heuristic must never *overestimate*, see the further reading
> at the end.

## Step 4 — Step to the neighbours

A pathfinder moves one square at a time. Let's list the open squares next to any
position. Add this function below `heuristic`:

```python
def neighbours(pos):
    r, c = pos
    result = []
    for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < len(GRID) and 0 <= nc < len(GRID[0]):
            if GRID[nr][nc] != "#":
                result.append((nr, nc))
    return result

print("neighbours of start:", neighbours(start))
```

Run it:

```
python astar.py
```

The output should look something like:

```
start: (0, 0)
goal: (4, 4)
guess from start to goal: 8
guess from (4,0) to goal: 4
neighbours of start: [(1, 0), (0, 1)]
```

Notice the start has only two neighbours — it's a corner, so there's nothing
above or to the left. Notice too that walls are already filtered out: our
pathfinder will never even consider stepping into a `#`.

## Step 5 — Search for the path

Now we bring it together. This is the heart of A*: always explore the square that
looks most promising — the one with the smallest *f* score, where *f* is the
distance travelled so far plus the guessed distance remaining.

Add this at the top of the file, on the very first line:

```python
import heapq
```

Then add this function below `neighbours`:

```python
def a_star(start, goal):
    frontier = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal:
            break

        for nxt in neighbours(current):
            new_cost = cost_so_far[current] + 1
            if nxt not in cost_so_far or new_cost < cost_so_far[nxt]:
                cost_so_far[nxt] = new_cost
                priority = new_cost + heuristic(nxt, goal)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = current

    return came_from

came_from = a_star(start, goal)
print("goal reached:", goal in came_from)
print("squares explored:", len(came_from))
```

Run it:

```
python astar.py
```

The output should look something like:

```
start: (0, 0)
goal: (4, 4)
guess from start to goal: 8
guess from (4,0) to goal: 4
neighbours of start: [(1, 0), (0, 1)]
goal reached: True
squares explored: 18
```

Notice `goal reached: True` — our pathfinder made it! And notice it only explored
18 squares. It did not wander the whole map; the heuristic pulled it toward the
goal. If you see `goal reached: False`, check that you added the `import heapq`
line at the very top of the file.

## Step 6 — Walk the path back

Our pathfinder knows how it reached the goal — the `came_from` map remembers each
step's predecessor. Let's follow those breadcrumbs from the goal back to the
start. Add this below the last `print`:

```python
def rebuild(came_from, start, goal):
    path = []
    current = goal
    while current is not None:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

path = rebuild(came_from, start, goal)
print("path:", path)
```

Run it:

```
python astar.py
```

The `path:` line of the output should look something like:

```
path: [(0, 0), (0, 1), (0, 2), (0, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4)]
```

Notice the list starts at `(0, 0)` — the start — and ends at `(4, 4)` — the goal.
Each pair steps to a direct neighbour of the one before it. That's a real,
walkable route.

## Step 7 — Watch the path light up

Numbers are good, but let's *see* the route. We will draw the grid again and mark
every square on the path with a `*`. Add this to the bottom of the file:

```python
def draw(path):
    marked = set(path)
    for r, row in enumerate(GRID):
        line = ""
        for c, cell in enumerate(row):
            if (r, c) == start:
                line += "S"
            elif (r, c) == goal:
                line += "G"
            elif (r, c) in marked:
                line += "*"
            else:
                line += cell
        print(line)

print()
draw(path)
```

Run it one last time:

```
python astar.py
```

The last block of the output should look something like:

```
S****
.###*
...#*
.#.#*
.#..G
```

There it is. Notice how the `*` trail hugs the top wall, dives down the right-hand
column, and slips into the goal — neatly avoiding every `#`. Your pathfinder just
solved the maze in front of your eyes.

Try changing a `.` to a `#` to block that route, or move the `G`, and run the
program again. Each time you run it, the path redraws itself around your new
obstacles.

## What you accomplished

You have now built a complete A* pathfinder from an empty file. It reads a map,
finds the start and goal, guesses distances, explores the most promising squares
first, reconstructs the shortest route, and paints it back onto the grid. That is
the same core algorithm powering navigation in games, robots, and map apps — and
you wrote it yourself, one small step at a time.

## Next steps / further reading

- **How-to**: change the movement rules to allow diagonal steps, or weight some
  squares as costlier terrain.
- **Reference**: Python's [`heapq`](https://docs.python.org/3/library/heapq.html)
  module, the priority queue at the centre of the search.
- **Explanation**: why an *admissible* heuristic (one that never overestimates)
  guarantees A* finds the shortest path — see Amit Patel's
  [Introduction to A*](https://www.redblobgames.com/pathfinding/a-star/introduction.html).
