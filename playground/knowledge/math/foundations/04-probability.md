# Tutorial: Your first steps with Probability for Machine Learning

In this tutorial, we will simulate random events with our own hands, watch a
probability distribution take shape, and finish by using Bayes' Theorem to
update a belief in the light of evidence — the reasoning at the core of many
machine learning models.

By the end, you will have run basic probability, sampled from distributions,
worked with random variables, and applied Bayes' Theorem.

This tutorial should take about 30 minutes.

> This is a learning exercise. Run every step. Probability becomes intuitive
> when you watch random simulations settle into predictable patterns.

## Before we start

You need Python 3 with NumPy and Matplotlib installed. Check them:

```bash
python -c "import numpy, matplotlib; print('ok')"
```

You should see `ok`. If not, run `pip install numpy matplotlib`.

Open a new file called `probability_intro.py`.

## Step 1 — Estimate a probability by simulation

Probability is the long-run fraction of times an event happens. Let's confirm
that a fair coin lands heads about half the time — by flipping it 10,000 times.
Type this into the file:

```python
import numpy as np

rng = np.random.default_rng(seed=0)

flips = rng.integers(0, 2, size=10_000)   # 0 = tails, 1 = heads
heads_fraction = np.mean(flips)

print("fraction of heads:", heads_fraction)
```

Run it:

```bash
python probability_intro.py
```

Because we fixed the seed to `0`, you should see exactly:

```
fraction of heads: 0.503
```

Notice the fraction (`0.503`) is very close to the ideal `0.5`, but not exactly.
That gap is normal — probability describes long-run behaviour, not any single
outcome. Change `size=10_000` to `size=100` and run again: notice the fraction
now lands further from `0.5`. Fewer trials means a noisier estimate. Set it back
to `10_000`.

## Step 2 — Combine probabilities

Add these lines to explore the basic rules using a single dice roll:

```python
rolls = rng.integers(1, 7, size=100_000)   # a six-sided die

p_even = np.mean(rolls % 2 == 0)
p_gt4 = np.mean(rolls > 4)
p_even_and_gt4 = np.mean((rolls % 2 == 0) & (rolls > 4))

print("P(even):", round(float(p_even), 3))
print("P(>4):", round(float(p_gt4), 3))
print("P(even and >4):", round(float(p_even_and_gt4), 3))
```

Run the file. You should see approximately:

```
P(even): 0.498
P(>4): 0.333
P(even and >4): 0.166
```

Notice `P(even)` is about `0.5` (three of six faces are even) and `P(>4)` is
about `0.333` (two of six faces). The "and" probability (`0.166`) is smaller
than either — only the face `6` is both even and greater than 4. Combining
conditions makes events rarer, an idea you will use constantly when reasoning
about model predictions.

## Step 3 — Sample from a distribution and plot it

A probability distribution describes how likely each outcome is. Let's draw many
samples from the famous bell-shaped normal distribution and see its shape
emerge. Add:

```python
import matplotlib.pyplot as plt

samples = rng.normal(loc=0, scale=1, size=50_000)

plt.hist(samples, bins=50, edgecolor="black")
plt.title("Samples from a normal distribution")
plt.xlabel("value")
plt.ylabel("count")
plt.savefig("normal_distribution.png")
print("saved normal_distribution.png")
```

Run the file, then open `normal_distribution.png`. You should see:

```
saved normal_distribution.png
```

Notice the bars form a symmetric bell, tallest in the middle near `0` and
tapering off on both sides. We never designed that shape — it emerged from
random sampling. The normal distribution appears everywhere in ML, from
initialising model weights to modelling noise.

## Step 4 — A random variable and its expected value

A random variable assigns a number to each random outcome. Its *expected value*
is the average you would get over many trials. Let's define the payout of a
simple game and measure it. Add:

```python
# A game: roll a die. If you roll a 6 you win 10 points, otherwise you lose 1.
die = rng.integers(1, 7, size=200_000)
payout = np.where(die == 6, 10, -1)

print("average payout per game:", round(float(np.mean(payout)), 4))
```

Run the file. You should see something close to:

```
average payout per game: 0.824
```

Notice the average payout is positive (about `0.82`), so this game is worth
playing in the long run, even though you lose most individual rounds. Expected
value is how a model weighs uncertain outcomes to make a decision.

## Step 5 — Apply Bayes' Theorem

Bayes' Theorem updates a belief when new evidence arrives. This is the finale.
Consider a medical test for a rare disease:

- 1% of people have the disease.
- The test is 99% accurate for sick people (true positive).
- The test wrongly flags 5% of healthy people (false positive).

If someone tests positive, what is the chance they actually have the disease?
Most people guess "about 99%". Let's compute the real answer. Add:

```python
p_disease = 0.01
p_pos_given_disease = 0.99
p_pos_given_healthy = 0.05

# Total probability of a positive test
p_positive = (p_pos_given_disease * p_disease
              + p_pos_given_healthy * (1 - p_disease))

# Bayes' Theorem
p_disease_given_pos = (p_pos_given_disease * p_disease) / p_positive

print("P(disease | positive test):",
      round(p_disease_given_pos, 4))
```

Run the file. You should see exactly:

```
P(disease | positive test): 0.1667
```

Notice the surprising answer: only about **17%**, not 99%. Because the disease is
rare, most positive tests are actually false alarms from the large healthy
population. Bayes' Theorem forced us to combine the evidence (a positive test)
with the prior (the disease is rare) to reach the correct belief. This exact
calculation is what a Naive Bayes classifier does for every prediction.

Now change `p_disease` to `0.5` (imagine a common condition) and run again.
Notice the answer jumps up dramatically. The rarer the thing you are looking
for, the more cautious you must be about a positive signal. Set it back to
`0.01`.

## What we did

You have, with your own hands:

- estimated a probability by simulating thousands of coin flips
- combined probabilities with "and" conditions on a die
- sampled a normal distribution and watched its bell shape appear
- computed the expected value of a random variable
- applied Bayes' Theorem and discovered why a positive test can still mean low risk

Probability is how machine learning reasons under uncertainty, and Bayes'
Theorem is how it changes its mind when it sees new data.

## Where to go next

- Continue with [Discrete Mathematics for Machine Learning](05-discrete-mathematics.md).
- For understanding the two philosophies of probability and *why* the 17% result
  is correct rather than a trick, read
  [About probability and how machines reason under uncertainty](explanations/about-probability-and-uncertainty.md).
- Rerun Step 5 with different disease rates and test accuracies whenever you
  want to sharpen your Bayesian intuition.
- For the formal axioms of probability, reach for a reference once these
  simulations feel natural.
