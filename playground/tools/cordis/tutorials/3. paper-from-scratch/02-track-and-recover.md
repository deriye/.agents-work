# Track a sequence and roll it all back

In this tutorial we will grow the self-undoing effect from the previous lesson
into something a real component needs: a way to apply **many** effects and then
reverse **all** of them with a single call. We will build an *accumulator* that
collects each effect's inverse as it happens, and a `recover` step that runs the
whole thing back to the starting state. These are the paper's `track` and
`recover`.

As before, we write plain TypeScript and run it directly with Node. Every step
prints something so you can see exactly what happened.

> This continues the from-scratch series that began with
> `01-an-effect-that-undoes-itself.md`. If you have not done that tutorial yet,
> do it first — we build directly on its `context.ts`.

## What you need

- The `effect-from-scratch` project from the previous tutorial, including its
  `package.json` and `context.ts`.
- [Node.js](https://nodejs.org/) version 24 or newer.

If you are starting in a fresh directory, create `package.json` with:

```json
{
  "type": "module"
}
```

and recreate `context.ts`:

```ts
// The shared environment. In the paper this is the context type, written Γ.
export interface Context {
  services: Record<string, string>
}

export function createContext(): Context {
  return { services: {} }
}
```

## Build the effect context

In the last tutorial we held a single `undo` in a variable. That does not scale:
with many effects we would need many variables and would have to remember to call
them in the right order. Instead we bundle the live context together with one
growing **accumulator** of inverses. The paper calls this pair the *effect
context* and writes it `∂Γ = Γ × (Γ → Γ)`.

Create `track1.ts`:

```ts
import { createContext, type Context } from './context.ts'

type Effect = (ctx: Context) => (ctx: Context) => void

// An effect context: the live context plus an accumulator of inverses.
// (Paper: ∂Γ = Γ × (Γ → Γ).)
interface EffectContext {
  ctx: Context
  accumulator: (ctx: Context) => void
}

function createEffectContext(): EffectContext {
  return { ctx: createContext(), accumulator: () => {} }
}
```

The accumulator starts as a function that does nothing — the identity. That empty
function is the paper's starting accumulator `id`, the state in which there is
nothing to undo yet.

## Write track and recover

Now the two operations. `track` applies one effect and folds its inverse onto the
front of the accumulator. `recover` runs the accumulator, undoing everything.

Add this to `track1.ts`, below what you already have:

```ts
// track: apply an effect and fold its inverse onto the accumulator.
function track(ec: EffectContext, effect: Effect): void {
  const undo = effect(ec.ctx)
  const previous = ec.accumulator
  ec.accumulator = (ctx) => {
    undo(ctx)       // undo THIS effect first...
    previous(ctx)   // ...then everything applied before it.
  }
}

// recover: run the whole accumulator, reverting every tracked effect.
function recover(ec: EffectContext): void {
  ec.accumulator(ec.ctx)
  ec.accumulator = () => {}
}
```

Read the new accumulator carefully. When we track an effect, its `undo` goes
*in front of* whatever was there before. So the most recently applied effect will
be undone first. That ordering is deliberate, and we will see why it matters in a
moment.

## Track three effects and recover them at once

Let's define three effects and put `track`/`recover` to work. Add this to the
bottom of `track1.ts`:

```ts
const addLogger: Effect = (ctx) => {
  ctx.services.logger = 'ConsoleLogger'
  return (ctx) => { delete ctx.services.logger }
}
const addDatabase: Effect = (ctx) => {
  ctx.services.database = 'SqliteDriver'
  return (ctx) => { delete ctx.services.database }
}
const addCache: Effect = (ctx) => {
  ctx.services.cache = 'MemoryCache'
  return (ctx) => { delete ctx.services.cache }
}

const ec = createEffectContext()
const before = JSON.stringify(ec.ctx.services)
console.log('start:  ', before)

track(ec, addLogger)
track(ec, addDatabase)
track(ec, addCache)
console.log('applied:', JSON.stringify(ec.ctx.services))

recover(ec)
const after = JSON.stringify(ec.ctx.services)
console.log('recover:', after)
console.log('identical?', before === after)
```

We snapshot the empty start, track three effects, print the fully-loaded context,
then call `recover` once and compare.

Run it:

```sh
node track1.ts
```

You should see exactly this:

```
start:   {}
applied: {"logger":"ConsoleLogger","database":"SqliteDriver","cache":"MemoryCache"}
recover: {}
identical? true
```

Look at what happened. Three separate effects each added a service, and a
*single* `recover` call removed all three, landing back on an empty context.
The `identical? true` confirms the soundness invariant from the last tutorial now
holds across a whole **sequence** of effects, not just one. We never listed the
services to remove — the accumulator remembered them for us.

## See the reversal order

We claimed effects are undone in reverse order of how they were applied. Let's
make that visible instead of taking it on faith.

Create a new file `track2.ts` with `track`, `recover`, and the effect context
copied from before, but this time each effect *announces* when its inverse runs:

```ts
import { createContext, type Context } from './context.ts'

type Effect = (ctx: Context) => (ctx: Context) => void

interface EffectContext {
  ctx: Context
  accumulator: (ctx: Context) => void
}
function createEffectContext(): EffectContext {
  return { ctx: createContext(), accumulator: () => {} }
}
function track(ec: EffectContext, effect: Effect): void {
  const undo = effect(ec.ctx)
  const previous = ec.accumulator
  ec.accumulator = (ctx) => {
    undo(ctx)
    previous(ctx)
  }
}
function recover(ec: EffectContext): void {
  ec.accumulator(ec.ctx)
  ec.accumulator = () => {}
}

// Each effect announces when its inverse runs, so we can SEE the order.
function addStep(name: string): Effect {
  return (ctx) => {
    ctx.services[name] = 'on'
    return (ctx) => {
      console.log('  undoing', name)
      delete ctx.services[name]
    }
  }
}

const ec = createEffectContext()
console.log('applying: first, second, third')
track(ec, addStep('first'))
track(ec, addStep('second'))
track(ec, addStep('third'))

console.log('recovering:')
recover(ec)
```

Run it:

```sh
node track2.ts
```

You should see exactly this:

```
applying: first, second, third
recovering:
  undoing third
  undoing second
  undoing first
```

Notice the order: we applied `first`, `second`, `third`, but recovery undid
`third`, then `second`, then `first` — last in, first out. This is exactly how
you take apart what you built: you remove the last thing you added first. The
paper relies on this reverse ordering so that when each inverse runs, the context
looks just as it did right after that effect was applied — which is the only state
that inverse knows how to undo.

Run `node track2.ts` again to confirm you get the same three lines in the same
order. That stable, predictable teardown order is the behavior we were after.

## What you have built

You have built the paper's tracking-and-recovery machinery by hand:

- An **effect context** (`∂Γ`) that pairs the live context with an **accumulator**
  of inverses, starting from the do-nothing identity.
- **`track`**, which applies an effect and folds its inverse onto the accumulator.
- **`recover`**, which runs the accumulator to reverse every tracked effect in
  one call — in **reverse order**, back to the exact starting state.

You saw the whole sequence roll back to `{}` with `identical? true`, and you
watched the inverses fire last-in-first-out. Rerun either file any time to
reinforce the feel; try adding a fourth effect and predicting the recovery order
before you run it.

## Where to go next

We can now load a bundle of effects and tear it all down. That bundle *is* a
component's contribution. In the next tutorial we will wrap a sequence of tracked
effects into a loadable, unloadable **component**, so that "unload" is just
`recover` — the bridge from these mechanics to the paper's calculus of dynamic
composition.

- Next: `03-a-loadable-component.md`
- The same idea in the real framework: [Cordis framework tutorial](../cordis.md),
  the "Watch Cordis clean up after a plugin" section.
- The paper sections behind this tutorial: §3.1.1–§3.1.3 (`track`, `recover`,
  effect iterators).
```
