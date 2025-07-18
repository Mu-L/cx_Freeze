"""Tests for hooks:
numpy, matplotlib, pandas, raterio, scipy, shapely, and vtk.
"""

from __future__ import annotations

import pytest

from cx_Freeze._compat import (
    IS_ARM_64,
    IS_CONDA,
    IS_WINDOWS,
)

TIMEOUT = 10
TIMEOUT_SLOW = 60 if IS_CONDA else 20
TIMEOUT_VERY_SLOW = 90 if IS_CONDA else 30

zip_packages = pytest.mark.parametrize(
    "zip_packages", [False, True], ids=["", "zip_packages"]
)


SOURCE_TEST_SCIPY = """
test_scipy.py
    import numpy as np
    import scipy
    from scipy.spatial.transform import Rotation

    print("Hello from cx_Freeze")
    print("numpy version", np.__version__)
    print("scipy version", scipy.__version__)
    print(Rotation.from_euler("XYZ", [10, 10, 10], degrees=True).as_matrix())
pyproject.toml
    [project]
    name = "test_scipy"
    version = "0.1.2.3"
    dependencies = [
        "numpy<1.26;python_version <= '3.10'",
        "numpy<2;python_version == '3.11'",
        "numpy>=2;python_version >= '3.12'",
        "scipy<1.9.2;python_version == '3.9'",
        "scipy<1.16;python_version == '3.10'",
        "scipy>=1.16;python_version >= '3.11'",
    ]

    [tool.cxfreeze]
    executables = ["test_scipy.py"]

    [tool.cxfreeze.build_exe]
    excludes = ["tkinter", "PySide6", "shiboken6"]
    include_msvcr = true
    optimize = 2
    silent = true
"""


@pytest.mark.xfail(
    IS_WINDOWS and IS_ARM_64,
    raises=ModuleNotFoundError,
    reason="scipy does not support Windows arm64",
    strict=True,
)
@pytest.mark.venv
@zip_packages
def test_scipy(tmp_package, zip_packages: bool) -> None:
    """Test that the scipy/numpy is working correctly."""
    tmp_package.create(SOURCE_TEST_SCIPY)
    if zip_packages:
        pyproject = tmp_package.path / "pyproject.toml"
        buf = pyproject.read_bytes().decode().splitlines()
        buf += ['zip_include_packages = "*"', 'zip_exclude_packages = ""']
        pyproject.write_bytes("\n".join(buf).encode("utf_8"))
    tmp_package.freeze()

    executable = tmp_package.executable("test_scipy")
    assert executable.is_file()
    result = tmp_package.run(executable, timeout=TIMEOUT_SLOW)
    result.stdout.fnmatch_lines(
        [
            "Hello from cx_Freeze",
            "numpy version *",
            "scipy version *",
            "[[*",
            " [*",
            " [*",
        ]
    )


SOURCE_TEST_SCIKIT_LEARN = """
test_sklearn.py
    import sklearn

    print("Hello from cx_Freeze")
    print("sklearn version", sklearn.__version__)
pyproject.toml
    [project]
    name = "test_sklearn"
    version = "0.1.2.3"
    dependencies = [
        "numpy<1.26;python_version <= '3.10'",
        "scikit-learn<1.3;python_version <= '3.10'",
        "scikit-learn<1.5;python_version == '3.11'",
        "scikit-learn>=1.7;python_version >= '3.12'",
    ]

    [tool.cxfreeze]
    executables = ["test_sklearn.py"]

    [tool.cxfreeze.build_exe]
    excludes = ["tkinter", "PySide6", "shiboken6"]
    include_msvcr = true
    silent = true
"""


@pytest.mark.xfail(
    IS_WINDOWS and IS_ARM_64,
    raises=ModuleNotFoundError,
    reason="scikit-learn does not support Windows arm64",
    strict=True,
)
@pytest.mark.venv
@zip_packages
def test_sklearn(tmp_package, zip_packages: bool) -> None:
    """Test that the scikit-learn is working correctly."""
    tmp_package.create(SOURCE_TEST_SCIKIT_LEARN)
    if zip_packages:
        pyproject = tmp_package.path / "pyproject.toml"
        buf = pyproject.read_bytes().decode().splitlines()
        buf += ['zip_include_packages = "*"', 'zip_exclude_packages = ""']
        pyproject.write_bytes("\n".join(buf).encode("utf_8"))
    tmp_package.freeze()

    executable = tmp_package.executable("test_sklearn")
    assert executable.is_file()
    result = tmp_package.run(executable, timeout=TIMEOUT_SLOW)
    result.stdout.fnmatch_lines(["Hello from cx_Freeze", "sklearn version *"])
