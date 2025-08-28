from __future__ import annotations

from pathlib import Path

from clipse.cli import main


def test_cli_validate_and_explain(monkeypatch) -> None:
    cfg = Path(__file__).parent.parent / "examples" / "example_config.json"
    assert cfg.exists()

    # validate
    rc = main(["validate", "--config", str(cfg)])
    assert rc == 0

    # explain json
    rc2 = main(["explain", "--config", str(cfg), "--format", "json"])
    assert rc2 == 0


def test_cli_list_styles() -> None:
    rc = main(["list-styles"])
    assert rc == 0
