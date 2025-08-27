
# Clipse Config: Objects & Actions – Authoring Guide

Author CLI specs that are **style‑agnostic** and map cleanly to noun–verb, verb–noun, unix, or shell renderings.  
**Schema target:** `https://github.com/msat1971/clipse/blob/develop/schema/clipse.schema.1.0.0.json`

---

## 1) Shape of the Document

- **Map‑based**: IDs are the **keys** for `objects`, `actions`, and their `options`/`positionals`.
- `shared_defs` provide reusable **blueprints**; items there have **no ids**.
- `global.options` is a map of true global flags/options.

```jsonc
{
  "title": "Example configuration file",
  "clipse_version": "https://github.com/msat1971/clipse/blob/develop/schema/clipse.schema.1.0.0.json",
  "shared_defs": { ... },
  "global": { "options": { ... } },
  "behavior": { ... },
  "objects": { ... },
  "actions": { ... }
}
```

### Objects (YAML)
```yaml
objects:
  foo:
    names: ["foo"]
    description_short: "Manage foo(s)."
    default_action: list
    actions:
      create:
        $ref: "#/shared_defs/actions/create"
        options:
          name:
            names: ["-n","--name"]
            kind: option
            takes_value: true
            type: string
            required: true
      delete:
        $ref: "#/shared_defs/actions/delete"
        positionals:
          foo_ref:
            name: FOO
            kind: positional
            type: string
            required: true
```

### Actions (JSON)
```json
{
  "actions": {
    "list": {
      "names": ["list","ls"],
      "description_short": "List object(s).",
      "objects": {
        "foo": { "description_short": "Lists foo(s)" },
        "bar": { "description_short": "Lists bar(s)" }
      },
      "default_object": "foo"
    }
  }
}
```

---

## 2) `$ref`, Overrides, and Merging

- `$ref` pulls from `shared_defs` and you may **override** fields at the use site.
- **Shallow merge** for scalars/objects.
- **Map fields** (`options`, `positionals`, `actions`, `objects`) merge **by key** with the use‑site winning on conflicts.

```json
{
  "objects": {
    "foo": {
      "actions": {
        "delete": {
          "$ref": "#/shared_defs/actions/delete",
          "description_short": "Delete a foo."
        }
      }
    }
  }
}
```

---

## 3) Variables (`{{ ... }}`)

- Strings may use `{{path}}` expressions, e.g., `{{id}}`, `{{vars.cmd_name}}`.
- Lookup order: **current scope** → `shared_defs.vars`.
- Resolve before validation of those fields; detect cycles.

---

## 4) Types & Environment Variables

**Types**
```json
{ "type": "string" }
{ "type": { "kind": "enum", "values": ["basic","web","api"] } }
{ "type": { "kind": "list", "of": { "kind": "path" } } }
```

**Environment binding**
```json
"env": "YOURCLI_DIR"
```
equals
```json
"env": { "var": "YOURCLI_DIR", "override_cli": false, "update": false }
```

**Precedence**
1) env (if `override_cli=true` and set) → 2) CLI value → 3) env (if set) → 4) `default` → 5) missing.

If `env.update=true`, set the environment variable to the final value.

---

## 5) Constraints (ID‑based)

Reference only **map keys** in the same scope:
```json
{
  "requires": ["name"],
  "conflicts": [["from_config","template"],["from_config","extra_files"]],
  "exactly_one_of": [["template","from_config"]],
  "at_least_one_of": [["dir","from_config"]]
}
```

---

## 6) Loader: Order & Checks

**Order**
1. Resolve `$ref`; shallow merge; maps by key (use‑site wins).
2. Resolve `{{...}}` variables with scope → `shared_defs.vars` (recurse until stable).
3. Build unions:
   - `OBJECTS = keys(objects) ∪ keys(actions[].objects) ∪ keys(shared_defs.objects used)`
   - `ACTIONS = keys(actions) ∪ keys(objects[].actions) ∪ keys(shared_defs.actions used)`
4. Validate defaults (`default_action`/`default_object` exist).
5. Resolve values (env/CLI/default precedence; apply `env.update`).
6. Type checks (incl. constraints).
7. Constraint checks (IDs exist in scope).
8. Schema validation against **clipse.schema.1.0.0.json**.

**Integrity checks**
- Unknown `$ref`, duplicate keys after merge.
- Circular variables.
- Missing defaults.
- Constraints targeting unknown ids.

---

## 7) Global Options (YAML & JSON)

```yaml
global:
  options:
    help:
      names: ["-h","--help","?"]
      kind: flag
      takes_value: false
      type: boolean
      description_short: Show help.
    verbose:
      names: ["-v","--verbose"]
      kind: flag
      takes_value: false
      type: count
      description_short: Increase verbosity.
```

```json
{
  "global": {
    "options": {
      "help":    { "names": ["-h","--help","?"], "kind":"flag", "takes_value": false, "type":"boolean", "description_short":"Show help." },
      "version": { "names": ["--version"], "kind":"flag", "takes_value": false, "type":"boolean", "description_short":"Show version and exit." }
    }
  }
}
```

---

## 8) Rendering (out of scope)

- noun–verb / verb–noun / unix / shell are projections from the object/action unions. Keep configs style‑neutral.
