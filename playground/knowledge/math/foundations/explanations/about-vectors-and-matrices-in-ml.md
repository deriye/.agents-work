# About vectors and matrices in machine learning

> This is an **explanation** article. It is meant to be read away from the
> keyboard, to deepen your understanding after you have worked through the
> [Linear Algebra tutorial](../01-linear-algebra.md). It does not contain steps
> to follow — it discusses *why* machine learning is built on linear algebra.

## The question behind this article

In the tutorial you created vectors and matrices and multiplied them together,
and you were told, in passing, that "every layer of a neural network is a matrix
multiplication." That is a large claim to drop without discussion. Why should an
entire field of engineering choose to express itself in the language of two
hundred-year-old mathematics? Why vectors and matrices, rather than, say, plain
lists of `if`-statements?

This article is about that choice — where it comes from, what it buys us, and
what it quietly costs us.

## Data is naturally a grid of numbers

Start with the data. A single photograph is a grid of pixel brightnesses. A
spreadsheet of customers is a grid of rows and columns. A sentence, once each
word is turned into a list of numbers, is a grid too. The moment you decide to
process information numerically, you find yourself holding rectangular blocks of
numbers, whether you wanted to or not.

A vector is a single row (or column) of that block; a matrix is the whole
rectangle; a tensor is the same idea stacked into more dimensions, as when you
hold a batch of many images at once. The `ndim` count you printed in the
tutorial was not a mathematical curiosity — it was a direct measure of how the
data is shaped.

So the first reason ML speaks in vectors and matrices is almost embarrassingly
practical: **that is the shape the data already has.** Linear algebra is simply
the branch of mathematics that was built to manipulate rectangular blocks of
numbers, so it is the natural tool to reach for.

## A model layer is a weighted combination

The second reason is deeper. Consider the simplest possible model: it takes some
inputs, multiplies each by an importance weight, and adds the results up. That
"multiply-and-add" is exactly the dot product you computed when
`np.dot([1,2,3], [4,5,6])` returned `32`.

Now suppose you want not one weighted combination but many — one for each
"neuron" in a layer. Each neuron has its own row of weights. Stacking those rows
gives you a matrix, and applying all the neurons at once to an input vector is,
by definition, a matrix–vector multiplication:

```
   weights (matrix)      input      output
   [ w11 w12 w13 ]      [ x1 ]      [ y1 ]
   [ w21 w22 w23 ]  @   [ x2 ]  =   [ y2 ]
   [ w31 w32 w33 ]      [ x3 ]      [ y3 ]

   each output y_i is one dot product: row i of weights · input
```

This is not an analogy or a convenient notation. A dense neural-network layer
*is* this multiplication, followed by a simple non-linear function. When people
say a network has "millions of parameters," they mean the numbers inside
matrices like this one. The tutorial's `M @ N` was a two-neuron, two-input
version of the same machinery that runs inside every large language model.

## Why this abstraction is worth having

It would be possible, in principle, to write a model as a long tangle of
individual multiplications and additions. Choosing matrices instead brings three
advantages that are worth naming explicitly.

**It compresses the description.** One symbol, `W @ x`, stands for thousands of
coordinated arithmetic operations. A reader — or a mathematician proving a
property about the model — can reason about the whole layer at once instead of
tracking each number. This is the same benefit you get from writing `sum(xs)`
instead of a hand-written loop, scaled up enormously.

**It matches the hardware.** Graphics processing units (GPUs) were built to do
one thing extraordinarily fast: multiply large matrices. Because we chose to
express models as matrix multiplications, the entire modern ML industry gets to
ride on hardware that was, by a happy accident of history, already optimised for
exactly this operation. Had we expressed models as sprawling `if`-statements,
none of that acceleration would apply. The design decision and the hardware
reinforce each other — a good example of how a mathematical choice can have very
worldly consequences.

**It lets us borrow proven results.** Two centuries of mathematicians have
already worked out when a matrix can be inverted, what its eigenvalues mean, and
how to decompose it. By phrasing ML in their language, we inherit all of that
for free. The determinant and inverse you computed in the tutorial are not ML
inventions; ML simply gets to use them.

## What the abstraction costs

An honest explanation should weigh the other side. Expressing everything as
linear algebra has a real price, and it is worth being aware of it.

The most obvious cost is to *human* intuition. A single matrix multiplication is
easy to picture; a hundred of them chained together, operating in
thousand-dimensional space, is not. We lose the ability to see what the model is
"thinking," which is one reason the roadmap later includes a whole topic on
Explainable AI. The very compression that makes the mathematics tractable makes
the resulting model opaque.

There is also a subtler cost. Linear algebra, on its own, can only express
*linear* relationships — straight lines and flat planes. Real phenomena are
rarely so obliging. This is precisely why neural-network layers insert a
non-linear "activation function" between the matrix multiplications: without
those, stacking a hundred matrix layers would be mathematically identical to a
single matrix, and the model could never capture a curve. So the linear-algebra
foundation is necessary but, interestingly, *not sufficient* — it has to be
deliberately broken with non-linearity to be useful. That tension sits at the
heart of deep learning.

## How this connects to the rest of the roadmap

Once you see models as matrices, several later topics stop looking like separate
subjects and start looking like the same idea viewed from different angles:

- **Calculus** enters because, to train those matrices, we need to know how a
  small change to each weight affects the output — that is the gradient, and it
  is the subject of the next tutorial.
- **Dimensionality reduction and PCA** are about finding a *smaller* matrix that
  preserves most of the information in a larger one — which is where the SVD you
  met returns to centre stage (see
  [About the Singular Value Decomposition](about-the-svd.md)).
- **Deep learning libraries** such as PyTorch and TensorFlow are, at their core,
  tools for building and multiplying these matrices efficiently and for
  computing their gradients automatically.

The vocabulary you rehearsed in the tutorial — scalar, vector, matrix, tensor,
dot product — is therefore not a warm-up exercise you leave behind. It is the
language every remaining topic in the roadmap will be spoken in.

## Further reading

- [About the Singular Value Decomposition](about-the-svd.md) — the companion
  explanation for the decomposition you ran at the end of the tutorial.
- The 3Blue1Brown *Essence of Linear Algebra* video series is an excellent
  visual, reflective treatment of these same ideas.
