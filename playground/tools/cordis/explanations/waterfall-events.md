# About waterfall events in Cordis

Cordis lets a plugin announce that something happened without knowing who is
listening. Most of the time that announcement is a one-way broadcast: the sender
speaks, any number of listeners react, and nobody's reply is collected. A
*waterfall* is the mode that breaks this pattern deliberately — it turns the
event from an announcement into a **collaborative computation**, where the
listeners together produce a single result. This document is about why that mode
exists, how it relates to ordinary events, and what its design asks of you in
return.

It is meant to be read away from the keyboard. If you want to *do* something with
waterfalls, the [Getting started tutorial](./cordis.md) walks through a working
example step by step; here we are only reflecting on how the thing works and why
it is shaped the way it is.

## Where waterfall sits among the dispatch modes

It helps to see waterfall not as a special feature but as one point on a
spectrum. Cordis offers several *dispatch modes* — different answers to the
question "when I fire an event, what happens to what the listeners return?"

At one end is `emit`: fire and forget. Return values are discarded, listeners are
independent, and the order in which they run carries no meaning. This is the
right tool when an event is genuinely a notification — "a counter changed", "a
connection opened" — and the sender has no stake in any reply.

Modes like `serial` and `bail` sit in the middle: listeners run in order and the
*first* one to produce a meaningful value wins, ending the chain. Here return
values suddenly matter, and so does order, but each listener still either answers
or defers — it cannot reshape another listener's answer.

Waterfall sits at the far end. Its listeners do not merely run in order; they are
*nested inside one another*. Each one is handed the others' work and may wrap it,
replace it, or let it pass. The mental model is no longer a list of listeners but
a stack of layers, and that difference is the whole reason the mode exists.

The important consequence is that **a waterfall event's mode is part of its
contract, not an implementation detail.** When you declare an event as a
waterfall — by giving its listeners a `next` parameter — you are promising every
listener that it will be able to intervene in the result. A listener written for
`emit` and a listener written for `waterfall` are not interchangeable, because
they make different assumptions about what their return value means.

## The shape of a waterfall: nesting, not sequence

The defining feature of a waterfall is that each listener receives a `next`
continuation alongside the event's arguments. Calling `next()` means "run
everything downstream of me and give me the result"; whatever a listener returns
becomes the result seen by the listener *above* it. At the very bottom sits the
default function that the caller passed to `ctx.waterfall(...)`, which runs only
if every listener chooses to descend all the way.

This produces two directions of travel that an ordinary event does not have. On
the way *down*, control passes from the outermost listener inward, one `next()`
call at a time, until it reaches the default. On the way *back up*, a value
returns through each listener in reverse, and each one has the opportunity to
transform it before handing it on. A single listener therefore participates
twice: once before it calls `next()`, and once after.

It is worth dwelling on why this is so powerful. Because a listener runs code
both before and after the downstream result exists, it can do things that a flat
list of handlers simply cannot: it can measure how long the rest of the chain
took, it can catch a failure from below and substitute a fallback, or — most
commonly — it can take the downstream answer and refine it. This is the same
structure that web frameworks call *middleware* and that functional programmers
recognise as function composition. Cordis did not invent it; it borrowed a shape
that has proven itself repeatedly, precisely because "wrap the thing below me" is
such a recurring need.

## The veto, and why silence is dangerous

A listener does not have to call `next()`. If it returns without doing so, the
descent stops where it is: nothing further down runs, *including the default*,
and the value the listener returned becomes the result that flows back up. The
Cordis documentation calls this the **veto**, and it is the feature that lets a
single listener answer on behalf of the whole chain — a policy plugin deciding an
outcome outright, say, rather than letting the default path be taken.

The veto is genuinely useful, but it carries a hazard that is worth understanding
rather than merely memorising. Consider a listener whose author only meant to
*observe* the result — to log it, or record a metric. If that author forgets to
call `next()` and simply lets the function end, the listener has, without
intending to, issued a veto. Everything downstream — every other listener, and
the default behaviour itself — is silently skipped. Nothing errors; the chain
simply produces the wrong answer, and does so quietly.

This is why the repository treats a rule as non-negotiable: **a waterfall
listener that only observes or annotates must call `next()`.** The reasoning is
not stylistic. It follows directly from the fact that in a waterfall, *not*
calling `next()` is itself a meaningful action — it is the veto. There is no
neutral way to "just look" at a waterfall; you are either a participant who
passes control on, or you are the one who ends the chain. Framing it that way
turns an easy-to-forget rule into an obvious consequence of the design.

## Why not just use return values everywhere?

A fair question is why Cordis bothers with a distinct waterfall mode at all,
rather than letting every listener return a value and combining them somehow. The
answer is that different situations want different combining rules, and no single
rule fits them all.

Sometimes you want *all* listeners to run regardless of what they return — that
is `emit`, and forcing a return-value protocol onto it would only add ceremony.
Sometimes you want the *first* usable answer and nothing more — that is `serial`
and `bail`. And sometimes you want listeners to *build on each other's* answers,
which requires handing each listener the downstream result before it decides what
to return — and that is only expressible with a continuation like `next`. The
`next` parameter is not decoration; it is the minimal machinery needed to let a
listener see downstream work before contributing its own.

Seen this way, the proliferation of modes is a feature rather than clutter. Each
mode encodes a specific, common relationship between listeners, so that the
relationship lives in the event's declaration where every reader can see it,
instead of being reinvented ad hoc inside each handler. Waterfall is simply the
mode reserved for the case where listeners collaborate on one evolving value.

## How this connects to the rest of Cordis

Two connections are worth drawing, because they show that waterfall is not an
isolated trick but part of Cordis's larger character.

First, listeners are registered with the same `ctx.on(...)` used for ordinary
events, and that registration is an *effect*. This means a waterfall listener is
torn down automatically when its plugin unloads, exactly like a timer or a
service — you never unsubscribe by hand. The interception layer a plugin adds
therefore has the same lifetime as the plugin itself, which is what makes it safe
for plugins to wrap each other's behaviour: remove the plugin, and its layer in
the waterfall vanishes with it.

Second, waterfall is how Cordis-based systems let cooperating plugins negotiate
decisions that no single plugin owns. When one plugin may need to replace a
request before it is sent, or another may need to answer a prompt instead of the
user, a waterfall lets each plugin insert itself as a layer without any of them
knowing about the others. The event name is the only thing they share. This is
the same decoupling that ordinary events provide — sender and listener meet only
through a name — extended to the richer case where the listeners are shaping a
result rather than merely being told about one.

That, ultimately, is the point of waterfall events. Plain events let plugins stay
ignorant of *who* reacts to an announcement. Waterfall events let them stay
ignorant of *who else is shaping a result*, while still contributing to it — which
is what makes it possible to assemble sophisticated, layered behaviour out of
small plugins that were never written with each other in mind.
