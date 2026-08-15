# Ruflo — Claude Code Configuration

## Windows Execution (READ FIRST)

Windows 11 + PowerShell. Getting the shell wrong is the #1 source of friction.

- **Default to the PowerShell tool** for commands. Do NOT run the Bash tool with a `C:\...` path — its Git Bash strips backslashes (`cd C:\Users\dre_l\autotrader` → `cd C:Usersdre_lautotrader: No such file or directory`). Use the Bash tool only for `/c/Users/...` POSIX paths.
- `npm` (npm.ps1), `uv` (`~/.local/bin`), `okx`, and `py` are on the PowerShell PATH ONLY, not Git Bash. A "não é reconhecido"/"not recognized" error means the wrong shell was used.
- `gh` is **NOT installed** — never use it; use `git` + the API instead.
- **No C compiler** (no gcc) — avoid deps that build wheels from source.

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

## Rules

- Do what has been asked; nothing more, nothing less
- NEVER create files unless absolutely necessary — prefer editing existing files
- NEVER create documentation files unless explicitly requested
- NEVER save working files or tests to root — use `/src`, `/tests`, `/docs`, `/config`, `/scripts`
- ALWAYS read a file before editing it
- NEVER commit secrets, credentials, or .env files
- NEVER add a `Co-Authored-By` trailer to user commits unless this project's `.claude/settings.json` has `attribution.commit` set (#2078). The Claude Code Bash tool may suggest one in its default commit-message template — ignore it. `Co-Authored-By` is semantic authorship attribution under git/GitHub convention; the tool is the facilitator, not a co-author.
- Keep files under 500 lines
- Validate input at system boundaries
- NEVER re-send a recurring monitoring prompt by hand — set it up once with `/loop` (in-session) or a scheduled task (persistent). The OKX DEMO grid-bot *monitoring/notification* cadence is 3x/day — but this is SEPARATE from the `OKX_BotState_Collector` scheduled task, which is an HOURLY data collector feeding the Qlib dataset (`crypto_data/bot_state.csv`) and must stay hourly. Do NOT change `OKX_BotState_Collector` to 3x/day.

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

### Patterns

| Pattern | Flow | Use When |
|---------|------|----------|
| **Pipeline** | A → B → C → D | Sequential dependencies (feature dev) |
| **Fan-out** | Lead → A, B, C → Lead | Independent parallel work (research) |
| **Supervisor** | Lead ↔ workers | Ongoing coordination (complex refactor) |

### Rules

- ALWAYS name agents — `name: "role"` makes them addressable
- ALWAYS include comms instructions in prompts — who to message, what to send
- Spawn ALL agents in ONE message with `run_in_background: true`
- After spawning: STOP, tell user what's running, wait for results
- NEVER poll status — agents message back or complete automatically

## Swarm & Routing

### Config
- **Topology**: hierarchical-mesh (anti-drift)
- **Max Agents**: 15
- **Memory**: hybrid
- **HNSW**: Enabled
- **Neural**: Enabled

```bash
npx @claude-flow/cli@latest swarm init --topology hierarchical --max-agents 8 --strategy specialized
```

### Agent Routing

| Task | Agents | Topology |
|------|--------|----------|
| Bug Fix | researcher, coder, tester | hierarchical |
| Feature | architect, coder, tester, reviewer | hierarchical |
| Refactor | architect, coder, reviewer | hierarchical |
| Performance | perf-engineer, coder | hierarchical |
| Security | security-architect, auditor | hierarchical |

### When to Swarm
- **YES**: 3+ files, new features, cross-module refactoring, API changes, security, performance
- **NO**: single file edits, 1-2 line fixes, docs updates, config changes, questions

### 3-Tier Model Routing

| Tier | Handler | Use Cases |
|------|---------|-----------|
| 1 | Agent Booster (WASM) | Simple transforms — skip LLM, use Edit directly |
| 2 | Haiku | Simple tasks, low complexity |
| 3 | Sonnet/Opus | Architecture, security, complex reasoning |

## Memory & Learning

### Before Any Task
```bash
npx @claude-flow/cli@latest memory search --query "[task keywords]" --namespace patterns
npx @claude-flow/cli@latest hooks route --task "[task description]"
```

### After Success
```bash
npx @claude-flow/cli@latest memory store --namespace patterns --key "[name]" --value "[what worked]"
npx @claude-flow/cli@latest hooks post-task --task-id "[id]" --success true --store-results true
```

### MCP Tools (use `ToolSearch("keyword")` to discover)

| Category | Key Tools |
|----------|-----------|
| **Memory** | `memory_store`, `memory_search`, `memory_search_unified` |
| **Bridge** | `memory_import_claude`, `memory_bridge_status` |
| **Swarm** | `swarm_init`, `swarm_status`, `swarm_health` |
| **Agents** | `agent_spawn`, `agent_list`, `agent_status` |
| **Hooks** | `hooks_route`, `hooks_post-task`, `hooks_worker-dispatch` |
| **Security** | `aidefence_scan`, `aidefence_is_safe`, `aidefence_has_pii` |
| **Hive-Mind** | `hive-mind_init`, `hive-mind_consensus`, `hive-mind_spawn` |

### Background Workers

| Worker | When |
|--------|------|
| `audit` | After security changes |
| `optimize` | After performance work |
| `testgaps` | After adding features |
| `map` | Every 5+ file changes |
| `document` | After API changes |

```bash
npx @claude-flow/cli@latest hooks worker dispatch --trigger audit
```

## Agents

**Core**: `coder`, `reviewer`, `tester`, `planner`, `researcher`
**Architecture**: `system-architect`, `backend-dev`, `mobile-dev`
**Security**: `security-architect`, `security-auditor`
**Performance**: `performance-engineer`, `perf-analyzer`
**Coordination**: `hierarchical-coordinator`, `mesh-coordinator`, `adaptive-coordinator`
**GitHub**: `pr-manager`, `code-review-swarm`, `issue-tracker`, `release-manager`

Any string works as a custom agent type.

## Build & Test

- ALWAYS run tests after code changes
- ALWAYS verify build succeeds before committing

```bash
npm run build && npm test
```

## CLI Quick Reference

```bash
npx @claude-flow/cli@latest init --wizard           # Setup
npx @claude-flow/cli@latest swarm init --v3-mode     # Start swarm
npx @claude-flow/cli@latest memory search --query "" # Vector search
npx @claude-flow/cli@latest hooks route --task ""    # Route to agent
npx @claude-flow/cli@latest doctor --fix             # Diagnostics
npx @claude-flow/cli@latest security scan            # Security scan
npx @claude-flow/cli@latest performance benchmark    # Benchmarks
```

26 commands, 140+ subcommands. Use `--help` on any command for details.

## Setup

```bash
claude mcp add claude-flow -- npx -y ruflo@latest mcp start
npx ruflo@latest doctor --fix
```

> The background `daemon` is optional. It runs interval workers that each spawn
> a headless `claude` session, so it consumes tokens continuously. Start it only
> if you want those sweeps: `npx ruflo@latest daemon start` (self-stops after 12h
> by default; `--ttl 0` to disable, `daemon status --all` to audit running daemons).

**Agent tool** handles execution (agents, files, code, git). **MCP tools** handle coordination (swarm, memory, hooks). **CLI** is the same via Bash.

# Ruflo Integration (auto-generated by ruflo init)
When working on multi-file tasks or complex features, use ToolSearch to find and invoke ruflo MCP tools.
Key tools: memory_store, memory_search, hooks_route, swarm_init, agent_spawn.
Check system-reminder tags for [INTELLIGENCE] pattern suggestions before starting work.
