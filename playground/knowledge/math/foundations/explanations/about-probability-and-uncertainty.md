# About probability and how machines reason under uncertainty

> This is an **explanation** article, for reflection after the
> [Probability tutorial](../04-probability.md). It discusses the two great ways
> of thinking about probability and why the "surprising" test result you
> computed is not a trick but a lesson. It is not a set of instructions.

## The question behind this article

In the tutorial you did two things that, on the surface, seem unrelated. First
you flipped a simulated coin ten thousand times and watched the fraction of
heads settle near one half. Later you fed a few numbers into Bayes' Theorem and
discovered that a person who tests positive for a rare disease is, most likely,
perfectly healthy — a mere 17% chance of actually being ill.

Both were "probability," yet they felt like different activities. That feeling
is correct, and it points at something worth understanding: there are two
distinct philosophies of what a probability *is*. Machine learning uses both,
often in the same breath, and knowing which is which clears up a great deal of
confusion.

## Two meanings of a single word

**The frequentist view: probability is long-run frequency.** When you flipped
the coin ten thousand times and got about 50% heads, you were living inside this
definition. Here, the probability of an event *is* the fraction of times it
happens if you repeat the experiment endlessly. It is objective, out in the
world, and you measure it by counting. This is the older, more intuitive view,
and it is why simulation felt so natural: you literally ran the experiment many
times and counted.

**The Bayesian view: probability is a degree of belief.** When you asked "given
this positive test, how much should I believe this person is ill?", there was no
experiment to repeat — this is one person, one test, one moment. The probability
here is not a frequency; it is a *measure of confidence*, a state of knowledge,
which changes as evidence arrives. Before the test you believed the person had a
1% chance of illness (because 1% of people do); after the positive result you
revised that belief upward, to 17%.

```
  frequentist:  "if I repeat this forever, how often?"   → count outcomes
  Bayesian:     "given what I now know, how confident?"  → update belief
```

Neither view is wrong. They are two lenses, each clearer for certain questions.
Frequency is the better lens for a coin you can flip a million times; belief is
the better lens for a one-off event where you must nonetheless act. The
long-running philosophical argument between the two camps need not concern a
practitioner — what matters is recognising which lens a given problem calls for.

## Why the 17% is correct, not a trick

The disease result surprises almost everyone, and the surprise is instructive
enough to unfold slowly.

Your intuition, hearing "the test is 99% accurate," wants to answer "then a
positive test means 99% chance of illness." The reason that intuition fails is
that it ignores how *rare* the disease is to begin with — what Bayesians call the
**prior**. Picture ten thousand people:

```
  10,000 people
     │
     ├─ 100 are ill (1%)          → test catches ~99 of them  → 99 true positives
     │
     └─ 9,900 are healthy (99%)   → test wrongly flags 5%      → 495 false positives
                                                                 ─────
   positive tests total:                                        594
   of which actually ill:                                        99
   → P(ill | positive) = 99 / 594 ≈ 0.17
```

There it is, laid bare. Because the healthy group is so enormous, even a small
5% error rate among them produces *more* false alarms (495) than there are true
cases (99). The test is not lying; there are simply far more healthy people to
mislabel than sick people to catch. Bayes' Theorem is the bookkeeping that
forces you to account for the size of each group, which raw intuition skips.

The lesson generalises far beyond medicine: **when you are looking for something
rare, a positive signal is weaker evidence than it appears.** Rare fraud among
millions of honest transactions, rare spam patterns, rare faults in
manufacturing — in every case, the rarity of the target means alarms must be
treated with suspicion. This is not pessimism; it is arithmetic.

## Why this is the shape of machine learning

Here is the connection that makes probability foundational rather than
decorative. A very large fraction of machine learning models do not output a
verdict; they output a *probability* — a degree of belief. A spam filter does
not know an email is spam; it assigns it, say, a 0.92 belief of being spam. A
medical model outputs a probability of disease, not a diagnosis.

This means models inherit exactly the subtlety you met in the tutorial. A model
that is "95% confident" about a rare condition may still, like the test, be
wrong most of the time it raises the alarm — *unless* it, and its users, account
for the prior. The **Naive Bayes** classifier named in the roadmap is Bayes'
Theorem turned directly into a prediction machine; it computes precisely the
kind of belief-update you did by hand. But even models with nothing "Bayesian"
in their name produce outputs that only make sense when read as probabilities,
with all the care that demands.

Expected value, which you also computed, is the other half of this story. A
model rarely wants only "how likely?" — it wants "given these likelihoods, what
should I *do*?" Weighing uncertain outcomes by their probabilities to choose an
action is exactly the expected-value calculation from the dice game, and it is
how a system decides whether a 17% chance of illness warrants further testing,
or whether a 0.92 spam score warrants deletion.

## A perspective worth holding

The deepest thing the tutorial teaches is not any single formula but a posture:
**certainty is rare, and honest reasoning means holding beliefs as
probabilities and revising them when evidence arrives.** The coin taught you
that randomness has stable long-run structure. Bayes' Theorem taught you that a
belief is not a fixed thing but a quantity you update, and that updating well
requires remembering where you started.

Machine learning, seen through this lens, is less a machine that *knows* and
more a machine that *believes carefully* — and the quality of its beliefs is
only ever as good as the priors and evidence we give it. That is a humbling and
useful thing to internalise early.

## Further reading

- [About sampling and inference](about-sampling-and-inference.md) — the
  companion piece; sampling and probability are the two halves of reasoning
  under uncertainty.
- When the roadmap reaches **Naive Bayes** and **classification metrics** such
  as precision and recall, return here: precision is, almost exactly, the
  "17% problem" wearing a different name.
