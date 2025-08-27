
# Clipse Config: Objects & Actions – Authoring Guide

This guide explains how to write a **style‑agnostic** CLI config using the *objects/actions* model and the JSON Schema you can validate against.

> Supports rendering into multiple styles: **noun–verb** (`yourcli address list`), **verb–noun** (`yourcli list address`), **unix** (`yourcli --action list --object address`), **shell** (`yourcli> list address`).

---

## File Structure

A config has these top‑level sections:

```json5
{
  "title": "...",                // optional metadata
  "description": "...",          // optional metadata
  "version": "0.1.0",            // optional metadata (project config version)
  "clipse_version": "https://json-schema.org/draft/2020-12/schema", // optional hint

  "shared_defs": { ... },        // reusable vars, options, objects, actions (no ids here)
  "global": { "options": [ ... ] },   // flags/options available everywhere

  "behavior": { ... },           // parsing and IO behavior
  "objects": [ ... ],            // object-centric definitions (each with actions)
  "actions": [ ... ]             // action-centric definitions (each with objects)
}
```

Either **objects** or **actions** may be empty; the **loader** builds the union of both views.

---

## Shared Definitions (`shared_defs`)

Like `components` in OpenAPI, you can define **blueprints** without `id`. Reference them elsewhere and override fields inline.

```yaml
shared_defs:
  vars:
    name: Your CLI
    cmd_name: yourcli
  options:
    dir:
      names: ["-d","--dir"]
      kind: option
      takes_value: true
      value_name: DIR
      type:
        kind: dir
        constraints: { relativity: absolute, exists: dir }
      env: { var: YOURCLI_DIR, override_cli: true, update: true }
  actions:
    delete:
      names: ["delete","rm"]
      description_short: Delete resource.
      options:
        - id: force
          $ref: "#/shared_defs/options/force"
  objects:
    foo:
      names: ["foo"]
      description_short: Foo(s)
```

> **Note:** items under `shared_defs` **do not need** `id`. When you *use* (`$ref`) them, you must provide an `id` at the use site.

---

## Global Options

Global options live under `global.options` and are available at any scope (root, any object, any action).

```json
{
  "global": {
    "options": [
      { "id": "help", "names": ["-h","--help","?"], "kind":"flag", "takes_value": false, "type":"boolean", "description_short":"Show help." },
      { "id": "version","names":["--version"], "kind":"flag","takes_value": false, "type":"boolean", "description_short":"Show version." }
    ]
  }
}
```

---

## Objects & Actions

You can define **objects in terms of actions** *and* **actions in terms of objects**. The loader merges these to form a complete graph.

### Object-centric (with actions)

```yaml
objects:
  - id: address
    names: ["address","addr"]
    description_short: Work with addresses.
    default_action: list
    actions:
      - id: create
        $ref: "#/shared_defs/actions/create"
        options:
          - id: name
            names: ["-n","--name"]
            kind: option
            takes_value: true
            type: string
            required: true
        positionals:
          - id: extra_files
            name: EXTRA_FILES
            kind: positional
            type: { kind: list, of: { kind: path } }
            arity: "0..*"
        constraints:
          requires: ["name"]
          exactly_one_of: [["template","from_config"]]
          at_least_one_of: [["dir","from_config"]]
          conflicts: [["from_config","template"],["from_config","extra_files"]]
```

### Action-centric (with objects)

```yaml
actions:
  - id: list
    names: ["list","ls"]
    description_short: List resources.
    objects:
      - "address"  # simple reference by id
      - id: school # override form
        description_short: List schools
        options:
          - id: region
            names: ["--region"]
            kind: option
            takes_value: true
            type: string
    default_object: address
```

---

## Options, Positionals, Env

- **Options** and **positionals** carry `id` and `type`.  
- `env` may be a **string** or an **object**:
  - String: `"env": "YOURCLI_DIR"` ⇒ `{ var: "YOURCLI_DIR", override_cli: false, update: false }`
  - Object: `{ "var": "YOURCLI_DIR", "override_cli": true, "update": true }`

Resolution precedence for a value (highest → lowest):
1. If `env.override_cli == true` and environment variable is set, **use env**.
2. Otherwise if CLI provided a value, **use CLI**.
3. Otherwise if environment variable is set, **use env**.
4. Otherwise if `default` is present, **use default**.
5. Else **missing** (validate against `required`, constraints).

If `env.update == true`, set/update the environment variable with the **final** resolved value.

---

## Variable Substitution (`{{ ... }}`)

- Strings can include `{{path}}` expressions.
- Lookup order: **current object scope** → `shared_defs.vars`.
- Examples: `{{id}}`, `{{vars.cmd_name}}`, `{{color.hue}}`.

> Substitution happens **before** schema validation of types for those fields (the loader works on the fully resolved document).

---

## Constraints

Use **ids** only (not flag names). Supported keys:

- `requires: ["name"]`
- `conflicts: [["from_config","template"],["from_config","extra_files"]]`
- `exactly_one_of: [["template","from_config"]]`
- `at_least_one_of: [["dir","from_config"]]`
- `custom: [{ "message": "...", "predicate": "if(from_stdin) then missing(extra_files)"}]`

---

## Examples (Scenarios)

Examples can be literal `cmd` strings or **style‑agnostic** `scenario` objects:

```json
{
  "description": "Create a web foo with two extra files.",
  "scenario": {
    "object": "foo",
    "action": "create",
    "options": { "name": "demo", "template": "web", "dir": "/opt/demo" },
    "positionals": { "extra_files": ["./a","./b"] }
  }
}
```

A renderer converts scenarios into concrete styles:

- noun–verb: `yourcli foo create …`
- verb–noun: `yourcli create foo …`
- unix: `yourcli --action create --object foo …`
- shell: `yourcli> create foo …`

---

## Loader Algorithm (Order, Precedence, Recursion)

**Inputs**: config JSON/YAML, optional standard types, environment, CLI argv.

**Steps**:

1. **Inline merge of `$ref`** (shallow fields override referenced fields). `$ref` targets may be within `shared_defs` or local fragments. When merging arrays like `options`/`positionals`, **dedupe by `id`**, prefer the referencing site’s entry.
2. **Variables**: resolve `{{...}}` with scope → `shared_defs.vars`. Recurse until stable or max depth (e.g., 10) to prevent cycles.
3. **Union build**:
   - `OBJECTS = ids(objects[]) ∪ ids(actions[].objects[]) ∪ ids(shared_defs.objects referenced via $ref)`
   - `ACTIONS = ids(actions[]) ∪ ids(objects[].actions[]) ∪ ids(shared_defs.actions referenced via $ref)`
4. **Defaults wiring**:
   - Validate each `objects[i].default_action ∈ ACTIONS`
   - Validate each `actions[j].default_object ∈ OBJECTS`
5. **Env/Value resolution** for each option/positional:
   - Apply precedence: env (if `override_cli` and set) → CLI → env → default.
   - If `env.update == true`, write final value back to env.
6. **Type checks** on resolved values (`type.kind`, constraints).
7. **Constraint checks** (`requires`, `conflicts`, `exactly_one_of`, `at_least_one_of`, `custom`).
8. **Schema validation** (post‑resolution) using the provided JSON Schema.
9. **Render** (outside loader): choose style and format command/execution usage.

**Failure modes**:
- Unknown `$ref`: fail with a pointer to the missing path.
- Circular substitution: detect after N expansions; report cycle path.
- Duplicate ids: report all duplicates with their object/action context.
- Type/constraint errors: collect and report per scope (global/object/action).

### Pseudocode (Python)

```python
def load_config(doc, env, argv):
    doc = merge_refs(doc)                 # step 1
    doc = resolve_vars(doc)               # step 2
    sets = build_unions(doc)              # step 3
    validate_defaults(doc, sets)          # step 4
    resolve_env_cli_defaults(doc, env, argv)  # step 5
    type_check(doc)                       # step 6
    constraint_check(doc)                 # step 7
    schema_validate(doc, SCHEMA)          # step 8
    return doc
```

---

## YAML vs JSON – Mini Examples

### JSON (object + action)

```json
{
  "objects": [
    {
      "id": "address",
      "names": ["address","addr"],
      "default_action": "list",
      "actions": [
        {
          "id": "create",
          "$ref": "#/shared_defs/actions/create",
          "options": [
            { "id": "name", "names": ["-n","--name"], "kind":"option", "takes_value":true, "type":"string", "required": true }
          ]
        }
      ]
    }
  ],
  "actions": [
    {
      "id": "list",
      "names": ["list","ls"],
      "objects": ["address"],
      "default_object": "address"
    }
  ]
}
```

### YAML (same idea)

```yaml
objects:
  - id: address
    names: ["address","addr"]
    default_action: list
    actions:
      - id: create
        $ref: "#/shared_defs/actions/create"
        options:
          - id: name
            names: ["-n","--name"]
            kind: option
            takes_value: true
            type: string
            required: true

actions:
  - id: list
    names: ["list","ls"]
    objects: ["address"]
    default_object: address
```

---

## Schema Check

After the loader resolves `$ref`s and variables, run JSON Schema validation (Draft 2020‑12) against the final document to catch structural drift. This guarantees:

- Every used option/positional has an `id` and valid `type`.
- `env` uses valid string or object form.
- Arrays are correctly structured and override points are legal.
- `examples` either `cmd` or `scenario` with `object` and `action` present.

---

## Loader Check (Integrity)

Before schema validation, perform these sanity checks:

- `default_object` exists among resolved **objects**.
- `default_action` exists among resolved **actions**.
- Every `objects[].actions[].id` is either fully inline or exists among resolved **actions**.
- Every `actions[].objects[]` entry resolves to a known **object**.
- No duplicate `id`s among options/positionals within the same scope.
- `conflicts`/`requires`/… reference **ids** that exist within the same scope.

---

## Rendering Notes

Projection into styles is outside the schema and controlled by the renderer:

- noun–verb: `yourcli <object> <action> ...`
- verb–noun: `yourcli <action> <object> ...`
- unix: `yourcli --action <action> --object <object> ...` (or `--list --address` projection)
- shell: `yourcli> <action> <object> ...`

Scenarios make examples portable across styles.

---

## Where to Go Next

- Add a tiny “renderer config” with templates for each style.
- Ship a `pytest` suite that loads `yourcli.config.json`, runs the loader, validates via schema, and snapshots rendered examples per style.
