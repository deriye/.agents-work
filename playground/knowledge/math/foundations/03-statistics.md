# Tutorial: Your first steps with Statistics for Machine Learning

In this tutorial, we will take a small dataset and, with our own hands, describe
it with statistics, then draw a chart of it, and finally use a sample to make an
inference about a larger population — the everyday work of a machine learning
practitioner exploring data.

By the end, you will have run descriptive statistics, made a graph, and taken
your first step into inferential statistics.

This tutorial should take about 25 minutes.

> This is a learning exercise. Type each step and read the output. You learn
> statistics by looking at real numbers, not by memorising formulas.

## Before we start

You need Python 3 with NumPy and Matplotlib installed. Check them:

```bash
python -c "import numpy, matplotlib; print('ok')"
```

You should see:

```
ok
```

If you get an error, install them:

```bash
pip install numpy matplotlib
```

Open a new file called `statistics_intro.py`.

## Step 1 — Load a dataset

We will use the exam scores of a small class. Type this into the file:

```python
import numpy as np

scores = np.array([55, 62, 68, 71, 71, 74, 78, 82, 88, 95])

print("number of students:", scores.size)
print("scores:", scores)
```

Run it:

```bash
python statistics_intro.py
```

You should see:

```
number of students: 10
scores: [55 62 68 71 71 74 78 82 88 95]
```

Notice we have exactly `10` scores. This small size is deliberate — you can
check every calculation by eye as we go, which builds trust in the tools.

## Step 2 — Measures of the center

Where is the "middle" of the data? There are three common answers. Add:

```python
print("mean:", np.mean(scores))
print("median:", np.median(scores))

values, counts = np.unique(scores, return_counts=True)
mode = values[np.argmax(counts)]
print("mode:", mode)
```

Run the file. You should see:

```
mean: 74.4
median: 72.5
mode: 71
```

Notice the three "centers" disagree slightly. The mean (`74.4`) is the average.
The median (`72.5`) is the middle value when sorted. The mode (`71`) is the most
frequent value — and indeed `71` is the only score that appears twice. In ML,
choosing the right center matters because the mean is easily dragged around by
extreme values.

## Step 3 — Measures of the spread

Center is not enough; we also need to know how spread out the data is. Add:

```python
print("min:", np.min(scores))
print("max:", np.max(scores))
print("range:", np.max(scores) - np.min(scores))
print("variance:", round(float(np.var(scores)), 2))
print("std dev:", round(float(np.std(scores)), 2))
```

Run the file. You should see:

```
min: 55
max: 95
range: 40
variance: 127.44
std dev: 11.29
```

Notice the standard deviation (`11.29`) is just the square root of the variance
(`127.44`); check it with a calculator if you like. The standard deviation tells
you the typical distance of a score from the mean. A model that ignores spread
will treat a tightly-clustered feature the same as a wildly-varying one, which
is usually a mistake.

## Step 4 — Draw a chart

Numbers are easier to grasp as a picture. Add:

```python
import matplotlib.pyplot as plt

plt.hist(scores, bins=5, edgecolor="black")
plt.title("Distribution of exam scores")
plt.xlabel("score")
plt.ylabel("number of students")
plt.savefig("scores_histogram.png")
print("saved scores_histogram.png")
```

Run the file. You should see:

```
saved scores_histogram.png
```

Now open the file `scores_histogram.png` that appeared next to your script.
Notice the bars show how many students fall into each score band. A histogram is
the first thing practitioners draw when they meet a new column of data, because
the *shape* of the data guides every later decision.

Run this step again and reopen the image. Confirm the chart looks the same —
reproducible pictures are as important as reproducible numbers.

## Step 5 — Your first inference

Descriptive statistics describe the data you *have*. Inferential statistics use
a *sample* to estimate something about a larger *population* you cannot fully
measure. Let's simulate that.

Add:

```python
rng = np.random.default_rng(seed=42)

population = rng.normal(loc=100, scale=15, size=100_000)
sample = rng.choice(population, size=30, replace=False)

print("true population mean:", round(float(np.mean(population)), 2))
print("estimate from 30 samples:", round(float(np.mean(sample)), 2))
```

Run the file. Because we fixed the seed to `42`, you should see exactly:

```
true population mean: 99.94
estimate from 30 samples: 101.26
```

Notice the estimate from just `30` samples (`101.26`) lands close to the true
mean of the whole `100,000`-strong population (`99.94`), even though we looked at
a tiny fraction. This is the heart of inferential statistics — and of machine
learning, which always learns from a limited sample and hopes to generalise to
data it has never seen.

Now change `size=30` to `size=1000` and run again. Notice the estimate moves
even closer to `99.94`. Larger samples give better estimates. Change it back to
`30`. You have just felt why "more data" so often helps in ML.

## What we did

You have, with your own hands:

- loaded a small dataset and inspected it
- computed the mean, median, and mode
- measured spread with range, variance, and standard deviation
- drawn and saved a histogram
- used a small sample to estimate a property of a large population

Descriptive statistics summarise your data; charts reveal its shape; and
inference is the bridge from the data you have to the world you want to predict.

## Where to go next

- Continue with [Probability for Machine Learning](04-probability.md).
- For understanding *why* a small sample can speak for a whole population — and
  the dangers of bias and variance when it can't — read
  [About sampling and inference](explanations/about-sampling-and-inference.md).
- Rerun Step 5 with different `size` values whenever you want to rebuild your
  feel for sampling.
- For the mathematics behind variance and inference, consult a statistics
  reference once you are comfortable running these experiments.
