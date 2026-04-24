import json
import sys
from workbench.cli import main
import pytest


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


def test_init_dry_run_short_flag(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["workbench", "init", "python", "short-dry", "-n"])
    monkeypatch.chdir(tmp_path)
    main()
    target = tmp_path / "short-dry"
    assert not target.exists()
    captured = capsys.readouterr()
    assert "Would create" in captured.out


def test_list_json_output(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "list", "--json"])
    main()
    captured = capsys.readouterr()
    out = json.loads(captured.out)
    assert isinstance(out, list)
    assert "python" in out


def test_list_plain_output(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "list", "--plain"])
    main()
    captured = capsys.readouterr()
    lines = [line for line in captured.out.splitlines() if line]
    assert "python" in lines
    assert "cli" in lines


def test_info_json_output(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "info", "python", "--json"])
    main()
    captured = capsys.readouterr()
    out = json.loads(captured.out)
    assert out["name"] == "python"
    assert isinstance(out["files"], list)


def test_info_plain_output(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "info", "python", "--plain"])
    main()
    captured = capsys.readouterr()
    lines = captured.out.splitlines()
    assert lines[0] == "python"
    assert "pyproject.toml.j2" in lines


def test_bare_init_shows_concise_help(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "init"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "workbench init" in captured.out
    assert "Example:" in captured.out


def test_bare_info_shows_concise_help(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "info"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "workbench info" in captured.out


def test_bare_validate_shows_concise_help(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "validate"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "workbench validate" in captured.out


def test_validate_json_output(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "validate", "python", "--json"])
    main()
    captured = capsys.readouterr()
    out = json.loads(captured.out)
    assert out["valid"] is True
    assert out["errors"] == []


def test_no_color_flag_disables_color(capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(sys, "argv", ["workbench", "--no-color", "init", "python", "no-color-proj"])
    monkeypatch.chdir(tmp_path)
    main()
    captured = capsys.readouterr()
    # ANSI codes should not appear
    assert "\033[1m" not in captured.out


def test_error_suggests_dry_run_and_force(capsys, monkeypatch, tmp_path):
    (tmp_path / "exists-proj").mkdir()
    (tmp_path / "exists-proj" / "file.txt").write_text("x")
    monkeypatch.setattr(sys, "argv", ["workbench", "init", "python", "exists-proj"])
    monkeypatch.chdir(tmp_path)
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "--dry-run" in captured.err or "-n" in captured.err
    assert "--force" in captured.err


def test_init_uses_config_author_and_license(capsys, monkeypatch, tmp_path):
    from workbench import config as config_module
    monkeypatch.setattr(config_module, "_get_config_dir", lambda: tmp_path / "workbench")
    config_module.save_config({"author": "8bit64k", "email": "8bit64k@example.com", "license": "Apache-2.0"})
    monkeypatch.setattr(sys, "argv", ["workbench", "init", "python", "config-proj"])
    monkeypatch.chdir(tmp_path)
    main()
    target = tmp_path / "config-proj"
    assert target.exists()
    pyproject = (target / "pyproject.toml").read_text()
    assert 'name = "8bit64k"' in pyproject
    assert 'email = "8bit64k@example.com"' in pyproject
    assert 'text = "Apache-2.0"' in pyproject
    assert "License :: OSI Approved :: Apache-2.0 License" in pyproject


def test_init_uses_config_template_dir(capsys, monkeypatch, tmp_path):
    from workbench import config as config_module
    monkeypatch.setattr(config_module, "_get_config_dir", lambda: tmp_path / "workbench")
    custom_dir = tmp_path / "custom_templates"
    custom_dir.mkdir()
    tpl = custom_dir / "custom"
    tpl.mkdir()
    (tpl / "pyproject.toml.j2").write_text("[project]\nname = \"{{project_name}}\"\n")
    config_module.save_config({"default_template_dir": str(custom_dir)})
    monkeypatch.setattr(sys, "argv", ["workbench", "init", "custom", "cfg-tpl-proj"])
    monkeypatch.chdir(tmp_path)
    main()
    target = tmp_path / "cfg-tpl-proj"
    assert target.exists()
    assert (target / "pyproject.toml").exists()


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


def test_config_set_and_get(capsys, monkeypatch, tmp_path):
    from workbench import config as config_module
    monkeypatch.setattr(config_module, "_get_config_dir", lambda: tmp_path / "workbench")
    monkeypatch.setattr(sys, "argv", ["workbench", "config", "set", "author", "8bit64k"])
    main()
    captured = capsys.readouterr()
    assert "Set author = 8bit64k" in captured.out
    monkeypatch.setattr(sys, "argv", ["workbench", "config", "get", "author"])
    main()
    captured = capsys.readouterr()
    assert captured.out.strip() == "8bit64k"


def test_config_list(capsys, monkeypatch, tmp_path):
    from workbench import config as config_module
    monkeypatch.setattr(config_module, "_get_config_dir", lambda: tmp_path / "workbench")
    config_module.save_config({"author": "Test", "license": "Apache-2.0"})
    monkeypatch.setattr(sys, "argv", ["workbench", "config", "list"])
    main()
    captured = capsys.readouterr()
    assert "author = Test" in captured.out
    assert "license = Apache-2.0" in captured.out


def test_config_unset(capsys, monkeypatch, tmp_path):
    from workbench import config as config_module
    monkeypatch.setattr(config_module, "_get_config_dir", lambda: tmp_path / "workbench")
    config_module.save_config({"email": "test@example.com"})
    monkeypatch.setattr(sys, "argv", ["workbench", "config", "unset", "email"])
    main()
    captured = capsys.readouterr()
    assert "Unset email" in captured.out
    monkeypatch.setattr(sys, "argv", ["workbench", "config", "get", "email"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1


def test_bare_config_shows_concise_help(capsys, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["workbench", "config"])
    with pytest.raises(SystemExit) as exc:
        main()
    assert exc.value.code == 1
    captured = capsys.readouterr()
    assert "workbench config" in captured.out
    assert "set" in captured.out.lower()
