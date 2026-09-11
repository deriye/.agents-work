# About sampling and inference

> This is an **explanation** article, for reflection after the
> [Statistics tutorial](../03-statistics.md). It discusses why a small sample
> can tell us about a much larger world, and why that idea is the foundation of
> machine learning itself. It contains no steps to follow.

## The question behind this article

In the tutorial you estimated the mean of a population of a hundred thousand
values by looking at just thirty of them — and the estimate came out close. Then
you increased the sample size and watched the estimate get closer still. It may
have felt almost too easy. *Why* should thirty randomly chosen numbers know
anything about a hundred thousand they were drawn from? And why does looking at
more of them help in such a reliable way?

This article is about that leap — the move from *describing the data you have*
to *inferring things about data you don't* — and about why every machine
learning model is, at heart, an act of that same leap.

## Two different jobs: describing and inferring

The tutorial quietly did two very different kinds of work, and it is worth
separating them.

The first half — mean, median, mode, variance, the histogram — was
**descriptive**. It summarised a set of numbers that were *entirely in your
hands*. There was no uncertainty and no guessing; the mean of those ten exam
scores simply *was* 74.4. Descriptive statistics make no claims about anything
beyond the data in front of you.

The final step was **inferential**, and it is a different animal altogether. You
had thirty numbers but wanted to say something about a hundred thousand you had
*not* fully examined. That is no longer summarising; it is *reasoning under
uncertainty*. You were making a claim about the unseen, and — crucially — that
claim could be wrong.

```
  descriptive:   [ the data you have ] → a summary of that data
                       (no uncertainty)

  inferential:   [ a sample ] → a claim about [ the whole population ]
                       (always some uncertainty)
```

The reason this distinction matters so much in ML is that **machine learning
lives entirely on the inferential side.** A model is never shown all possible
data. It sees a sample — the training set — and must make claims about data it
has never encountered. The comfort you felt watching thirty numbers approximate
a hundred thousand is the same comfort, and the same risk, that underlies every
prediction a model makes.

## Why a sample resembles its population

So why does it work at all? The short answer is that a *random* sample has no
reason to be systematically unlike the thing it was drawn from. Because each of
your thirty values was picked without bias, high and low values tend to appear
in roughly the proportions they occur in the population. Their average therefore
tends to land near the population's average. Not exactly — but near.

The gap between your estimate and the truth is called **sampling error**, and
the beautiful, dependable fact you observed is that this error shrinks as the
sample grows. Loosely, quadrupling the sample size halves the typical error.
This is why "get more data" is such reliable advice in ML: more data means a
sample that resembles reality more faithfully, and a model that generalises
better.

But notice the hidden condition doing all the work: the sample must be *random*,
or at least *representative*. This is not a technicality — it is the whole game.

## When inference goes wrong: the quiet danger of bias

Here the article must sound a warning, because this is where inference — and
machine learning — most often fails.

Everything above assumed the sample was drawn fairly. If instead the sample is
*biased* — if some part of the population is systematically over- or
under-represented — then no amount of extra data will save you. A large biased
sample does not converge on the truth; it converges, confidently and precisely,
on the *wrong answer*. More data makes a biased estimate more certain, not more
correct, which is worse than obvious error because it wears the disguise of
rigour.

This is not a hypothetical concern. It is the root of many real machine-learning
failures: a face-recognition model trained mostly on one group of faces, a
hiring model trained on a company's historically skewed decisions, a medical
model trained on patients from a single hospital. In every case the model
performed its inference faithfully; the *sample* was the problem. The
mathematics was innocent, and useless.

So the lesson to carry from the tutorial is double-edged. Sampling is powerful:
it lets us reason about vast populations from small glimpses. And sampling is
dangerous: it is only as trustworthy as the glimpse is representative. A mature
practitioner holds both truths at once.

## The bias–variance idea, informally

There is a second reason a small sample can mislead, and it points at a tension
that runs through all of ML. Return to your experiment: with thirty samples the
estimate wobbled noticeably from the truth; with a thousand it wobbled far less.
That wobble is **variance** — the tendency of an estimate to swing around
depending on which particular sample you happened to draw.

Bias and variance are two distinct ways of being wrong:

- **Bias** is being wrong *in a consistent direction* — the archer whose arrows
  all cluster tightly, but off to the left of the target.
- **Variance** is being wrong *inconsistently* — the archer whose arrows scatter
  all around the bullseye, right on average but individually unreliable.

```
   high bias, low variance      low bias, high variance
        ( arrows )                    ( arrows )
        · ·                              ·
       · ·   ← tight but                    ·   ← centred but
        ·      off-centre              ·   ·      scattered
      target: +                     target: + ·
```

You cannot usually eliminate both at once; reducing one often increases the
other, and managing that trade-off is one of the central arts of building
models. When the roadmap later discusses *overfitting* (a model with low bias
but ruinous variance — it memorises its sample and fails on new data) and
*underfitting* (high bias — too simple to capture the pattern), it is describing
exactly the two failure modes you glimpsed by changing a sample size.

## A perspective worth holding

It is tempting to treat inferential statistics as a preliminary — the boring
groundwork before the "real" machine learning begins. I would argue the reverse:
inference *is* the real machine learning, and everything else is engineering
around it. A model is a machine for generalising from a sample to a population.
Understanding, in your bones, both *why that works* and *how it fails* is not
preparation for the subject — it is the subject, met early and in its simplest
form.

The thirty numbers that approximated a hundred thousand were a first, honest
encounter with the single assumption on which the entire field rests: that the
data we have can speak, carefully and conditionally, for the data we don't.

## Further reading

- [About probability and uncertainty](about-probability-and-uncertainty.md) —
  the companion piece, since inference and probability are two faces of
  reasoning under uncertainty.
- When the roadmap reaches **Model Evaluation**, **overfitting**, and
  **validation techniques**, return here: they are the bias–variance idea made
  practical.
