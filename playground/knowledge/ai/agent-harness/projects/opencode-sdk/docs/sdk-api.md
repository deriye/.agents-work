# OpenCode SDK API Reference

Type-safe JS client for opencode server.

## Installation

```bash
npm install @opencode-ai/sdk
```

## Client Creation

```js
import { createOpencode } from "@opencode-ai/sdk"
const { client } = await createOpencode()
```

### Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `hostname` | `string` | Server hostname | `127.0.0.1` |
| `port` | `number` | Server port | `4096` |
| `signal` | `AbortSignal` | Abort signal for cancellation | `undefined` |
| `timeout` | `number` | Timeout in ms for server start | `5000` |
| `config` | `Config` | Configuration object | `{}` |

## Client Only Mode

If you already have a running instance of opencode:

```js
import { createOpencodeClient } from "@opencode-ai/sdk"

const client = createOpencodeClient({
  baseUrl: "http://localhost:4096",
})
```

### Client Options

| Option | Type | Description | Default |
|--------|------|-------------|---------|
| `baseUrl` | `string` | URL of the server | `http://localhost:4096` |
| `fetch` | `function` | Custom fetch implementation | `globalThis.fetch` |
| `parseAs` | `string` | Response parsing method | `auto` |
| `responseStyle` | `string` | Return style: `data` or `fields` | `fields` |
| `throwOnError` | `boolean` | Throw errors instead of return | `false` |

---

## APIs

### Global

| Method | Description | Response |
|--------|-------------|----------|
| `global.health()` | Check server health and version | `{ healthy: true, version: string }` |

```js
const health = await client.global.health()
console.log(health.data.version)
```

---

### App

| Method | Description | Response |
|--------|-------------|----------|
| `app.log()` | Write a log entry | `boolean` |
| `app.agents()` | List all available agents | `Agent[]` |

```js
// Write a log entry
await client.app.log({
  body: {
    service: "my-app",
    level: "info",
    message: "Operation completed",
  },
})

// List available agents
const agents = await client.app.agents()
```

---

### Project

| Method | Description | Response |
|--------|-------------|----------|
| `project.list()` | List all projects | `Project[]` |
| `project.current()` | Get current project | `Project` |

```js
const projects = await client.project.list()
const currentProject = await client.project.current()
```

---

### Path

| Method | Description | Response |
|--------|-------------|----------|
| `path.get()` | Get current path | `Path` |

```js
const pathInfo = await client.path.get()
```

---

### Config

| Method | Description | Response |
|--------|-------------|----------|
| `config.get()` | Get config info | `Config` |
| `config.providers()` | List providers and default models | `{ providers: Provider[], default: { [key: string]: string } }` |

```js
const config = await client.config.get()
const { providers, default: defaults } = await client.config.providers()
```

---

### Sessions

| Method | Description | Response |
|--------|-------------|----------|
| `session.list()` | List sessions | `Session[]` |
| `session.get({ path })` | Get session | `Session` |
| `session.children({ path })` | List child sessions | `Session[]` |
| `session.create({ body })` | Create session | `Session` |
| `session.delete({ path })` | Delete session | `boolean` |
| `session.update({ path, body })` | Update session properties | `Session` |
| `session.init({ path, body })` | Analyze app and create `AGENTS.md` | `boolean` |
| `session.abort({ path })` | Abort a running session | `boolean` |
| `session.share({ path })` | Share session | `Session` |
| `session.unshare({ path })` | Unshare session | `Session` |
| `session.summarize({ path, body })` | Summarize session | `boolean` |
| `session.messages({ path })` | List messages in a session | `{ info: Message, parts: Part[] }[]` |
| `session.message({ path })` | Get message details | `{ info: Message, parts: Part[] }` |
| `session.prompt({ path, body })` | Send prompt message | `AssistantMessage` (supports structured output) |
| `session.command({ path, body })` | Send command to session | `{ info: AssistantMessage, parts: Part[] }` |
| `session.shell({ path, body })` | Run a shell command | `AssistantMessage` |
| `session.revert({ path, body })` | Revert a message | `Session` |
| `session.unrevert({ path })` | Restore reverted messages | `Session` |
| `postSessionByIdPermissionsByPermissionId({ path, body })` | Respond to a permission request | `boolean` |

```js
// Create and manage sessions
const session = await client.session.create({
  body: { title: "My session" },
})

const sessions = await client.session.list()

// Send a prompt message
const result = await client.session.prompt({
  path: { id: session.id },
  body: {
    model: { providerID: "anthropic", modelID: "claude-3-5-sonnet-20241022" },
    parts: [{ type: "text", text: "Hello!" }],
  },
})

// Inject context without triggering AI response (useful for plugins)
await client.session.prompt({
  path: { id: session.id },
  body: {
    noReply: true,
    parts: [{ type: "text", text: "You are a helpful assistant." }],
  },
})
```

---

### Files

| Method | Description | Response |
|--------|-------------|----------|
| `find.text({ query })` | Search for text in files | Array of match objects |
| `find.files({ query })` | Find files and directories by name | `string[]` (paths) |
| `find.symbols({ query })` | Find workspace symbols | `Symbol[]` |
| `file.read({ query })` | Read a file | `{ type: "raw" \| "patch", content: string }` |
| `file.status({ query? })` | Get status for tracked files | `File[]` |

`find.files` optional query fields:
- `type`: `"file"` or `"directory"`
- `directory`: override the project root for the search
- `limit`: max results (1-200)

```js
// Search and read files
const textResults = await client.find.text({
  query: { pattern: "function.*opencode" },
})

const files = await client.find.files({
  query: { query: "*.ts", type: "file" },
})

const directories = await client.find.files({
  query: { query: "packages", type: "directory", limit: 20 },
})

const content = await client.file.read({
  query: { path: "src/index.ts" },
})
```

---

### TUI (Terminal UI)

| Method | Description | Response |
|--------|-------------|----------|
| `tui.appendPrompt({ body })` | Append text to the prompt | `boolean` |
| `tui.openHelp()` | Open the help dialog | `boolean` |
| `tui.openSessions()` | Open the session selector | `boolean` |
| `tui.openThemes()` | Open the theme selector | `boolean` |
| `tui.openModels()` | Open the model selector | `boolean` |
| `tui.submitPrompt()` | Submit the current prompt | `boolean` |
| `tui.clearPrompt()` | Clear the prompt | `boolean` |
| `tui.executeCommand({ body })` | Execute a command | `boolean` |
| `tui.showToast({ body })` | Show toast notification | `boolean` |

```js
// Control TUI interface
await client.tui.appendPrompt({
  body: { text: "Add this to prompt" },
})

await client.tui.showToast({
  body: { message: "Task completed", variant: "success" },
})
```

---

### Auth

| Method | Description | Response |
|--------|-------------|----------|
| `auth.set({ ... })` | Set authentication credentials | `boolean` |

```js
await client.auth.set({
  path: { id: "anthropic" },
  body: { type: "api", key: "your-api-key" },
})
```

---

### Events

| Method | Description | Response |
|--------|-------------|----------|
| `event.subscribe()` | Server-sent events stream | Server-sent events stream |

```js
// Listen to real-time events
const events = await client.event.subscribe()
for await (const event of events.stream) {
  console.log("Event:", event.type, event.properties)
}
```

---

## Structured Output

Request structured JSON output by specifying a `format` with a JSON schema:

```js
const result = await client.session.prompt({
  path: { id: sessionId },
  body: {
    parts: [{ type: "text", text: "Research Anthropic and provide company info" }],
    format: {
      type: "json_schema",
      schema: {
        type: "object",
        properties: {
          company: { type: "string", description: "Company name" },
          founded: { type: "number", description: "Year founded" },
          products: {
            type: "array",
            items: { type: "string" },
            description: "Main products",
          },
        },
        required: ["company", "founded"],
      },
    },
  },
})

// Access the structured output
console.log(result.data.info.structured_output)
// { company: "Anthropic", founded: 2021, products: ["Claude", "Claude API"] }
```

### Output Format Types

| Type | Description |
|------|-------------|
| `text` | Default. Standard text response (no structured output) |
| `json_schema` | Returns validated JSON matching the provided schema |

### JSON Schema Format Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | `'json_schema'` | Required. Specifies JSON schema mode |
| `schema` | `object` | Required. JSON Schema object defining the output structure |
| `retryCount` | `number` | Optional. Number of validation retries (default: 2) |

---

## Types

Import TypeScript definitions directly:

```js
import type { Session, Message, Part } from "@opencode-ai/sdk"
```

All types are generated from the server's OpenAPI specification.

---

## Error Handling

```js
try {
  await client.session.get({ path: { id: "invalid-id" } })
} catch (error) {
  console.error("Failed to get session:", (error as Error).message)
}
```

For structured output errors:

```js
if (result.data.info.error?.name === "StructuredOutputError") {
  console.error("Failed to produce structured output:", result.data.info.error.message)
  console.error("Attempts:", result.data.info.error.retries)
}
```
