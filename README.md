# ✨ firstlight

> In astronomy, **first light** is the moment a new telescope captures its first image.
> This tool is that moment for your code.

[![CI](https://github.com/NC4321/firstlight/actions/workflows/ci.yml/badge.svg)](https://github.com/NC4321/firstlight/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/firstlight)](https://pypi.org/project/firstlight/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

`firstlight` scaffolds a new project in one command: folder structure, README,
license, `.gitignore`, a working CI pipeline, a git repo with a first commit —
even the GitHub remote. For **Python**, **Node/TypeScript**, or **Go**.

<!-- demo.gif goes here: `vhs demo.tape` regenerates it -->

## The problem

Every new project starts with the same twenty minutes of ceremony: copy a
`.gitignore` from the last project, re-google "hatchling pyproject minimal",
paste the MIT license and update the year, write the same CI workflow again,
`git init`, first commit, create the repo. `firstlight` compresses all of it
into the ten seconds it deserves.

## Install

```bash
pipx install firstlight   # or: pip install firstlight
```

## Usage

Fully interactive — just answer the prompts:

```bash
firstlight new my-project
```

Or fully scripted — no prompts at all:

```bash
firstlight new sky-survey --stack python --license mit --git --github --public --no-input
```

Preview what would be created without writing a single file:

```text
$ firstlight new sky-survey --stack python --no-input --dry-run
dry run — nothing will be written

sky-survey/
├── .github/
│   └── workflows/
│       └── ci.yml (526 bytes)
├── .gitignore (93 bytes)
├── LICENSE (1063 bytes)
├── README.md (288 bytes)
├── pyproject.toml (667 bytes)
├── src/
│   └── sky_survey/
│       └── __init__.py (66 bytes)
└── tests/
    └── test_smoke.py (82 bytes)
```

Every generated project passes its own lint and tests out of the box — that's
enforced by firstlight's CI, which scaffolds all three stacks on every push and
runs each one's real toolchain (ruff/pytest, eslint/tsc/vitest, go vet/test).

### What you get per stack

| | Python | Node/TypeScript | Go |
|---|---|---|---|
| Package config | `pyproject.toml` (hatchling) | `package.json` (ESM) + strict `tsconfig` | `go.mod` |
| Starter code | `src/` layout + smoke test | `src/index.ts` + vitest test | `main.go` + table test |
| Lint | ruff (+ format) | eslint flat config | `go vet` + gofmt |
| CI stub | GitHub Actions matrix | GitHub Actions | GitHub Actions |

Plus, for every stack: README, stack-matched `.gitignore`, LICENSE
(MIT / Apache-2.0 / none) with your name and year filled in, optional
pre-commit config, `git init` + first commit, and optional
`gh repo create --push`.

### Saved defaults

Stop re-answering the same prompts:

```bash
firstlight config init    # author, email, default stack/license, GitHub user
firstlight config show
```

Precedence is always: explicit flag → prompt answer → config file → built-in
default. With `--no-input`, prompts are skipped and your config fills the gaps
(handy in scripts and CI).

## Design notes

- **Nothing touches disk until everything renders.** Templates render into an
  in-memory plan first; `--dry-run` and the writer are just two consumers of it.
  A typo'd template variable fails loudly (Jinja `StrictUndefined`) before any
  file exists.
- **Stacks are data, not code.** Adding a stack is one registry entry and one
  template directory — no branching logic anywhere else.
- **Templates are real files** shipped inside the wheel (with a uniform `.j2`
  suffix), not strings in code — easy to read, easy to contribute to.
- **git/gh failures never eat your scaffold.** All files are written before any
  git step runs, and a missing binary degrades to a warning with the manual
  command to run.

## What I'd improve next

- **Custom template directories** (`~/.config/firstlight/templates/`) so you can
  scaffold from your own project shapes, not just the built-ins.
- **A plugin system for stacks** — the registry is already data-only, so
  third-party stacks are mostly an entry-point discovery problem.
- **Monorepo scaffolding** (multiple packages in one repo).
- **`firstlight add`** — retrofit a single piece (CI, pre-commit, license) into
  an existing project instead of only creating new ones.

## Development

```bash
git clone https://github.com/NC4321/firstlight && cd firstlight
python -m venv .venv && source .venv/bin/activate
pip install -e .[dev]
pre-commit install
pytest
```

## License

MIT
