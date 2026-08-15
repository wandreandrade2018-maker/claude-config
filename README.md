# Claude Code — config versionada

Versionamento **local** da configuração do Claude Code do Dre: skills, agents,
commands e o `CLAUDE.md` global. Serve de backup e histórico de mudanças da
config — **sem remote por escolha** (ver segurança abaixo).

## O que está versionado

| Caminho | Conteúdo |
|---|---|
| `.agents/skills/` | Skills customizadas (okx-cex-*, autotrader-dev, mt5-connect, earn-hunter, …) |
| `.claude/agents/` | Definições de agents |
| `.claude/commands/` | Slash commands |
| `.claude/skills/` | Skills adicionais |
| `CLAUDE.md` | Instruções globais (setup, rotas de agentes, gotchas de ambiente) |

## Segurança — o que NUNCA entra (por design)

O `.gitignore` é **whitelist**: ignora tudo por padrão e libera só os caminhos
curados acima. Mesmo um `git add -A` distraído não commita:

- 🔑 **`.credentials.json`** — token de autenticação do Claude Code
- 💬 **`projects/**/*.jsonl`** — transcripts completos das conversas
- 🧠 **`memory/`** — perfil pessoal/financeiro (fica só na máquina)
- ⚙️ **`settings.local.json`**, `*.key`, `*.pem`, `.env` — segredos e config local
- 🗑️ **`history.jsonl`** e arquivos-lixo de shell

Defesa em duas camadas: a whitelist + regras explícitas de negação para os
segredos conhecidos (belt-and-suspenders).

## Por que só local

O `CLAUDE.md` e os SKILL.md descrevem o setup pessoal (paths, contas demo,
algoIds, rotinas) — não são segredos, mas são pessoais. Ficam versionados na
máquina com histórico; se um dia for publicar, criar um repo **privado** e
`git remote add` — a whitelist já protege o resto.

## Uso

```bash
cd C:\Users\dre_l\.claude
git add -A          # seguro: a whitelist só deixa entrar a config curada
git commit -m "..."
```
