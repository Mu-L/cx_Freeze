"""Tests for hooks of anyio async package
(implicitly test the asyncio and uvloop packages).
"""

from __future__ import annotations

import sys

import pytest

from cx_Freeze._compat import ABI_THREAD

TIMEOUT = 10

zip_packages = pytest.mark.parametrize(
    "zip_packages", [False, True], ids=["", "zip_packages"]
)

SOURCE_ANYIO = """
test_anyio.py
    import sys
    import sysconfig

    from anyio import run

    ABI_THREAD = sysconfig.get_config_var("abi_thread") or ""

    async def main():
        print("Hello from cx_Freeze")

    run(
        main,
        backend_options={
            "use_uvloop": sys.platform != "win32" and ABI_THREAD == ""
        },
    )
pyproject.toml
    [project]
    name = "test_anyio"
    version = "0.1.2.3"
    dependencies = ["anyio"]

    [tool.cxfreeze]
    executables = ["test_anyio.py"]

    [tool.cxfreeze.build_exe]
    excludes = ["tkinter", "unittest"]
    silent = true
"""


@pytest.mark.venv
@zip_packages
def test_anyio(tmp_package, zip_packages) -> None:
    """Test if anyio is working correctly."""
    tmp_package.create(SOURCE_ANYIO)
    if zip_packages:
        pyproject = tmp_package.path / "pyproject.toml"
        buf = pyproject.read_bytes().decode().splitlines()
        buf += ['zip_include_packages = "*"', 'zip_exclude_packages = ""']
        pyproject.write_bytes("\n".join(buf).encode("utf_8"))
    if sys.platform != "win32" and ABI_THREAD == "":
        tmp_package.install("uvloop")
    tmp_package.freeze()
    executable = tmp_package.executable("test_anyio")
    assert executable.is_file()
    result = tmp_package.run(executable, timeout=TIMEOUT)
    result.stdout.fnmatch_lines(["Hello from cx_Freeze"])
