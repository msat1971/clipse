
# Clipse — Prompt Directives (Map‑Based)

**Mission**: design and evolve a spec‑first, style‑agnostic CLI using **objects** and **actions** as **maps keyed by id**.

## Core Rules
- **Schema target**: `https://github.com/msat1971/clipse/blob/develop/schema/clipse.schema.1.0.0.json`
- `objects`, `actions`, and inner `options`/`positionals` are **maps** (ids are keys).
- `shared_defs` hold blueprints with no ids; use `$ref` and override at use sites; shallow merge; maps merge by key (use‑site wins).
- `global.options` is a map of true global flags/options.
- Use **ids** in constraints; never flag spellings. Variables `{{...}}` resolve in scope → `shared_defs.vars`.

## Loader Order
1) Resolve `$ref` (merge rules above).  
2) Resolve variables.  
3) Build unions of objects/actions from both views.  
4) Validate defaults (`default_action`/`default_object`).  
5) Resolve values (env/CLI/default precedence; `env.update` honored).  
6) Type checks.  
7) Constraint checks.  
8) Validate against the schema.

## Env Semantics
- `env` may be `"ENV_NAME"` or `{ "var":"ENV_NAME","override_cli":false|true,"update":false|true }`.
- Precedence: env (if `override_cli=true` and set) > CLI > env > default > missing.

## Rendering
- Projections (noun–verb, verb–noun, unix, shell) come from the objects/actions unions; configs stay style‑neutral.

## Output Expectations
- When asked, produce downloadable config/docs/code/tests that pass ruff/mypy/pytest (per pyproject). Export `__version__`, `load_config`; include `py.typed`.
