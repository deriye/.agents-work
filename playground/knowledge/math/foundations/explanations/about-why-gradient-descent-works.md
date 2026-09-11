# About why gradient descent works (and when it doesn't)

> This is an **explanation** article, for reflection after the
> [Calculus tutorial](../02-calculus.md). It discusses the ideas behind the
> gradient descent loop you ran, and weighs its strengths and weaknesses. It is
> not a set of steps.

## The question behind this article

In the tutorial you watched a value start at `10` and march steadily toward `0`,
the bottom of the curve `f(x) = x²`, guided only by its gradient. Then you
changed the learning rate to `0.9` and watched the same process bounce around
instead of settling. Those two runs contain, in miniature, almost everything
that matters about how machine learning models are trained. This article is
about *why* the downhill walk works, why it sometimes fails, and why the field
relies on it despite there often being, in principle, better alternatives.

## The idea: learning as descending a landscape

The central metaphor is worth stating carefully because so much rests on it.
Imagine the model's error — how wrong its predictions are — as the height of a
landscape. The model's adjustable numbers (its weights) are your coordinates on
that landscape. Training means finding the coordinates where the height, the
error, is lowest.

```
  error
   |    \                        .
   |     \                     .
   |      \                 .
   |       \.           .
   |          \.     .          ← we want to reach the bottom
   |             \_.
   +-------------------------------- weight value
        start →→→ ... →→→ minimum
```

You cannot see the whole landscape — it exists in as many dimensions as the
model has weights, often millions. But at your current spot you *can* feel the
slope beneath your feet. The gradient is exactly that slope: it points in the
direction of steepest *increase*. So to go down, you step in the opposite
direction. Take a step, feel the new slope, step again. That is gradient
descent, and it is the whole of the loop you ran.

The quiet brilliance of this is that it needs only *local* information. At no
point does the algorithm know where the bottom is. It only knows which way is
downhill *right here*, and trusts that repeatedly going downhill will get it
somewhere low. For a problem in a million dimensions, where seeing the whole
landscape is hopeless, that locality is not a limitation — it is the only thing
that makes the problem tractable at all.

## Why the learning rate misbehaved

When you set the learning rate to `0.9`, the value stopped settling and started
bouncing. This was not a bug; it was the method showing you its central tension.

The learning rate is the *size* of each step. Too small, and the descent creeps
along, taking thousands of steps to reach the bottom — wasting time. Too large,
and each step overshoots the minimum entirely, landing on the far wall of the
valley higher than where it started, then overshooting back the other way:

```
  small rate:  . . . . . . .→  (slow but sure)

  good rate:   .   .   .  . .→  (brisk and stable)

  large rate:      .           .
                 .               .    (overshoots, may never settle
               .                   .   or even fly off to infinity)
```

There is no universally correct learning rate; it is a *judgement*, one of the
first things a practitioner learns to tune by feel. That a single number can be
the difference between a model that trains beautifully and one that never
converges is, to newcomers, one of the more surprising facts about deep
learning — and you discovered it firsthand by changing one line.

## The connection to the chain rule

In the tutorial you also confirmed the chain rule by two independent methods and
saw them agree at `12.0`. That agreement is what makes gradient descent usable
on real models.

A real model is functions nested inside functions, layer upon layer. To take a
downhill step we need the gradient of the *final* error with respect to *every*
weight buried deep inside. The chain rule is what lets us compute that: it
multiplies together the local slope of each layer, propagating the error signal
backwards from the output to every parameter. This procedure has a name —
**backpropagation** — and it is nothing more than the chain rule applied
systematically across a whole network. The humble two-function example you
verified is the same mechanism that trains a model with billions of parameters.

## When gradient descent doesn't work

An honest account must admit the method's failure modes, because they shape much
of the practical craft of ML.

**Local minima and flat regions.** The curve `x²` you used has exactly one
bottom, so downhill always leads to the right place. Real error landscapes are
rugged, with many valleys. Gradient descent, seeing only the local slope, can
settle into a *local* minimum — a valley that is low, but not the lowest — and
have no way of knowing a deeper valley lies beyond a nearby ridge. It can also
crawl to a halt on a vast flat plateau where the slope is nearly zero and there
is no clear way down.

**Sensitivity to scale.** If different weights live on wildly different scales,
the landscape becomes a long narrow ravine, and plain gradient descent
ping-pongs across it inefficiently. This is one of the concrete reasons the
tutorials on data preprocessing insist on *feature scaling* — it reshapes the
landscape into something rounder and easier to descend.

These difficulties are why the roadmap later mentions optimisers with names like
*momentum* and *Adam*. They are all variations on the downhill walk, each adding
a trick to cope with ravines, plateaus, or awkward learning rates. None of them
abandon the core idea; they refine it.

## Why not just solve it directly?

A fair objection: for a simple curve like `x²`, calculus can find the exact
minimum in one step by setting the derivative to zero. Why iterate at all?

The answer is a matter of scale and honesty about our tools. Direct solutions
exist only for a few well-behaved problems. For a deep neural network — millions
of interacting weights, non-linear at every layer — there is no formula for the
minimum. There is no equation to set to zero and solve. The landscape is too
complex to describe, let alone solve analytically. Iterative descent, which asks
only "which way is down from here?", is the method that survives contact with
that complexity. It trades the certainty of an exact answer for the ability to
make progress on a problem no formula can touch — and in machine learning, that
trade is almost always the right one.

## A perspective worth holding

It is easy to see gradient descent as a mere numerical trick. I would encourage
the opposite view: it is a *philosophy of learning from feedback*. Make a guess,
measure how wrong you are, adjust slightly in the direction that reduces the
error, and repeat. Framed that way, the loop you ran is not only how neural
networks train — it is a decent description of how any system, including a
person practising a skill, improves through corrected repetition. The tutorial
made it concrete; the idea is much larger than the code.

## Further reading

- [About vectors and matrices in machine learning](about-vectors-and-matrices-in-ml.md)
  — the matrices being adjusted are what gradient descent operates on.
- When the roadmap reaches **Neural Network Basics** and mentions
  backpropagation, return here: it is the chain rule from your tutorial, applied
  at scale.
