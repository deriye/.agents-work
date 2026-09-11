# An effect that undoes itself

In this tutorial we will build the smallest possible piece of the theory behind
the paper *A Programming Paradigm for Spatiotemporal Composability*: an **effect
that carries its own undo**. We will create a shared environment, change it, and
then reverse that change back to the exact state we started from — using nothing
but the value the effect handed back to us.

We will write plain TypeScript files and run them with Node directly, with no
build step. Every step prints something to your terminal, so you can always see
the result of what you just did.

> This is the first in a from-scratch series. Here we build the mechanism by
> hand so you can feel how it works. Later, the
> [Cordis framework tutorial](../cordis.md) shows the same idea inside the real
> framework, where `ctx.effect()` does this for you.

## What you need

- [Node.js](https://nodejs.org/) version 24 or newer, installed and on your `PATH`.
- A terminal and a text editor.

You do not need any prior experience with the paper, effect systems, or Cordis.
We will meet each idea by doing.

Let's check that Node is ready. In your terminal, run:

```sh
node --version
```

You should see a version number like `v24.0.0` or higher. Recent Node runs
TypeScript files directly, which is what lets us skip any build tooling.

## Set up the project

We will do everything inside one fresh directory. Create it and move into it:

```sh
mkdir effect-from-scratch
cd effect-from-scratch
```

Now create a single file called `package.json` with exactly this content:

```json
{
  "type": "module"
}
```

That one line lets us use `import` syntax in our `.ts` files. Without it, Node
would refuse the `import` lines with a `Cannot use import statement outside a
module` error. We are now ready to write code.

## Create the shared environment

Everything in the paper happens against a shared environment it calls the
**context**. We will represent it as a plain object that holds named services.

Create a file called `context.ts`:

```ts
// The shared environment. In the paper this is the context type, written Γ.
export interface Context {
  services: Record<string, string>
}

export function createContext(): Context {
  return { services: {} }
}
```

`createContext()` gives us a fresh, empty environment. Let's confirm we can make
one and change it.

Create `step1.ts`:

```ts
import { createContext } from './context.ts'

const ctx = createContext()
console.log('before:', JSON.stringify(ctx.services))

ctx.services.logger = 'ConsoleLogger'
console.log('after: ', JSON.stringify(ctx.services))
```

Run it:

```sh
node step1.ts
```

You should see exactly this:

```
before: {}
after:  {"logger":"ConsoleLogger"}
```

There it is: we started with an empty environment and added one service to it.
Right now, though, that change is permanent — we have no way to take it back. That
is the problem the rest of this tutorial solves.

## Make the change carry its own undo

Here is the central move of the paper. Instead of writing a function that only
*changes* the context, we write one that changes the context **and returns a
second function that reverses that exact change**.

The paper writes the type of such an effect as `Γ → Γ × (Γ → Γ)`: given a
context, produce the new context together with an inverse. We will write it in
TypeScript and watch it work.

Create `step2.ts`:

```ts
import { createContext, type Context } from './context.ts'

// An effect: given the context, it changes it AND returns a function
// that undoes exactly that change. (Paper: Γ → Γ × (Γ → Γ).)
type Effect = (ctx: Context) => (ctx: Context) => void

const addLogger: Effect = (ctx) => {
  ctx.services.logger = 'ConsoleLogger'
  return (ctx) => {
    delete ctx.services.logger
  }
}

const ctx = createContext()
console.log('start:   ', JSON.stringify(ctx.services))

const undo = addLogger(ctx)
console.log('applied: ', JSON.stringify(ctx.services))

undo(ctx)
console.log('reverted:', JSON.stringify(ctx.services))
```

Notice the shape of `addLogger`. When we call it, it makes its change *and* hands
back the `undo` function. We hold onto that `undo` and call it when we want the
change gone. We never wrote a separate "remove the logger" routine somewhere
else — the undo travels with the effect that created it.

Run it:

```sh
node step2.ts
```

You should see exactly this:

```
start:    {}
applied:  {"logger":"ConsoleLogger"}
reverted: {}
```

Watch the three lines in order. We started empty, the effect added the logger,
and then calling `undo` removed it again. The environment came back to where it
began, and the instructions for how to get there were supplied *by the effect
itself*.

## Prove the reversal is exact

"Looks empty again" is not quite the same as "is exactly what it was". Let's make
the runtime check that for us, so we can trust it rather than eyeball it.

Create `step3.ts`:

```ts
import { createContext, type Context } from './context.ts'

type Effect = (ctx: Context) => (ctx: Context) => void

const addLogger: Effect = (ctx) => {
  ctx.services.logger = 'ConsoleLogger'
  return (ctx) => {
    delete ctx.services.logger
  }
}

const ctx = createContext()
const before = JSON.stringify(ctx.services)

const undo = addLogger(ctx)
undo(ctx)

const after = JSON.stringify(ctx.services)
console.log('before:', before)
console.log('after: ', after)
console.log('identical?', before === after)
```

We snapshot the environment before applying the effect, apply and undo it, snapshot
again, and compare the two snapshots.

Run it:

```sh
node step3.ts
```

You should see exactly this:

```
before: {}
after:  {}
identical? true
```

That `identical? true` is the whole point of this tutorial. The paper calls the
guarantee behind it the **soundness invariant**: after an effect and its inverse,
the context is recovered to precisely its earlier state. You just watched that
invariant hold, checked by the machine.

Try running `node step3.ts` a second and third time. You will see `identical?
true` every time. Repeating a step and getting the same result is a good habit
while learning — it confirms the behavior is real and not a fluke of one run.

## What you have built

You have built the atom of temporal composability from the paper:

- A **context** — a shared environment you can change.
- An **effect** that, when applied, returns its own **inverse** — the function
  that undoes exactly what it did.
- A checked demonstration that applying an effect and then its inverse **recovers
  the original context exactly** (the paper's soundness invariant).

Everything you did produced a visible result in your terminal that you can
reproduce by rerunning the commands. If you want to reinforce the idea, change
`addLogger` to add a *different* service and adjust its undo to remove that one —
then rerun `step3.ts` and watch `identical? true` hold again.

## Where to go next

Right now we undo effects one at a time, by hand. Real components apply *many*
effects and must reverse *all* of them on removal. In the next tutorial we will
build an **accumulator** that collects every inverse as effects are applied, so a
single call rolls the whole sequence back to the start — the paper's `track` and
`recover`.

- Next: `02-track-and-recover.md`
- The same idea in the real framework: [Cordis framework tutorial](../cordis.md)
- The paper section behind this tutorial: §3.1.1 "Effect Context".
