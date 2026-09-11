# Tutorial: Your first steps with Calculus for Machine Learning

In this tutorial, we will compute derivatives with our own hands using Python,
watch a gradient point us downhill, and finish by running a tiny gradient
descent loop — the exact procedure that trains every neural network.

By the end, you will have run each idea that ML depends on: derivatives, partial
derivatives, the gradient, the chain rule, and gradient descent.

This tutorial should take about 30 minutes.

> This is a learning exercise. Do each step and watch the numbers change. The
> understanding comes from the doing, not from the reading.

## Before we start

You need Python 3 with NumPy installed. Check it in a terminal:

```bash
python -c "import numpy; print(numpy.__version__)"
```

You should see a version number like `1.26.4`. If you get an error, run
`pip install numpy` first.

Open a new file called `calculus.py`. We will build it up step by step.

## Step 1 — Estimate a derivative

A derivative measures how fast a function changes. Let's measure it for
`f(x) = x²` at the point `x = 3`, without any calculus rules — just by nudging
`x` a tiny bit and seeing how much `f` moves.

Type this into `calculus.py`:

```python
def f(x):
    return x ** 2

x = 3.0
h = 0.0001
slope = (f(x + h) - f(x)) / h

print("approx derivative at x=3:", round(slope, 4))
```

Run it:

```bash
python calculus.py
```

You should see:

```
approx derivative at x=3: 6.0001
```

Notice the answer is almost exactly `6`. The calculus rule says the derivative of
`x²` is `2x`, and `2 * 3 = 6`. We just recovered that rule by experiment. The
tiny number `h` is the "nudge"; the smaller it is, the closer we get to `6`.

Change `x` to `5.0` and run again. You should see roughly `10.0`, because
`2 * 5 = 10`. Change it back to `3.0`.

## Step 2 — Partial derivatives

Real ML functions have many inputs. A *partial* derivative nudges just one input
and holds the rest still. Let's use `g(x, y) = x² + y³` and measure how it
responds to each input separately.

Add:

```python
def g(x, y):
    return x ** 2 + y ** 3

x, y = 2.0, 3.0
h = 0.0001

df_dx = (g(x + h, y) - g(x, y)) / h
df_dy = (g(x, y + h) - g(x, y)) / h

print("partial wrt x:", round(df_dx, 3))
print("partial wrt y:", round(df_dy, 3))
```

Run the file. You should see (approximately):

```
partial wrt x: 4.0
partial wrt y: 27.001
```

Notice that nudging `x` gave about `4` (`2x = 2*2`) while nudging `y` gave about
`27` (`3y² = 3*9`). Each partial derivative ignores the other variable
completely. This is how a model figures out which input to adjust.

## Step 3 — Assemble the gradient

The gradient is simply all the partial derivatives collected into one vector.
Add:

```python
import numpy as np

gradient = np.array([df_dx, df_dy])
print("gradient:", np.round(gradient, 3))
```

Run it. You should see:

```
gradient: [ 4.    27.001]
```

Notice the gradient is just the two numbers from Step 2 side by side. The
gradient points in the direction where the function increases fastest. To make
a function *smaller* — which is what training does — we will step in the
*opposite* direction. Keep that in mind for the last step.

## Step 4 — The chain rule

Models are functions stacked inside functions, like `h(x) = (2x + 1)²`. The
chain rule multiplies the rates of change of each layer. Let's confirm it by
experiment. Add:

```python
def outer(u):
    return u ** 2

def inner(x):
    return 2 * x + 1

def h(x):
    return outer(inner(x))

x = 1.0
step = 0.0001
numeric = (h(x + step) - h(x)) / step

# chain rule: d(outer)/du * d(inner)/dx = (2u) * (2)
u = inner(x)
chain_rule = (2 * u) * 2

print("numeric derivative:", round(numeric, 3))
print("chain rule result:", round(chain_rule, 3))
```

Run the file. You should see both numbers agree:

```
numeric derivative: 12.0
chain rule result: 12.0
```

Notice the two methods match. The chain rule (`12.0`) gives the same answer as
the brute-force nudge (`12.0`). This matching is exactly why the chain rule is
trusted, and it is the engine of "backpropagation," which trains neural
networks.

## Step 5 — Run gradient descent

Now we put it together. We will find the lowest point of `f(x) = x²` by starting
at `x = 10` and repeatedly stepping downhill using the gradient. Add:

```python
x = 10.0
learning_rate = 0.1

for step_number in range(1, 26):
    grad = 2 * x            # derivative of x**2
    x = x - learning_rate * grad
    if step_number % 5 == 0:
        print(f"step {step_number:2d}: x = {x:.4f}")
```

Run the file. You should see `x` marching toward zero:

```
step  5: x = 3.2768
step 10: x = 1.0737
step 15: x = 0.3518
step 20: x = 0.1153
step 25: x = 0.0378
```

Notice `x` gets smaller and smaller, closing in on `0`, which is the bottom of
`x²`. We never told the program the answer — it found the minimum by following
the gradient downhill, one small step at a time. This loop, scaled up to
millions of numbers, is how every neural network learns.

Run the file two or three more times and confirm you get the same sequence each
time. Then try changing `learning_rate` to `0.9` and run again — notice `x` now
bounces around instead of settling. Set it back to `0.1`. You have just felt,
with your own hands, why the learning rate matters.

## What we did

You have, with your own hands:

- estimated a derivative by nudging an input
- computed partial derivatives one variable at a time
- assembled those partials into a gradient
- confirmed the chain rule against a brute-force calculation
- run a gradient descent loop that found a minimum on its own

These are not separate tricks — they are the single mechanism that trains
machine learning models.

## Where to go next

- Continue with [Statistics for Machine Learning](03-statistics.md).
- For understanding *why* the downhill walk works, why the learning rate matters,
  and when it fails, read
  [About why gradient descent works (and when it doesn't)](explanations/about-why-gradient-descent-works.md).
- Come back and rerun Step 5 with different starting points and learning rates
  whenever you want to rebuild your intuition.
- For the formal rules behind these experiments, see any calculus reference —
  but only once you feel comfortable with the doing.
