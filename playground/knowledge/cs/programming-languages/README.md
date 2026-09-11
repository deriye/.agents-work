# Programming Languages

Language-specific notes and cross-language design patterns.

## Structure

| Path | What's inside |
|------|---------------|
| [languages/c](./languages/c/) | C — `practice/` (I/O drills, problems) |
| [languages/cpp](./languages/cpp/) | C++ — `practice/` (I/O drills) |
| [languages/go](./languages/go/) | Go |
| [languages/js](./languages/js/) | JavaScript — `projects/stable-matching` |
| [languages/rust](./languages/rust/) | Rust — `projects/rust-todo` |
| [oop](./oop/) | OOP design patterns: adapter, bridge, composite, composition-over-inheritance |

## Convention

`languages/<lang>/` holds a language's material; `oop/<pattern>/` holds one design pattern each with its own
`README.md`. Within a language, a coherent build goes in `projects/`, while loose single-file drills and
exercises go in `practice/` (e.g. `practice/io/`, `practice/problems/`) — nothing runnable floats at the
language root. See the [playground README](../../../README.md).
