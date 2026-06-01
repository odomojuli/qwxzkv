"""CLI smoke tests."""

import json

from typosquat.cli import main


def test_cli_text_output(capsys):
    assert main(["generate", "requests", "-e", "pypi", "--top", "5"]) == 0
    out = capsys.readouterr().out
    assert "candidates for 'requests'" in out
    assert "pypi" in out


def test_cli_json_output(capsys):
    assert main(["generate", "cross-env", "-e", "npm", "--json", "--top", "5"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert isinstance(data, list) and data
    assert {"name", "normalized", "risk", "families"} <= set(data[0])


def test_cli_family_filter(capsys):
    assert main(["generate", "requests", "--families", "omission", "--json"]) == 0
    data = json.loads(capsys.readouterr().out)
    assert all(c["families"] == ["omission"] for c in data)
