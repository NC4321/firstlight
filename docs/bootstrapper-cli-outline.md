# Project Bootstrapper CLI — Build Outline

## What it does
A command-line tool that scaffolds a new project with your preferred structure, config, and boilerplate in one command — instead of manually copying files or re-googling "how do I set up X" every time.

## Core features (v1)
- `bootstrap new <project-name>` — creates a new project folder
- Prompts (or flags) for:
  - Language/stack (e.g. Python, Node/TS, Go)
  - License (MIT, Apache-2.0, none)
  - Whether to init git + make first commit
  - Whether to init a remote GitHub repo (via `gh` CLI if available)
- Generates:
  - README.md template (title, description, install, usage, license sections)
  - `.gitignore` matched to the chosen stack
  - LICENSE file with your name + year auto-filled
  - Basic folder structure (`src/`, `tests/`, etc., stack-dependent)
  - CI config stub (GitHub Actions workflow for lint/test, stack-dependent)
  - Pre-commit config (optional flag)

## Stretch features (v2+)
- Custom templates: let user define their own template folder (`~/.bootstrap/templates/`) and pick from it
- Config file (`.bootstraprc` or similar) to save default preferences (name, email, license, default stack) so you're not re-answering prompts every time
- Support for monorepo scaffolding (multiple packages)
- Plugin system so others can add stack support without touching core code

## Tech decisions to make
- **Language**: pick something you're comfortable shipping a CLI in (Python + `click`/`typer`, Node + `commander`/`oclif`, Go + `cobra` are all solid choices — Go/Node give you a single binary distribution, which is nice for install friction)
- **Distribution**: PyPI (`pip install`) or npm (`npx`) or a compiled binary via GitHub Releases
- **Templating**: simple string replacement is fine for v1; consider a templating engine (Jinja2, Handlebars) only if templates get complex

## Suggested repo structure
```
bootstrapper-cli/
├── src/
│   ├── cli.py (or index.ts)
│   ├── commands/
│   │   └── new.py
│   ├── templates/
│   │   ├── python/
│   │   ├── node/
│   │   └── go/
│   └── utils/
├── tests/
├── .github/workflows/ci.yml
├── README.md
├── LICENSE
└── pyproject.toml (or package.json)
```

## README must-haves (for the portfolio value)
- Problem statement: what annoyance this solves
- Demo GIF or terminal screenshot showing it in action
- Install instructions (one-liner if possible)
- Usage examples with actual command output
- "What I'd improve next" section — shows self-awareness and ongoing thinking

## Build order (suggested milestones)
1. Hardcode one stack (e.g. Python) end-to-end, no flags — prove the concept
2. Add CLI argument parsing + interactive prompts
3. Add a second stack to force generalizing the template system
4. Write tests for the generation logic (not just "it runs")
5. Add CI (lint + test on push)
6. Polish README, add demo GIF, publish to PyPI/npm
7. (Stretch) Add config file support and custom templates

## Notes for whoever picks this up
- Keep the template files as literal files on disk (not strings in code) — much easier to maintain and let others contribute new stacks
- Validate project name input (no spaces/special chars, check if folder already exists) early — this is a common source of bad first impressions in CLI tools
- Consider `--dry-run` flag to preview what would be created without writing files
