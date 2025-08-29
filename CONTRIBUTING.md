# Contributing

Thank you for contributing to Dclipse!

## Docstrings & Examples (Policy)

- All public modules, classes, functions, and methods must have docstrings using the Google style.
- Docstrings must include an "Examples" section demonstrating typical usage.
- Tests and examples folders are exempt from docstring requirements.

This policy is enforced via pre-commit (see below) and Ruff pydocstyle.

## Development Workflow

1. Create a virtualenv and install dev deps:

   ```bash
   pip install -e .[dev]
   ```

2. Install pre-commit hooks (runs on each commit):

   ```bash
   pre-commit install
   ```

3. Run formatters, linters, and tests locally:

   ```bash
   ruff check .
   mypy src
   pytest -q
   ```

4. When adding or changing public APIs:
   - Add/update docstrings with Args/Returns/Raises and an Examples section.
   - Update user docs in `docs/` as needed.
   - Add or update unit tests.

## Makefile & CI

See Makefile targets and CI workflow for automation details.

---

## Branching strategy (Git Flow)

We use a lightweight Git Flow model:

- `main`: production-ready, tagged releases only. Default/base branch.
- `develop`: integration branch for completed features.
- `feature/<name>`: short-lived branches for individual changes. Merge into `develop` via PR.
- `release/<x.y.z>`: stabilization for the upcoming release (optional). Merge into `main` and back-merge to `develop`.
- `hotfix/<x.y.z>`: urgent fixes off `main`; merge back to `main` and `develop`.

Typical flow:

1. Branch from `develop` → `feature/my-change`.
2. Open PR into `develop`.
3. After review + green CI, squash-merge to `develop`.
4. When ready to release, cut `release/x.y.z`, then PR to `main`.
5. Tag on `main` (e.g., `v1.2.3`).
6. Back-merge `main` → `develop`.

### Core idea (summary)

- **main**: always reflects production-ready code. Every commit on `main` should be deployable.
- **develop**: integration branch. All features/changes land here first — effectively the “next release candidate.”

### Typical workflow

- **Feature development**
  - Create a branch off `develop`, e.g., `feature/user-auth`.
  - Build, commit, and test on the feature branch.
  - Merge back into `develop` when done via PR.
- **Preparing a release**
  - When `develop` has enough features, cut `release/x.y.z`.
  - Do QA, bugfixes, and version bumps here.
  - Merge the release branch into both `main` (production) and `develop` (to keep `develop` up to date).
- **Hotfixes**
  - For urgent production issues, branch directly off `main` as `hotfix/x.y.z`.
  - Fix, then merge back into both `main` and `develop`.

### Why this pattern exists

It separates:

- What’s live now (**main**)
- What’s coming next (**develop**)
- Work in progress (**feature/release/hotfix** branches)

This separation is valuable for longer release cycles or when managing multiple versions in parallel.

### Branch protections (policy)

- `main` (strict):
  - Require PRs from non-`main` branches.
  - Require status checks to pass (CI, Docs) before merge.
  - Require linear history (squash merge) and at least 1 review.
  - Restrict direct pushes (maintainers only if urgently needed).
- `develop`:
  - Require PRs and passing checks.
  - Allow maintainers to update when needed.
- `gh-pages` (publish branch): managed by GitHub Pages Deploy Action. Do not push manually. Keep unprotected or allow GitHub Actions to bypass protection.

## Documentation deployment (GitHub Pages)

- Docs build is defined in `.github/workflows/docs.yml` (MkDocs Material).
- Triggers on pushes to `main` and `develop`.
- Deploys via `actions/deploy-pages` to the `github-pages` environment.
- The workflow publishes to the Pages site (backed by `gh-pages`). Avoid manual changes to `gh-pages`.

## CODEOWNERS

- The repository uses `.github/CODEOWNERS` for automatic review requests.
- Default owner is `@msat1971`. As the project grows, prefer GitHub Teams (e.g., `@org/docs`, `@org/core`).
- Keep ownership rules aligned with repo structure (source, tests, docs, workflows, schemas).

## Pull Request checklist

- [ ] Tests updated/added and passing (`pytest -q`).
- [ ] Lint + types pass (`ruff check .`, `mypy src`).
- [ ] Public APIs documented with Examples.
- [ ] Changelog entry if user-facing.
- [ ] Docs updated if behavior or usage changed.
