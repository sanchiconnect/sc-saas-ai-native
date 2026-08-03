# Onboarding — SanchiSaaS AI-Native Workspace

This gets a teammate's machine to the same state as the reference workspace: the 7 product repos, plus the workspace-level Claude Code layer (root `CLAUDE.md`, `.claude/` commands & agents, `specs/`) that makes this an "AI-native" setup rather than a plain poly-repo checkout.

**Read this in order — Part 1 is a hard prerequisite for Part 2 to make sense.**

---

## Part 1 — Understand the two layers

1. **The 7 product repos.** Each is its own git repo with its own GitHub remote, versioned/deployed independently (poly-repo, not a monorepo). Normal `git clone` access.
2. **The workspace-root orchestration layer.** `CLAUDE.md` (constitution), `.claude/commands/*.md`, `.claude/agents/*.md`, `.claude/hooks/`, `.claude/settings.json`, `specs/`, plus reference docs (`knowledge.md`, `design.md`, `database.md`, `api.md`, `README.md`, `AGENTS.md`, `AI-NATIVE-SETUP.md`). **This layer is intentionally NOT a git repo** — there is no remote to clone it from. It has to be copied to you directly (ask whoever set up the reference workspace to zip the workspace root — excluding the 7 repo subfolders, which are separately cloned — and send it to you, or check whether it's since been promoted to its own repo).

Don't skip layer 2 — without it you get a normal poly-repo checkout with no slash commands, no subagents, no cross-repo invariant docs, and no specs.

---

## Part 2 — Set up your machine

### 2.1 Prerequisites
- [Claude Code CLI](https://docs.claude.com/claude-code) installed and signed in with your own account (subscription/API access is per-person, not shared).
- Node.js (for the 3 NestJS repos + Angular frontend), PHP ≥8.1 + Composer (for the 2 PHP admin repos), Python 3.10+ (for `ai-startups-analyzer`).
- GitHub access to the `sanchiconnect` org's repos below — request from whoever manages repo access if you don't have it yet.
- Access to wherever your team stores secrets (`.env` values, DB creds, API keys) — **none of these are in git**, ask your team lead for the secure channel (vault / 1Password / etc.).

### 2.2 Create the workspace folder and clone the 7 repos

```bash
mkdir -p ~/Desktop/Work/SanchiSaaS && cd ~/Desktop/Work/SanchiSaaS

git clone https://github.com/sanchiconnect/sanchiconnect-saas-tenants.git
git clone https://github.com/sanchiconnect/sc-saas-backend.git
git clone https://github.com/sanchiconnect/sc-saas-frontend.git
git clone https://github.com/sanchiconnect/sc-saas-admin.git
git clone https://github.com/sanchiconnect/ai-startups-analyzer.git
git clone https://github.com/sanchiconnect/sc-saas-3rdparty-webservices.git
git clone https://github.com/sanchiconnect/sanchiconnect-saas-tenants-admin.git
```

Each repo's active development branch is **`ai_native_setup`** (not `main`) — after cloning, check out that branch in each repo:

```bash
for d in */; do (cd "$d" && git checkout ai_native_setup); done
```

### 2.3 Drop in the workspace-root layer

Once you have the layer-2 files (see Part 1), place them directly in `~/Desktop/Work/SanchiSaaS/` (the parent of the 7 repo folders), so the layout is:

```
SanchiSaaS/
├── CLAUDE.md
├── AI-NATIVE-SETUP.md
├── README.md, AGENTS.md, knowledge.md, design.md, database.md, api.md
├── .gitignore
├── .claude/
│   ├── settings.json          ← keep as-is
│   ├── settings.local.json    ← DO NOT copy this one; it's machine-specific, create your own (see 2.5)
│   ├── commands/*.md
│   ├── agents/*.md
│   └── hooks/guard-sensitive-files.sh
├── specs/
├── sanchiconnect-saas-tenants/       (cloned in 2.2)
├── sc-saas-backend/                 (cloned in 2.2)
├── sc-saas-frontend/                (cloned in 2.2)
├── sc-saas-admin/                   (cloned in 2.2)
├── ai-startups-analyzer/            (cloned in 2.2)
├── sc-saas-3rdparty-webservices/    (cloned in 2.2)
└── sanchiconnect-saas-tenants-admin/(cloned in 2.2)
```

### 2.4 Per-repo dependencies and `.env`

Each repo's own `CLAUDE.md` documents its exact run/build/test/lint commands. In short:

| Repo | Install | Env setup |
|---|---|---|
| `sanchiconnect-saas-tenants` | `npm install` | copy `.env.example` → `.env`, fill DB/JWT creds |
| `sc-saas-backend` | `npm install` | same — also needs the cockpit's URL at bootstrap |
| `sc-saas-frontend` | `npm install` | `src/environments/environment.local.ts` — cockpit base URL |
| `sc-saas-admin` | `composer install` | `config/db_settings.php` (gitignored) — tenant DB creds |
| `sanchiconnect-saas-tenants-admin` | `composer.phar install` | copy `.env.example` → `.env` — DB, JWT, AWS keys, role IDs |
| `sc-saas-3rdparty-webservices` | `npm install` | `.env` — only fill keys for providers you'll test locally |
| `ai-startups-analyzer` | `pip install -r requirements.txt` (or `poetry install`) | `.env` — DB, `DEFAULT_PROVIDER`, provider API keys |

Get the actual secret values from your team's secure channel — never from git, never from another teammate's Slack message.

### 2.5 Open the workspace in Claude Code

1. Open the **`SanchiSaaS/` root folder** (not a repo subfolder) in VS Code / your editor.
2. Launch Claude Code from the root — accept the workspace-trust prompt so `.claude/settings.json`, commands, agents, and the hook activate.
3. Start a **fresh session** after this — file-based commands/agents load at session start (`/agents` can load them interactively without a restart).
4. `.claude/settings.local.json` is gitignored/machine-specific — you don't need to copy the reference one; Claude Code will create an empty one for you as you approve permissions on your own machine.

### 2.6 Authenticate the MCP connectors (per-person, cannot be shared)

This workspace uses two MCP connectors — **Linear** (issue tracking) and **Sentry** (error monitoring). OAuth tokens are tied to your own account and can't be copied from another machine.

- Run `/mcp` inside a Claude Code session, select **Linear**, click **Authenticate**, complete the browser OAuth flow.
- Repeat for **Sentry**.
- Confirm both show `✔ Connected` via `/mcp` before relying on `/from-linear`, `/bug-fix`, or any Sentry-triage workflow.

### 2.7 Verify the setup

- `/onboard` — should produce a platform summary reading all 7 repos' `CLAUDE.md` files without complaining anything is missing.
- Ask a real question referencing a Linear issue (e.g. "what's SAN-1 about?") — confirms the Linear connector.
- Ask "what are the latest unresolved issues in the sc-saas-frontend Sentry project?" — confirms the Sentry connector.
- Each repo: run its documented lint/build command from its own `CLAUDE.md` and confirm it passes clean on a fresh checkout.

---

## What you get once this is done

- **Workspace slash commands**: `/onboard`, `/catchup`, `/cross-repo-review`, `/plan-feature`, `/trace-flag`, `/audit-contract`, `/check-isolation`, `/flag-impact`, `/spec-new`, `/spec-implement`, `/from-linear`, `/bug-fix`.
- **Cross-repo subagents**: `cross-repo-reviewer`, `feature-flag-mapper`, `api-contract-auditor`, `tenant-isolation-reviewer`, `flag-impact-planner`, `spec-author`, `spec-implementer`.
- **The spec system** (`specs/features/*.spec.md`, `<repo>/src/<module>/module.spec.md`) with per-repo master indexes.
- **Guardrails**: a `PreToolUse` hook that blocks writes to secrets/keys and flags edits to flag-definition/API-contract files for a second look.

Full detail on all of the above lives in `AI-NATIVE-SETUP.md` and the root `CLAUDE.md` once you have them.
