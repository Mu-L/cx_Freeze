"""Tests for some cx_Freeze.hooks."""

from __future__ import annotations

import pytest

pytest.importorskip("numpy", reason="Depends on extra package: numpy")


@pytest.mark.parametrize(
    "zip_packages", [False, True], ids=["", "zip-include-packages"]
)
def test_pandas(tmp_package, zip_packages: bool) -> None:
    """Test that the pandas/numpy is working correctly."""
    pytest.importorskip("pandas", reason="Depends on extra package: pandas")

    command = "python setup.py build_exe -O2"
    if zip_packages:
        command += " --zip-include-packages=* --zip-exclude-packages="

    tmp_package.create_from_sample("pandas")
    output = tmp_package.run("python setup.py build_exe -O2")
    executable = tmp_package.executable("test_pandas")
    assert executable.is_file()

    output = tmp_package.run(executable, timeout=10)
    lines = output.splitlines()
    assert lines[0].startswith("numpy version")
    assert lines[1].startswith("pandas version")
    assert len(lines) == 8, lines[2:]
