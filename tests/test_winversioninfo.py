"""Test winversioninfo."""

from __future__ import annotations

from pathlib import Path

import pytest
from packaging.version import Version

from cx_Freeze._compat import EXE_SUFFIX, IS_MINGW, IS_WINDOWS
from cx_Freeze.winversioninfo import COMMENTS_MAX_LEN, VersionInfo, main_test

SOURCE_SIMPLE_TEST = """
test.py
    print("Hello from cx_Freeze")
setup.py
    from cx_Freeze import setup

    setup(
        name="hello",
        version="0.1.2.3",
        description="Sample cx_Freeze script",
        executables=["test.py"],
    )
"""


@pytest.mark.skipif(not (IS_MINGW or IS_WINDOWS), reason="Windows tests")
class TestVersionInfo:
    """Test VersionInfo class."""

    def test___init__(self) -> None:
        """Tests the default value for the VersionInfo class."""
        input_version = "9.9.9.9"
        default_version = VersionInfo(input_version)
        valid_version = Version(input_version)
        assert default_version.version == "9.9.9.9"
        assert default_version.valid_version == valid_version
        assert default_version.internal_name is None
        assert default_version.original_filename is None
        assert default_version.comments is None
        assert default_version.company is None
        assert default_version.description is None
        assert default_version.copyright is None
        assert default_version.trademarks is None
        assert default_version.product is None
        assert default_version.dll is None
        assert default_version.debug is None
        assert default_version.verbose is True

    def test___init__with_kwargs(self) -> None:
        """Tests keyword values for the VersionInfo class."""
        input_version = "9.9.9.9"
        input_internal_name = "Test Internal Name"
        input_original_filename = "TestTempFileName"
        input_comments = "TestComment"
        input_company = "TestCompany"
        input_description = "TestDescription"
        input_copyright = "TestCopyright"
        input_trademarks = "TestMark"
        input_product = object()
        input_dll = True
        input_debug = True
        input_verbose = False

        version_instance = VersionInfo(
            version=input_version,
            internal_name=input_internal_name,
            original_filename=input_original_filename,
            comments=input_comments,
            company=input_company,
            description=input_description,
            copyright=input_copyright,
            trademarks=input_trademarks,
            product=input_product,
            dll=input_dll,
            debug=input_debug,
            verbose=input_verbose,
        )

        assert version_instance.version == "9.9.9.9"
        assert version_instance.valid_version == Version(input_version)
        assert version_instance.internal_name == input_internal_name
        assert version_instance.original_filename == input_original_filename
        assert version_instance.comments == input_comments
        assert version_instance.company == input_company
        assert version_instance.description == input_description
        assert version_instance.copyright == input_copyright
        assert version_instance.trademarks == input_trademarks
        assert version_instance.product == input_product
        assert version_instance.dll is input_dll
        assert version_instance.debug is input_debug
        assert version_instance.verbose is input_verbose

    def test_big_comment(self) -> None:
        """Tests a big comment value for the VersionInfo class."""
        input_version = "9.9.9.9"
        input_comments = "TestComment" + "=" * COMMENTS_MAX_LEN
        version_instance = VersionInfo(input_version, comments=input_comments)
        assert version_instance.version == "9.9.9.9"
        assert version_instance.comments == input_comments[:COMMENTS_MAX_LEN]

    @pytest.mark.parametrize(
        ("input_version", "version"),
        [
            ("9", "9.0.0.0"),
            ("0.1", "0.1.0.0"),
            ("1.0", "1.0.0.0"),
            ("1.0.1", "1.0.1.0"),
            ("1.2.3.4", "1.2.3.4"),
            ("6.0alpha", "6.0.0.0"),
            ("6.0.alpha", "6.0.0.0"),
            ("1.0.dev1", "1.0.0.0"),
            ("1.0.post1", "1.0.0.0"),
        ],
    )
    def test_windows_versions(self, input_version, version) -> None:
        """Tests that short versions get padded to the expected x4 digit
        windows versions.
        """
        default_version = VersionInfo(input_version)
        assert default_version.version == version
        assert default_version.version_info(Path(f"test{EXE_SUFFIX}"))

    def test_file_not_found(self) -> None:
        """Test for FileNotFoundError exception."""
        version = VersionInfo("0.1")
        with pytest.raises(FileNotFoundError):
            version.stamp(f"test{EXE_SUFFIX}")

    @pytest.mark.venv
    @pytest.mark.parametrize(
        "option",
        [
            "--dict",
            "--raw",
            pytest.param("--pywin32", marks=pytest.mark.xfail),
        ],
    )
    def test_main(self, tmp_package, option, capsys) -> None:
        """Test the cx_Freeze.winversioninfo __main_ entry point."""
        tmp_package.create(SOURCE_SIMPLE_TEST)
        if option == "--pywin32":
            tmp_package.monkeypatch.setenv("CX_FREEZE_STAMP", "pywin32")
            tmp_package.install("pywin32")
        tmp_package.freeze()

        executable = tmp_package.executable("test")
        assert executable.is_file(), f"file not found: {executable}"

        result = tmp_package.run(executable, timeout=10)
        result.stdout.fnmatch_lines("Hello from cx_Freeze")

        main_test(args=["--version=0.2", option, f"{executable}"])
        captured = capsys.readouterr()
        assert captured.out.splitlines()[-1].startswith("Stamped:")

    def test_main_no_option(self) -> None:
        """Test argparse error exception."""
        with pytest.raises(SystemExit):
            main_test(args=[])

    @pytest.mark.venv
    def test_main_with_environ(self, tmp_package) -> None:
        """Test argparse error exception."""
        tmp_package.install("pywin32")
        tmp_package.monkeypatch.setenv("CX_FREEZE_STAMP", "pywin32")
        result = tmp_package.run("python -m cx_Freeze.winversioninfo")
        assert result.ret > 0
