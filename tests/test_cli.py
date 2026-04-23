def test_version_flag():
    import sys
    from io import StringIO
    import pytest
    from workbench.cli import main

    old_argv = sys.argv
    old_stdout = sys.stdout
    try:
        sys.argv = ["workbench", "--version"]
        sys.stdout = StringIO()
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
        assert "0.1.0" in sys.stdout.getvalue()
    finally:
        sys.argv = old_argv
        sys.stdout = old_stdout
