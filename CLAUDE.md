# Ruflo — Claude Code Configuration

## Windows Execution (READ FIRST)

Windows 11 + PowerShell. Getting the shell wrong is the #1 source of friction.

- **Default to the PowerShell tool** for commands. Do NOT run the Bash tool with a `C:\...` path — its Git Bash strips backslashes. Use the Bash tool only for `/c/Users/...` POSIX paths.
- `npm` (npm.ps1), `uv` (`~/.local/bin`), `okx`, and `py` are on the PowerShell PATH ONLY, not Git Bash. A "não é reconhecido"/"not recognized" error means the wrong shell was used.
- `gh` is **NOT installed** — never use it; use `git` + the API instead.
- **No C compiler** (no gcc) — avoid deps that build wheels from source.

## Code Blocks: Only What He Should Run

He copies fenced blocks straight into PowerShell. On 2026-09-22 a block quoting
a broken `SendMessage({to: ...})` line — cited to *explain* a defect, never to be
run — went into his console and produced a cascade of "não é reconhecido", one
error per word. Nothing broke, but nothing needed to happen either.

So:

- **A fenced block is a promise that it is runnable.** Put a command there only
  when you mean for him to run it, and tag the language: ` ```powershell `,
  ` ```bash `. Never mix runnable lines with explanatory ones inside it.
- **Anything you are only quoting** — a line from a source file, a defect you are
  pointing at, the name of a Claude tool — goes in `inline backticks` or a
  blockquote, never in a fenced block. If it needs context, give the path and
  line number instead of pasting the block.
- **Claude tool calls are not shell commands.** `SendMessage`, `Agent`, `Task`,
  `Read` and the `mcp__*` tools exist only inside Claude. They will never run in
  PowerShell and must never be presented as if they could.
- Output you are showing him (test results, a CI log, a diff) is fine in a block
  — it is obviously not a command. Say so if it is ambiguous.

Note that the `Agent(...)`/`SendMessage(...)` block under **Agent Comms** below
breaks this rule: it is tagged `javascript` but its contents are Claude tool
calls, runnable nowhere. It stays because it documents a real pattern — treat it
as the example of what NOT to hand him in a console.

## Interpreters & Project Roots

Claude launches from `C:\Users\dre_l\.claude`, so always use **absolute paths** for project files.

- System Python = **3.10** at `C:\Users\dre_l\AppData\Local\Programs\Python\Python310` — do NOT use for project code; do NOT install the MS Store python.
- **autotrader** → `C:\Users\dre_l\autotrader` — use its `.venv\Scripts\python.exe` or `uv run` (Python 3.12), never bare `python`.
- **qlib** → `C:\Users\dre_l\Documents\qlib_project`.
- **Vault "Cérebro Claude"** → `C:\Users\dre_l\Desktop\Cerebro Claude` (the obsidian-mind repo).

## Network (TLS proxy)

Behind a TLS-intercepting proxy: `pypi.org`, GitHub downloads, and direct exchange HTTP (ccxt/okx/binance) frequently fail with SSL/cert errors.

- For OHLCV/market data, prefer the connected **MCP servers** (metatrader5 `get_candles_latest`, the OKX MCP, crypto.com `get_market_candles`) over ccxt/direct HTTP.
- For `uv`/`pip`, use `--native-tls` and a trusted cert bundle. Expect failures and use the escape hatch — don't loop blindly.

## Exchange / broker auth

- **OKX:** complete the device-code link immediately (expires fast). Re-auth: `okx auth login` — valid subcommands are `login`/`logout`/`status` only, there is **no `doctor`**. Invoke the `okx-cex-auth` skill on any "Session expired"/"codigo expirado"/"401".
- **MT5:** launch `terminal64.exe` and log into demo `10011606885` BEFORE any `metatrader5` tool; verify with `get_account_info`. Demo = can trade; live = read-only.

## Ruflo memory init

Ruflo memory may be uninitialized ("Memory store not found — run memory init"). Run `memory init` before the mandated `memory search`/`memory store` steps below, or skip them if init fails rather than erroring the whole task.

## Core Rules

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary — prefer editing existing files
- NEVER create documentation files unless explicitly requested
- NEVER save working files or tests to root — use `/src`, `/tests`, `/docs`, `/config`, `/scripts`
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files
- NEVER add a `Co-Authored-By` trailer unless attribution.commit is set
- Keep files under 500 lines
- Validate input at system boundaries

## Agent Comms (SendMessage-First Coordination)

Named agents coordinate via `SendMessage`, not polling or shared state.

```
Lead (you) ←→ architect ←→ developer ←→ tester ←→ reviewer
               (named agents message each other directly)
```

### Spawning a Coordinated Team

```javascript
// ALL agents in ONE message, each knows WHO to message next
Agent({ prompt: "Research the codebase. SendMessage findings to 'architect'.",
  subagent_type: "researcher", name: "researcher", run_in_background: true })
Agent({ prompt: "Wait for 'researcher'. Design solution. SendMessage to 'coder'.",
  subagent_type: "system-architect", name: "architect", run_in_background: true })
Agent({ prompt: "Wait for 'architect'. Implement it. SendMessage to 'tester'.",
  subagent_type: "coder", name: "coder", run_in_background: true })
Agent({ prompt: "Wait for 'coder'. Write tests. SendMessage results to 'reviewer'.",
  subagent_type: "tester", name: "tester", run_in_background: true })
Agent({ prompt: "Wait for 'tester'. Review code quality and security.",
  subagent_type: "reviewer", name: "reviewer", run_in_background: true })

// Kick off the pipeline
SendMessage({ to: "researcher", summary: "Start", message: "[task context]" })
```

## Ruflo Integration

When working on multi-file tasks or complex features, use ToolSearch to find and invoke ruflo MCP tools.

Key tools: `memory_store`, `memory_search`, `hooks_route`, `swarm_init`, `agent_spawn`.

Check system-reminder tags for [INTELLIGENCE] pattern suggestions before starting work.