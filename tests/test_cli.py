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


def test_info_command_shows_template_details(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "info", "python"])
    main()
    captured = capsys.readouterr()
    assert "python" in captured.out
    assert "pyproject.toml" in captured.out or "files" in captured.out.lower()


def test_info_unknown_template_exits_with_error(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "info", "nonexistent"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 2
    captured = capsys.readouterr()
    assert "invalid choice" in captured.err or "not found" in captured.err.lower()


def test_init_dry_run_flag(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["workbench", "init", "python", "dry-proj", "--dry-run"])
    monkeypatch.chdir(tmp_path)
    main()
    captured = capsys.readouterr()
    assert "Would create" in captured.out
    assert "pyproject.toml" in captured.out
    assert not (tmp_path / "dry-proj").exists()


def test_init_output_flag(capsys, monkeypatch, tmp_path):
    out_dir = tmp_path / "custom"
    out_dir.mkdir()
    monkeypatch.setattr(sys, "argv", ["workbench", "init", "python", "out-proj", "--output", str(out_dir)])
    monkeypatch.chdir(tmp_path)
    main()
    captured = capsys.readouterr()
    assert "Created" in captured.out
    assert (out_dir / "out-proj" / "pyproject.toml").exists()
