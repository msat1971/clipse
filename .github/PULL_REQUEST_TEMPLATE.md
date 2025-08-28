# PR Checklist

Please confirm the following before requesting review:

- [ ] Docstrings: All public modules/classes/functions updated to Google style.
- [ ] Examples: Each public API docstring includes an "Examples" section.
- [ ] Lint: `ruff check .` passes locally.
- [ ] Types: `mypy src` passes (or added TODOs/issues as needed).
- [ ] Tests: Added/updated unit tests for new/changed behavior.
- [ ] Docs: Updated user docs in `docs/` if behavior or usage changed.

Notes for reviewers:

- [ ] Breaking changes documented and migration guidance added (if any).
- [ ] Security/privacy implications considered (if any).
- [ ] Performance implications considered (if any).
