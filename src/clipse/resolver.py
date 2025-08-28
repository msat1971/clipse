"""Config resolution: expand refs, render variables, and validate constraints.

This module turns a raw clipse configuration into a resolved representation and
collects any constraint issues for reporting in CLI commands.
"""

from __future__ import annotations

import copy
import os
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Optional

from .schema import validate_core_config

_JSON_POINTER_RE = re.compile(r"^#(/[^/]+)*$")
_VAR_RE = re.compile(r"\{\{\s*vars\.([a-zA-Z0-9_\-]+)\s*\}\}")


@dataclass(frozen=True)
class ResolutionResult:
    """Result of resolving a config: the resolved doc and any issues."""
    resolved: dict[str, Any]
    issues: list[str]


class ResolutionError(Exception):
    """Raised for invalid references or resolution-time errors."""


def _json_pointer_get(doc: Mapping[str, Any], pointer: str) -> Any:
    """Resolve a local JSON Pointer ("#/...") within ``doc``.

    Args:
        doc: Document to traverse.
        pointer: Local JSON Pointer starting with '#'.

    Returns:
        The value located at the pointer.

    Raises:
        ResolutionError: If the pointer is malformed or points to a non-existent path.
    """
    if not _JSON_POINTER_RE.match(pointer):
        raise ResolutionError(f"Unsupported $ref; must be local JSON Pointer, got: {pointer}")
    cur: Any = doc
    if pointer == "#":
        return cur
    for token_enc in pointer.lstrip("#/").split("/"):
        token = token_enc.replace("~1", "/").replace("~0", "~")
        if not isinstance(cur, Mapping) or token not in cur:
            raise ResolutionError(f"Invalid $ref path segment: {token!r} in {pointer}")
        cur = cur[token]
    return cur


def _merge(a: Mapping[str, Any], b: Mapping[str, Any]) -> dict[str, Any]:
    """Deep-merge two mappings with ``b`` overriding ``a`` recursively for dicts."""
    out: dict[str, Any] = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, Mapping):
            out[k] = _merge(out[k], v)
        else:
            out[k] = copy.deepcopy(v)
    return out


def _render_vars_in_str(s: str, vars_map: Mapping[str, Any], *, id_value: Optional[str] = None) -> str:
    """Render ``{{vars.KEY}}`` and optional ``{{id}}`` placeholders in a string."""
    def rep(m: re.Match[str]) -> str:
        key = m.group(1)
        val = vars_map.get(key)
        return str(val) if val is not None else m.group(0)

    s2 = _VAR_RE.sub(rep, s)
    if id_value is not None:
        s2 = s2.replace("{{id}}", id_value)
    return s2


def _render_vars_in_obj(obj: Any, vars_map: Mapping[str, Any], *, id_value: Optional[str] = None) -> Any:
    """Recursively render placeholders within strings nested in ``obj``."""
    if isinstance(obj, str):
        return _render_vars_in_str(obj, vars_map, id_value=id_value)
    if isinstance(obj, list):
        return [_render_vars_in_obj(x, vars_map, id_value=id_value) for x in obj]
    if isinstance(obj, dict):
        return {k: _render_vars_in_obj(v, vars_map, id_value=id_value) for k, v in obj.items()}
    return obj


def _collect_selected_keys(section: Mapping[str, Any]) -> list[str]:
    """Collect option/positional keys used to evaluate constraints."""
    return list(section.keys())


def _validate_constraints(selected: list[str], constraints: Mapping[str, Any]) -> list[str]:
    """Evaluate constraint rules and return human-readable issue strings."""
    errs: list[str] = []
    sel = set(selected)
    req = constraints.get("requires", [])
    for name in req:
        if name not in sel:
            errs.append(f"requires: missing {name}")
    for pair in constraints.get("conflicts", []):
        a, b = pair[0], pair[1]
        if a in sel and b in sel:
            errs.append(f"conflicts: {a} vs {b}")
    for group in constraints.get("exactly_one_of", []):
        n = sum(1 for k in group if k in sel)
        if n != 1:
            errs.append(f"exactly_one_of violation: {group} present={n}")
    for group in constraints.get("at_least_one_of", []):
        n = sum(1 for k in group if k in sel)
        if n < 1:
            errs.append(f"at_least_one_of violation: {group}")
    return errs


def _apply_refs(doc: dict[str, Any]) -> dict[str, Any]:
    """Walk objects/actions and expand local ``$ref`` with shallow-merge overrides."""
    def process_mapping(mapping: dict[str, Any]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, val in mapping.items():
            if isinstance(val, Mapping) and "$ref" in val:
                base = _json_pointer_get(doc, str(val["$ref"]))
                if not isinstance(base, Mapping):
                    raise ResolutionError(f"$ref must point to a mapping: {val['$ref']}")
                merged = _merge(copy.deepcopy(base), {k: v for k, v in val.items() if k != "$ref"})
                out[key] = merged
            else:
                out[key] = copy.deepcopy(val)
        return out

    resolved: dict[str, Any] = copy.deepcopy(doc)
    if "objects" in resolved and isinstance(resolved["objects"], Mapping):
        objs: dict[str, Any] = process_mapping(dict(resolved["objects"]))
        for key, obj in list(objs.items()):
            if isinstance(obj, Mapping) and "actions" in obj and isinstance(obj["actions"], Mapping):
                obj_dict: dict[str, Any] = dict(obj)
                obj_dict["actions"] = process_mapping(dict(obj["actions"]))
                objs[key] = obj_dict
        resolved["objects"] = objs
    if "actions" in resolved and isinstance(resolved["actions"], Mapping):
        resolved["actions"] = process_mapping(dict(resolved["actions"]))
    # global options already direct; options under nodes may have $ref which process_mapping handled
    return resolved


def resolve_config(raw: dict[str, Any], *, env: Optional[Mapping[str, str]] = None) -> ResolutionResult:
    """Resolve a raw config and collect any constraint issues.

    Steps:
      - Validate against the core schema.
      - Expand local ``$ref`` and merges.
      - Render ``{{vars.*}}`` and ``{{id}}`` placeholders.
      - Collect constraint issues for objects and actions.

    Args:
        raw: The input configuration mapping.
        env: Optional environment mapping (reserved for future use).

    Returns:
        A ``ResolutionResult`` containing the resolved document and issues.

    Examples:
        >>> from clipse.resolver import resolve_config
        >>> res = resolve_config({"objects": {}})
        >>> isinstance(res.resolved, dict) and isinstance(res.issues, list)
        True
    """
    validate_core_config(raw)
    env = env or os.environ
    doc = _apply_refs(raw)

    vars_map: Mapping[str, Any] = {}
    if isinstance(doc.get("shared_defs"), Mapping) and isinstance(doc["shared_defs"].get("vars"), Mapping):
        vars_map = doc["shared_defs"]["vars"]  # type: ignore[assignment]

    # Render vars across top-level string fields and within objects/actions descriptions
    doc = _render_vars_in_obj(doc, vars_map)

    issues: list[str] = []

    # Validate constraints at object and action levels using present option/positional keys
    if isinstance(doc.get("objects"), Mapping):
        for obj_id, obj in doc["objects"].items():
            if not isinstance(obj, Mapping):
                continue
            opts = obj.get("options", {}) if isinstance(obj.get("options"), Mapping) else {}
            poss = obj.get("positionals", {}) if isinstance(obj.get("positionals"), Mapping) else {}
            selected = _collect_selected_keys({**opts, **poss})
            if isinstance(obj.get("constraints"), Mapping):
                issues += [f"object {obj_id}: {e}" for e in _validate_constraints(selected, obj["constraints"])]
            if isinstance(obj.get("actions"), Mapping):
                for act_id, act in obj["actions"].items():
                    if not isinstance(act, Mapping):
                        continue
                    aopts = act.get("options", {}) if isinstance(act.get("options"), Mapping) else {}
                    apos = act.get("positionals", {}) if isinstance(act.get("positionals"), Mapping) else {}
                    sel = _collect_selected_keys({**aopts, **apos})
                    if isinstance(act.get("constraints"), Mapping):
                        issues += [
                            f"object {obj_id} action {act_id}: {e}"
                            for e in _validate_constraints(sel, act["constraints"])
                        ]

    if isinstance(doc.get("actions"), Mapping):
        for act_id, act in doc["actions"].items():
            if not isinstance(act, Mapping):
                continue
            aopts = act.get("options", {}) if isinstance(act.get("options"), Mapping) else {}
            apos = act.get("positionals", {}) if isinstance(act.get("positionals"), Mapping) else {}
            sel = _collect_selected_keys({**aopts, **apos})
            if isinstance(act.get("constraints"), Mapping):
                issues += [f"action {act_id}: {e}" for e in _validate_constraints(sel, act["constraints"])]

    return ResolutionResult(resolved=doc, issues=issues)
