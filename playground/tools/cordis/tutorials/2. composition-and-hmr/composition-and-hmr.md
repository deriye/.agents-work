# Composing and reloading Cordis plugins

In this tutorial, we will treat the *composition* of an application — which
plugins are mounted, and when — as something we actively change while the program
runs. Along the way we will turn a plugin off without deleting it, replace a
running plugin with a new version and watch its resources unwind first, and track
down a plugin that loads silently and does nothing. By the end you will be able
to look at a running Cordis application and answer the question "what is actually
loaded right now, and why?"

We will keep writing plain TypeScript files and running them with Node, exactly as
before. Every step prints something to your terminal, so you can always see the
result of what you just did.

> This tutorial follows on from [Getting started with Cordis](./cordis.md). It
> assumes you already have the `cordis-tutorial` project from that lesson, with
> `cordis` and `tsx` installed. If you do not, work through that tutorial first —
> we will reuse its project and its habits here.

## What you need

- The `cordis-tutorial` project directory from the previous tutorial.
- A terminal and a text editor.

Move into the project directory you created before:

```sh
cd cordis-tutorial
```

Let's confirm the project is still in place. Run:

```sh
npm ls cordis
```

You should see a line like `cordis@4.0.0-rc.8` (your exact version may differ).
Good — we have a working project to build on.

## Turn a plugin on and off

The applications we composed earlier listed every plugin in `main.ts` and mounted
them all. But composition is a choice you make, and one of the most common choices
is simply *which plugins are active*. Let's build a tiny two-plugin application and
practise switching one of them off and on again.

Create `alpha.ts`:

```ts
import type { Context } from 'cordis'

export function apply(ctx: Context) {
  console.log('alpha is running')
}
```

Create `beta.ts`:

```ts
import type { Context } from 'cordis'

export function apply(ctx: Context) {
  console.log('beta is running')
}
```

Now compose both in `main.ts`:

```ts
import { Context } from 'cordis'
import { apply as alpha } from './alpha.ts'
import { apply as beta } from './beta.ts'

const ctx = new Context()
ctx.plugin(alpha)
ctx.plugin(beta)
```

Run it:

```sh
node --import tsx main.ts
```

You should see exactly this:

```
alpha is running
beta is running
```

Both plugins mounted, both ran. Now let's turn `beta` off *without removing it
from the file*, by commenting out the line that mounts it:

```ts
import { Context } from 'cordis'
import { apply as alpha } from './alpha.ts'
import { apply as beta } from './beta.ts'

const ctx = new Context()
ctx.plugin(alpha)
// ctx.plugin(beta)   // beta is kept in the file, just not mounted
```

Run it again:

```sh
node --import tsx main.ts
```

This time you see only:

```
alpha is running
```

`beta` is still imported and still sitting in the file — but because we did not
call `ctx.plugin(beta)`, Cordis never mounted it, so its `apply` never ran.
Composition is exactly this: the set of `ctx.plugin(...)` calls decides what your
application *is*. Uncomment the line again and rerun to confirm both come back —
flipping a plugin off and on is something you will do constantly while building.

Restore `main.ts` so both plugins are mounted before continuing:

```ts
import { Context } from 'cordis'
import { apply as alpha } from './alpha.ts'
import { apply as beta } from './beta.ts'

const ctx = new Context()
ctx.plugin(alpha)
ctx.plugin(beta)
```

## Replace a running plugin

Turning a plugin off and rerunning the whole program is one thing. The more
interesting trick is replacing a plugin *while the application keeps running* —
unloading the old version and loading a new one in its place. This is the heart of
what hot module replacement does for you automatically, and we can perform it by
hand to see the machinery clearly.

The reason this is safe is something you already saw in the first tutorial: when a
plugin unloads, Cordis unwinds every effect it registered. So replacing a plugin
means "unwind the old one completely, then start the new one" — no leftover timers,
no duplicated listeners.

Let's watch that happen. Create `worker.ts`, a plugin factory that stamps each
version with a label and runs a ticking effect:

```ts
import type { Context } from 'cordis'

export function makeWorker(version: string) {
  return function worker(ctx: Context) {
    console.log(`worker ${version} loading`)
    ctx.effect(() => {
      const timer = setInterval(() => console.log(`tick ${version}`), 100)
      return () => {
        clearInterval(timer)
        console.log(`worker ${version} cleaned up`)
      }
    })
  }
}
```

Now drive the swap from `main.ts`. We mount version `v1`, let it tick a few times,
then dispose it and mount `v2` in its place:

```ts
import { Context } from 'cordis'
import { makeWorker } from './worker.ts'

const ctx = new Context()
let fiber = ctx.plugin(makeWorker('v1'))

// After a moment, replace v1 with v2.
setTimeout(async () => {
  console.log('--- reloading ---')
  await fiber.dispose()
  fiber = ctx.plugin(makeWorker('v2'))
}, 350)

// Exit a little later so we can see v2 tick too.
setTimeout(() => process.exit(0), 700)
```

The key is the order inside the timeout: we `await fiber.dispose()` — which fully
unloads `v1` and runs its cleanup — *before* we mount `v2`. Run it:

```sh
node --import tsx main.ts
```

You should see something very close to this:

```
worker v1 loading
tick v1
tick v1
tick v1
--- reloading ---
worker v1 cleaned up
worker v2 loading
tick v2
tick v2
tick v2
```

Watch the middle of that output carefully. The moment we reload, `worker v1
cleaned up` prints *before* `worker v2 loading`. That ordering is the whole point:
the old version's timer is stopped and its effect unwound before the new version
gets a chance to start its own. No `tick v1` ever appears after the reload line —
the old timer is truly gone. This is why hot-reloading a plugin does not leak
resources or leave two copies running: unload always completes before load begins.

You may see a different number of `tick` lines depending on exact timing. That is
expected — the important thing is that the cleanup line for `v1` always appears
once, right after `--- reloading ---` and right before `v2` loads.

## Diagnose a plugin that never loads

There is a flip side to the dependency-driven loading you met with `inject`. A
plugin whose `inject` names a service that *nobody provides* does not fail — it
simply waits, printing nothing, in case a provider shows up later. That is a
perfectly legitimate state, but the first time you meet it, a silent plugin is
baffling. Let's create that situation on purpose and then learn to see it.

Create `needs-cache.ts`, a plugin that depends on a `cache` service we will never
provide:

```ts
import type { Context } from 'cordis'

export function apply(ctx: Context) {
  ctx.inject(['cache'], (ctx) => {
    console.log('needs-cache ran')
  })
}
```

Compose it in `main.ts`:

```ts
import { Context } from 'cordis'
import { apply as needsCache } from './needs-cache.ts'

const ctx = new Context()
ctx.plugin(needsCache)
```

Run it:

```sh
node --import tsx main.ts
```

The process exits and prints **nothing at all**. No `needs-cache ran`, and no
error. The plugin is waiting for a `cache` service that never arrives, so its
injected callback never runs — but nothing went wrong, so nothing is reported.
This silence is exactly what makes a missing dependency confusing, so let's build a
tool that makes the waiting visible.

Every context can enumerate its plugin registry and inspect the state of each
loaded plugin's fiber. Create `diagnose.ts`:

```ts
import { FiberState, type Context } from 'cordis'

export function apply(ctx: Context) {
  setTimeout(() => {
    let pending = 0
    for (const runtime of ctx.registry.values()) {
      for (const fiber of runtime.fibers) {
        if (fiber.state === FiberState.PENDING) pending++
      }
    }
    if (pending > 0) {
      console.log(`${pending} plugin(s) PENDING — a required service is missing`)
    } else {
      console.log('no plugins are PENDING')
    }
  }, 300)
}
```

The new pieces are `ctx.registry`, which lets us walk every plugin Cordis knows
about, and `FiberState`, the set of states a fiber can be in. We wait a short
moment for everything to settle, count any fibers still in the `PENDING` state —
the state a plugin sits in while it waits for a dependency — and report what we
found.

Add it to `main.ts` alongside the waiting plugin:

```ts
import { Context } from 'cordis'
import { apply as needsCache } from './needs-cache.ts'
import { apply as diagnose } from './diagnose.ts'

const ctx = new Context()
ctx.plugin(needsCache)
ctx.plugin(diagnose)
```

Run it:

```sh
node --import tsx main.ts
```

This time the silence is broken:

```
1 plugin(s) PENDING — a required service is missing
```

There it is — the plugin that printed nothing is now accounted for, and the state
tells you exactly why: it is `PENDING`, waiting on a service that has no provider.
When a plugin in your own applications does nothing and reports nothing, this is
the first thing to check.

Now let's prove the diagnosis is correct by *satisfying* the dependency. Create a
`cache.ts` service:

```ts
import { Service, type Context } from 'cordis'

declare module 'cordis' {
  interface Context {
    cache: CacheService
  }
}

export class CacheService extends Service {
  constructor(ctx: Context) {
    super(ctx, 'cache')
  }
}

export function apply(ctx: Context) {
  ctx.plugin(CacheService)
}
```

Add it to `main.ts` — order does not matter, as you learned when you met
`inject`:

```ts
import { Context } from 'cordis'
import { apply as needsCache } from './needs-cache.ts'
import { apply as diagnose } from './diagnose.ts'
import { apply as cache } from './cache.ts'

const ctx = new Context()
ctx.plugin(cache)
ctx.plugin(needsCache)
ctx.plugin(diagnose)
```

Run it once more:

```sh
node --import tsx main.ts
```

Now you see:

```
needs-cache ran
no plugins are PENDING
```

Notice both changes at once: `needs-cache ran` now prints, *and* the diagnostic
reports `no plugins are PENDING` instead of counting one. Once `cache` existed,
`needs-cache` left the pending state, its injected callback ran, and our
diagnostic found nothing waiting. Watching the count drop from one to zero the
moment the provider is present is the clearest possible confirmation that a silent
plugin was simply waiting for a dependency all along.

## What you have done

You have taken control of a running application's composition, and in doing so met
the tools Cordis gives you for managing it:

- You **turned a plugin off and on** by controlling whether it is mounted, keeping
  its code in the project while excluding it from the running application.
- You **replaced a running plugin** by disposing its fiber and mounting a new
  version, and you saw the old version's effects unwind completely *before* the
  new version loaded — the guarantee that makes hot reloading safe.
- You **diagnosed a silent plugin** by walking `ctx.registry` and checking each
  fiber's `FiberState`, turning an invisible `PENDING` wait into a visible count,
  then watched that count drop to zero by providing the missing service.

Every one of these produced a visible result in your terminal that you can
reproduce by rerunning the commands. If a plugin ever behaves in a way you do not
expect, come back to the registry-and-state technique from the last section — being
able to ask "what state is this fiber in?" is the single most useful habit for
understanding a live Cordis application.

## Where to go next

- The [Cordis primer](https://deepseek-harness.github.io/deepseek-harness/en/reference/cordis-primer) explains fibers, states, and the registry as connected concepts, rather than the hands-on slices you used here.
- The [full Cordis framework tutorial](https://deepseek-harness.github.io/deepseek-harness/en/develop/cordis-tutorial/06-composition-and-hmr) covers composition and hot module replacement using the `cordis.yml` loader and the dedicated HMR plugin, which automate by file-watching the manual swap you did in this lesson.
- The [Cordis repository](https://github.com/cordiverse/cordis) is where the framework itself lives.