# Tutorial: Your first steps with Linear Algebra for Machine Learning

In this tutorial, we will build up the core objects of linear algebra with our
own hands using Python and NumPy. Along the way we will create vectors and
matrices, multiply them, and finish by decomposing a matrix with the Singular
Value Decomposition — the same operation that powers dimensionality reduction in
machine learning.

By the end, you will have run every building block that appears again and again
in ML: scalars, vectors, tensors, matrix multiplication, determinants, inverses,
eigenvalues, and the SVD.

This tutorial should take about 30 minutes.

> This is a learning exercise. It does not matter if you already know some of
> this — what matters is that you *do* each step and watch what happens.

## Before we start

You need Python 3 with NumPy installed. Let's check. In a terminal, run:

```bash
python -c "import numpy; print(numpy.__version__)"
```

You should see a version number printed, something like:

```
1.26.4
```

If instead you see an error, install NumPy first:

```bash
pip install numpy
```

Now open a new file called `linear_algebra.py` in your editor. We will add to it
step by step and run it each time.

## Step 1 — Create a scalar, a vector, and a tensor

Type the following into `linear_algebra.py`:

```python
import numpy as np

scalar = np.array(7)
vector = np.array([2, 5, 3])
matrix = np.array([[1, 2],
                   [3, 4]])
tensor = np.array([[[1, 2], [3, 4]],
                   [[5, 6], [7, 8]]])

print("scalar ndim:", scalar.ndim)
print("vector ndim:", vector.ndim)
print("matrix ndim:", matrix.ndim)
print("tensor ndim:", tensor.ndim)
```

Run it:

```bash
python linear_algebra.py
```

The output should look exactly like this:

```
scalar ndim: 0
vector ndim: 1
matrix ndim: 2
tensor ndim: 3
```

Notice that `ndim` grows by one each time: `0, 1, 2, 3`. This number is the
count of axes an array has. A scalar has none, a vector has one, a matrix has
two, and a tensor has three or more. This is the vocabulary you will use to
describe every piece of data in an ML model.

Try changing `vector` to `np.array([2, 5, 3, 9, 1])` and run again. Notice the
`ndim` stays `1` — adding more numbers does not add an axis. Change it back
before continuing.

## Step 2 — Do arithmetic on vectors

Add these lines to the bottom of the file:

```python
a = np.array([1, 2, 3])
b = np.array([4, 5, 6])

print("sum:", a + b)
print("scaled:", 3 * a)
print("dot product:", np.dot(a, b))
```

Run the file again. You should now see, appended to the previous output:

```
sum: [5 7 9]
scaled: [3 6 9]
dot product: 32
```

Notice that `a + b` and `3 * a` work element by element, but the dot product
collapses two vectors into a single number: `1*4 + 2*5 + 3*6 = 32`. The dot
product is how a neural network combines inputs with weights, so this one number
matters a lot.

Run the file once more. Confirm you get `32` again — the same input always gives
the same result.

## Step 3 — Multiply matrices

Add:

```python
M = np.array([[1, 2],
              [3, 4]])
N = np.array([[5, 6],
              [7, 8]])

print("M @ N =")
print(M @ N)
```

Run it. The new output should be:

```
M @ N =
[[19 22]
 [43 50]]
```

Notice the `@` operator does matrix multiplication, not element-by-element
multiplication. The top-left value `19` comes from the first row of `M` dotted
with the first column of `N`: `1*5 + 2*7 = 19`. Every layer of a neural network
is a matrix multiplication like this one.

## Step 4 — Determinant and inverse

Add:

```python
det = np.linalg.det(M)
inv = np.linalg.inv(M)

print("determinant:", round(det, 1))
print("inverse =")
print(inv)
print("M @ inverse =")
print(np.round(M @ inv, 1))
```

Run it. You should see:

```
determinant: -2.0
inverse =
[[-2.   1. ]
 [ 1.5 -0.5]]
M @ inverse =
[[1. 0.]
 [0. 1.]]
```

Notice the last result: multiplying `M` by its inverse gives the identity matrix
(ones on the diagonal, zeros elsewhere). That is the definition of an inverse.
The determinant being non-zero (`-2.0`) is what guarantees the inverse exists.

Let's check what happens when it does not exist. Temporarily change `M` to:

```python
M = np.array([[1, 2],
              [2, 4]])
```

Run again. The determinant now prints `0.0` and `np.linalg.inv` raises a
`LinAlgError`. That error is linear algebra telling you the matrix cannot be
inverted. Change `M` back to the original before continuing.

## Step 5 — Eigenvalues and diagonalization

Add:

```python
M = np.array([[2, 0],
              [0, 3]])

values, vectors = np.linalg.eig(M)
print("eigenvalues:", values)
print("eigenvectors =")
print(vectors)
```

Run it. You should see:

```
eigenvalues: [2. 3.]
eigenvectors =
[[1. 0.]
 [0. 1.]]
```

Notice the eigenvalues `2.` and `3.` are exactly the numbers on the diagonal of
`M`. Eigenvalues tell you the amounts by which a matrix stretches space along
special directions (the eigenvectors). This is the idea underneath Principal
Component Analysis, which you will meet later in the roadmap.

## Step 6 — Singular Value Decomposition

Now for the finale. Add:

```python
A = np.array([[3, 1, 1],
              [1, 3, 1]])

U, S, Vt = np.linalg.svd(A)
print("singular values:", np.round(S, 3))

reconstructed = U @ np.diag(S) @ Vt[:2, :]
print("reconstruction matches original:",
      np.allclose(A, reconstructed))
```

Run the file one last time. You should see:

```
singular values: [4.243 2.   ]
reconstruction matches original: True
```

Notice two things. First, the SVD broke our matrix `A` into three pieces
(`U`, `S`, `Vt`). Second, when we multiplied those pieces back together, we
recovered the original matrix exactly — `np.allclose` returned `True`. The
singular values `[4.243, 2.0]` rank the "importance" of each direction in the
data; keeping only the largest ones is exactly how dimensionality reduction
compresses data.

Run this step two or three more times. Each run should print the same singular
values and `True`. Getting the same result every time is the confidence that
you have done it correctly.

## What we did

You have, with your own hands:

- created scalars, vectors, matrices, and tensors, and told them apart by `ndim`
- added and scaled vectors, and computed a dot product
- multiplied two matrices with `@`
- found a determinant and an inverse, and seen when an inverse cannot exist
- computed eigenvalues and eigenvectors
- decomposed a matrix with the SVD and reconstructed it perfectly

Every one of these appears constantly in machine learning: data lives in
tensors, models are matrix multiplications, and decompositions like SVD compress
and denoise data.

## Where to go next

- Try the next tutorial: [Calculus for Machine Learning](02-calculus.md).
- For understanding *why* ML is built on this in the first place, read
  [About vectors and matrices in machine learning](explanations/about-vectors-and-matrices-in-ml.md).
- When you want to understand *why* the SVD works and where it reappears, read
  [About the Singular Value Decomposition](explanations/about-the-svd.md).
- For the exact function signatures, see the
  [NumPy linear algebra reference](https://numpy.org/doc/stable/reference/routines.linalg.html).
