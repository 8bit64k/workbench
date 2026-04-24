import sys

import pytest

from workbench.cli import main


def test_version_flag(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "--version"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "0.1.0" in captured.out


def test_bare_invocation_prints_help(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "usage:" in captured.out


def test_unknown_subcommand_exits_with_error(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "notacommand"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "invalid choice" in captured.err or "error" in captured.err.lower()


def test_list_command(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "list"])
    main()
    captured = capsys.readouterr()
    assert "python" in captured.out
    assert "library" in captured.out
    assert "cli" in captured.out
