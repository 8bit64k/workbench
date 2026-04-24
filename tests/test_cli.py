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
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Unknown template" in captured.err


def test_init_unknown_template_shows_suggestion(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "init", "pthon", "bad-proj"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "Unknown template" in captured.err
    assert "python" in captured.err.lower()  # Should suggest 'python'


def test_list_with_no_templates_shows_warning(capsys, monkeypatch, tmp_path):
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    monkeypatch.setattr(sys, "argv", ["workbench", "--template-dir", str(empty_dir), "list"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 0
    captured = capsys.readouterr()
    assert "Warning: No templates found." in captured.out


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


def test_init_quiet_suppresses_output(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["workbench", "init", "python", "quiet-proj", "--quiet"])
    monkeypatch.chdir(tmp_path)
    main()
    captured = capsys.readouterr()
    assert "Created" not in captured.out
    assert (tmp_path / "quiet-proj" / "pyproject.toml").exists()


def test_init_verbose_shows_debug_info(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["workbench", "init", "python", "verbose-proj", "--verbose"])
    monkeypatch.chdir(tmp_path)
    main()
    captured = capsys.readouterr()
    assert "Created" in captured.out
    # Verbose should include extra context
    assert "template" in captured.out.lower() or "files" in captured.out.lower()


def test_init_uses_custom_template_dir(capsys, monkeypatch, tmp_path):
    custom_dir = tmp_path / "custom_templates"
    custom_dir.mkdir()
    # Create a minimal custom template
    tpl = custom_dir / "custom"
    tpl.mkdir()
    (tpl / "pyproject.toml.j2").write_text("[project]\nname = \"{{project_name}}\"\n")
    monkeypatch.setattr(sys, "argv", ["workbench", "--template-dir", str(custom_dir), "init", "custom", "custom-proj"])
    monkeypatch.chdir(tmp_path)
    main()
    target = tmp_path / "custom-proj"
    assert target.exists()
    assert (target / "pyproject.toml").exists()
    assert "custom_proj" in (target / "pyproject.toml").read_text()


def test_list_shows_custom_templates(capsys, monkeypatch, tmp_path):
    custom_dir = tmp_path / "custom_templates"
    custom_dir.mkdir()
    (custom_dir / "alpha").mkdir()
    (custom_dir / "beta").mkdir()
    monkeypatch.setattr(sys, "argv", ["workbench", "--template-dir", str(custom_dir), "list"])
    main()
    captured = capsys.readouterr()
    assert "alpha" in captured.out
    assert "beta" in captured.out


def test_validate_passes_for_good_template(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "validate", "python"])
    main()
    captured = capsys.readouterr()
    assert "valid" in captured.out.lower() or "pass" in captured.out.lower()


def test_validate_fails_for_broken_jinja(capsys, monkeypatch, tmp_path):
    from workbench.scaffold import TEMPLATE_DIR
    # Create a temporary broken template
    broken = tmp_path / "broken"
    broken.mkdir()
    (broken / "pyproject.toml.j2").write_text("{{unclosed")
    monkeypatch.setattr(sys, "argv", ["workbench", "validate", "broken"])
    # Patch TEMPLATE_DIR temporarily
    monkeypatch.setattr("workbench.scaffold.TEMPLATE_DIR", tmp_path)
    monkeypatch.setattr("workbench.cli.get_templates", lambda _custom_dir=None: ["broken"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "invalid" in captured.out.lower() or "error" in captured.out.lower()
