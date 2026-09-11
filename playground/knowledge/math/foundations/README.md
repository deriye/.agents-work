# Math Foundations for Machine Learning — Tutorials

A five-part, hands-on tutorial series covering the **Math Foundations** section
of the [roadmap.sh Machine Learning roadmap](https://roadmap.sh/machine-learning).

These are **tutorials** in the [Diátaxis](https://diataxis.fr/tutorials/) sense:
they are *learning-oriented* lessons where you learn by *doing*. Each step is a
small, concrete action in Python that produces a visible result you can check
against the expected output shown in the text.

## The series

Work through them in order — each one builds confidence for the next.

1. [Linear Algebra](01-linear-algebra.md) — scalars, vectors, tensors, matrix
   operations, determinants, inverses, eigenvalues, and the Singular Value
   Decomposition.
2. [Calculus](02-calculus.md) — derivatives, partial derivatives, the gradient,
   the chain rule, and a working gradient descent loop.
3. [Statistics](03-statistics.md) — descriptive statistics, charts, and a first
   step into inferential statistics.
4. [Probability](04-probability.md) — basic probability, distributions, random
   variables, and Bayes' Theorem.
5. [Discrete Mathematics](05-discrete-mathematics.md) — sets, counting, boolean
   logic, and graph traversal.

## Going deeper: explanations

The tutorials deliberately keep explanation to a minimum so you can focus on
*doing*. Once you have completed a tutorial and want to understand *why* things
work, read the matching **explanation** article. These follow the
[Diátaxis explanation](https://diataxis.fr/explanation/) style: they are
understanding-oriented, discursive, and meant to be read away from the keyboard.

| After this tutorial | Read this explanation |
|---|---|
| Linear Algebra | [About vectors and matrices in ML](explanations/about-vectors-and-matrices-in-ml.md) |
| Linear Algebra (SVD step) | [About the Singular Value Decomposition](explanations/about-the-svd.md) |
| Calculus | [About why gradient descent works (and when it doesn't)](explanations/about-why-gradient-descent-works.md) |
| Statistics | [About sampling and inference](explanations/about-sampling-and-inference.md) |
| Probability | [About probability and uncertainty](explanations/about-probability-and-uncertainty.md) |
| Discrete Mathematics | [About discrete structures in ML](explanations/about-discrete-structures-in-ml.md) |

## What you need

- Python 3
- NumPy and Matplotlib: `pip install numpy matplotlib`

Every tutorial begins with a quick check that your environment is ready.

## How to use these

- Type the code yourself rather than copy-pasting — the typing is part of the
  learning.
- Run the file after every step and compare with the expected output.
- Where a step invites you to change a value and re-run, do it. Repetition is
  how the ideas stick.
- These lessons deliberately keep explanation to a minimum. When you want to
  understand *why* something works, that is the job of an explanation article or
  a reference, linked at the end of each tutorial.
