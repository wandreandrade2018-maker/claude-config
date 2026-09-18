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
cd C:\Users\<seu-usuario>\.claude
git add -A          # seguro: a whitelist só deixa entrar a config curada
git commit -m "..."
```

## Site publicado (GitHub Pages)

O branch `gh-pages` guarda um site já buildado (MkDocs Material) e é servido
pelo GitHub Pages em <https://wandreandrade2018-maker.github.io/claude-config/>.
O repositório é público (necessário para o Pages no plano gratuito) e o
**Source** do Pages está configurado como **"GitHub Actions"** (não "Deploy
from a branch") — quem publica de fato é o workflow
[`.github/workflows/deploy-pages.yml`](.github/workflows/deploy-pages.yml).

### Como funciona o deploy

O workflow vive no `main` (não no `gh-pages`) porque o ambiente
`github-pages`, criado automaticamente pelo GitHub, só permite deploys
disparados a partir do branch padrão por política default — uma versão
anterior que vivia no próprio `gh-pages` era rejeitada em ~1s, sem rodar
nada. Ele faz checkout do conteúdo do `gh-pages` e publica com
`actions/upload-pages-artifact` + `actions/deploy-pages`.

Ele dispara de duas formas:
- **Automático**: depois que o workflow `CI` (`validate-config.yml`) passa
  no `main` (`workflow_run`).
- **Manual**: aba *Actions* → **Deploy GitHub Pages** → **Run workflow**
  (branch `main`).

### ⚠️ Importante: editar o site não publica sozinho

Um `git push` no `gh-pages` **não** dispara o deploy automaticamente — só
mudanças no `main` disparam (via `workflow_run`), e o ambiente não aceita
gatilho vindo do próprio `gh-pages`. Depois de qualquer alteração no
conteúdo do site, é preciso disparar o workflow manualmente (aba *Actions*
→ **Deploy GitHub Pages** → **Run workflow**) para a mudança ir ao ar.
