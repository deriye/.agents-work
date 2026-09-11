# About discrete structures in machine learning

> This is an **explanation** article, for reflection after the
> [Discrete Mathematics tutorial](../05-discrete-mathematics.md). It discusses
> why sets, logic, and graphs — the "countable" side of mathematics — sit
> alongside the continuous mathematics of the other tutorials, and where each
> belongs. It contains no steps to follow.

## The question behind this article

The first four tutorials lived in a world of smooth, continuous quantities:
gradients that could take any value, distributions that flowed in bell curves,
matrices of real numbers. Then the fifth tutorial changed register entirely. You
worked with sets that either contained an element or did not, logic that was
strictly true or false, and a graph where a path either existed or it didn't.
Nothing was continuous; everything was countable and exact.

Why does machine learning need *both* kinds of mathematics? Why not pick one?
This article is about the division of labour between the continuous and the
discrete, and about why the systems around machine learning — as opposed to the
learning itself — are so often built from discrete structures.

## Two mathematical worlds, two kinds of question

It helps to name the distinction plainly. **Continuous mathematics** answers
questions of *how much* and *in which direction* — quantities that vary
smoothly and can be nudged by tiny amounts. That is the natural home of
learning: a model improves by adjusting its weights a hair at a time, which only
makes sense if "a hair" is meaningful. Gradient descent would be impossible in a
world of whole numbers, because you cannot take an infinitesimally small step in
integers.

**Discrete mathematics** answers questions of *which one*, *how many*, and
*is it connected* — matters that are exact and countable, with no in-between.
There is no "1.5th element" of a set, no "70% true" in classical logic, no "half
an edge" in a graph.

```
  continuous:  how much? which direction?     →  learning, optimisation
               (weights, gradients, curves)

  discrete:    which? how many? connected?     →  structure, decisions, data
               (sets, logic, graphs, counts)
```

Machine learning needs both because a working system does two different jobs. It
*learns* — a continuous process of gradual adjustment. And it *represents and
organises* — a discrete matter of categories, relationships, and choices. The
tutorials before the fifth taught the learning; the fifth taught the
scaffolding that learning hangs upon.

## Sets: the mathematics of "distinct things"

A set captures the simplest discrete idea: a collection of distinct items, no
duplicates, no order. This sounds humble, but it is everywhere the moment data
stops being purely numeric. The unique categories in a column ("red", "green",
"blue"), the vocabulary of distinct words in a body of text, the set of users
who clicked an advert — all are sets, and the intersection, union, and
difference you computed are how systems reason about them.

There is a bridge worth noticing here, because it explains something you will
meet later. Models cannot consume the *word* "blue"; they need numbers. So a
discrete set of categories gets converted into continuous vectors — a step
called *encoding* or *embedding*. The set defines *what the distinct things
are*; the continuous machinery then learns *how they relate*. The two
mathematical worlds meet exactly at this seam, and much of the practical art of
feature engineering lives right there.

## Logic: the mathematics of decisions

The truth table you built — `and`, `or`, and the quietly surprising `implies` —
is the mathematics of clean, binary decisions. Its most direct appearance in ML
is the **decision tree**, one of the models named later in the roadmap. A
decision tree is, quite literally, a cascade of logical tests: *is the
temperature above 30? and is the humidity high? then predict rain.* Each split
is a boolean question, and the tree is a structure of nested logic.

This is worth dwelling on because it reveals a genuine philosophical divide
among ML models. Some models — decision trees, rule systems — reason in crisp
discrete logic, and their great virtue is that a human can *read* the reasoning:
"it predicted rain because humidity was high." Other models — neural networks —
reason in continuous, tangled arithmetic, and buy accuracy at the price of
opacity. The choice between them is often a choice between *understandability*
and *raw performance*, and reasonable practitioners disagree about where to draw
that line. The humble truth table is one end of that spectrum.

## Graphs: the mathematics of relationships

The graph you built and searched is the discrete structure for representing
*relationships* — who connects to whom, what links to what. Its reach in modern
systems is enormous and easy to underestimate.

Social networks are graphs of people connected by friendship. Recommendation
systems are graphs of users connected to the items they liked, and a
recommendation is often a short path through that graph — "people connected to
what you bought were also connected to this." Knowledge graphs, which power many
question-answering systems, are graphs of facts connected by relationships. Even
the roadmap you are following is a graph: topics connected by edges, which is
literally how its data was stored.

The breadth-first search you ran matters because it answers the graph's most
common question — *what is the shortest path between two things?* — and it does
so with a guarantee: by exploring outward one ring at a time, the first time it
reaches the destination it has necessarily used the fewest possible hops. That
guarantee is why "degrees of separation" and shortest-route problems are solved
this exact way. An entire modern subfield, *graph neural networks*, exists to
let the continuous learning machinery operate directly on these discrete
relational structures — again, the two worlds meeting.

## Why exactness is a feature, not a limitation

It might seem that discrete mathematics is the poorer relation — rigid where
continuous mathematics is flexible. The opposite perspective is more useful:
**exactness is precisely what makes discrete structures trustworthy for the
parts of a system that must not be fuzzy.**

You do not want a "73% member" of a set of authorised users. You do not want a
recommendation engine that thinks two people are "somewhat connected" when the
question is whether a path exists at all. You do not want a decision audit trail
that reasons in probabilities when a regulator asks *why* a loan was refused.
The discrete world's refusal to blur is exactly its value: it is where a system
keeps the things that have to be definite. The continuous world, meanwhile,
keeps the things that have to be *learnable*. A well-built ML system is a
carefully negotiated partnership between the two.

## A perspective worth holding

The fifth tutorial can feel like a detour after the momentum of gradients and
distributions — a return to something more elementary. I would frame it
differently: it is the tutorial that describes the *world the model lives in*.
The other tutorials taught how a model learns; this one taught how its inputs
are categorised, how some models decide, and how its data relates. Learning
happens in the continuous world, but it is always surrounded by, fed by, and
accountable to the discrete one. Seeing both, and knowing which is which, is a
large part of thinking clearly about machine learning systems as a whole.

## Further reading

- [About vectors and matrices in machine learning](about-vectors-and-matrices-in-ml.md)
  — the continuous counterpart; note where encoding bridges the discrete set of
  categories into continuous vectors.
- When the roadmap reaches **Decision Trees** and **Recommendation Systems**,
  return here: they are the logic and graph ideas from your tutorial, grown into
  full models.
