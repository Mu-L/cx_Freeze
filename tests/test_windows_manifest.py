"""Tests for some cx_Freeze.hooks."""

from __future__ import annotations

import ctypes
import os
import sys

import pytest

from cx_Freeze.dep_parser import PEParser

if sys.platform != "win32":
    pytest.skip(reason="Windows tests", allow_module_level=True)

SOURCE = """
test_manifest.py
    import sys

    winver = sys.getwindowsversion()
    print(f"Windows version: {winver.major}.{winver.minor}")
pyproject.toml
    [project]
    name = "test_manifest"
    version = "0.1.2.3"
    description = "Sample for test with cx_Freeze"

    [[tool.cxfreeze.executables]]
    script = "test_manifest.py"

    [[tool.cxfreeze.executables]]
    script = "test_manifest.py"
    manifest = "simple.manifest"
    target_name = "test_simple_manifest"

    [[tool.cxfreeze.executables]]
    script = "test_manifest.py"
    uac_admin = true
    target_name = "test_uac_admin"

    [[tool.cxfreeze.executables]]
    script = "test_manifest.py"
    uac_admin = true
    uac_uiaccess = true
    target_name = "test_uac_uiaccess"

    [tool.cxfreeze.build_exe]
    excludes = ["tkinter", "unittest"]
    silent = true
simple.manifest
    <?xml version='1.0' encoding='UTF-8' standalone='yes'?>
    <assembly xmlns='urn:schemas-microsoft-com:asm.v1' manifestVersion='1.0'>
      <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
        <security>
          <requestedPrivileges>
            <requestedExecutionLevel level='asInvoker' uiAccess='false' />
          </requestedPrivileges>
        </security>
      </trustInfo>
    </assembly>
"""


@pytest.fixture
def tmp_manifest(tmp_package):  # noqa: ANN201
    """Temporary path to build test manifest."""
    tmp_package.create(SOURCE)
    tmp_package.run()
    return tmp_package


def test_manifest(tmp_manifest) -> None:
    """With the correct manifest, windows version return 10.0 in Windows 10."""
    executable = tmp_manifest.executable("test_manifest")
    assert executable.is_file()
    output = tmp_manifest.run(executable, timeout=10)
    winver = sys.getwindowsversion()
    expected = f"Windows version: {winver.major}.{winver.minor}"
    assert output.splitlines()[0].strip() == expected


def test_simple_manifest(tmp_manifest) -> None:
    """With simple manifest, without "supportedOS Id", windows version returned
    is the compatible version for Windows 8.1, ie, 6.2.
    """
    if os.environ.get("CX_FREEZE_BIND", "") == "imagehlp":
        pytest.skip(reason="Use of lief is disabled")
    pytest.importorskip("lief", reason="Depends on extra package: lief")

    executable = tmp_manifest.executable("test_simple_manifest")
    assert executable.is_file()
    output = tmp_manifest.run(executable, timeout=10)
    expected = "Windows version: 6.2"
    assert output.splitlines()[0].strip() == expected

    parser = PEParser([], [])
    manifest = parser.read_manifest(executable)
    simple = tmp_manifest.path / "simple.manifest"
    assert manifest == simple.read_bytes().decode()


def test_uac_admin(tmp_manifest) -> None:
    """With the uac_admin, should return WinError 740 - requires elevation."""
    if os.environ.get("CX_FREEZE_BIND", "") == "imagehlp":
        pytest.skip(reason="Use of lief is disabled")
    pytest.importorskip("lief", reason="Depends on extra package: lief")

    executable = tmp_manifest.executable("test_uac_admin")
    assert executable.is_file()
    if ctypes.windll.shell32.IsUserAnAdmin():
        pytest.xfail(reason="User is admin")
    with pytest.raises(OSError, match="[WinError 740]"):
        tmp_manifest.run(executable, timeout=10)


def test_uac_uiaccess(tmp_manifest) -> None:
    """With the uac_uiaccess, should return WinError 740."""
    if os.environ.get("CX_FREEZE_BIND", "") == "imagehlp":
        pytest.skip(reason="Use of lief is disabled")
    pytest.importorskip("lief", reason="Depends on extra package: lief")

    executable = tmp_manifest.executable("test_uac_uiaccess")
    assert executable.is_file()
    if ctypes.windll.shell32.IsUserAnAdmin():
        pytest.xfail(reason="User is admin")
    with pytest.raises(OSError, match="[WinError 740]"):
        tmp_manifest.run(executable, timeout=10)
