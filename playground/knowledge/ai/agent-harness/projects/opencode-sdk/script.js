import { createOpencode } from "@opencode-ai/sdk"

const opencode = await createOpencode({
    port: 5001,
})

console.log(`Server running at ${opencode.server.url}`)

opencode.server.close()