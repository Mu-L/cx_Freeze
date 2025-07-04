"""cxfreeze-quickstart command line tool."""

from __future__ import annotations

import os
import subprocess
import sys
from typing import ClassVar


class SetupWriter:
    """SetupWriter class."""

    bases: ClassVar[dict[str, str]] = {
        "C": "console",
        "G": "gui",
        "S": "service",
    }

    @property
    def base(self) -> str:
        return self.bases[self.base_code]

    @property
    def default_executable_name(self) -> str:
        return os.path.splitext(self.script)[0]

    def __init__(self) -> None:
        self.name = self.description = self.script = ""
        self.executable_name = self.default_executable_name
        self.setup_file_name = "setup.py"
        self.version = "1.0"
        self.base_code = "C"

    def get_boolean_value(self, label, default=False) -> bool:
        default_response = "y" if default else "n"
        while True:
            response = self.get_value(
                label, default_response, separator="? "
            ).lower()
            if response in ("y", "n", "yes", "no"):
                break
        return response in ("y", "yes")

    def get_value(self, label, default="", separator=": ") -> str:
        if default:
            label += f" [{default}]"
        return input(label + separator).strip() or default

    def populate_from_command_line(self) -> None:
        self.name = self.get_value("Project name", self.name)
        self.version = self.get_value("Version", self.version)
        self.description = self.get_value("Description", self.description)
        self.script = self.get_value(
            "Python file to make executable from", self.script
        )
        self.executable_name = self.get_value(
            "Executable file name", self.default_executable_name
        )
        bases_prompt = (
            "(C) console application, (G) GUI application, or (S) service"
        )
        while True:
            self.base_code = self.get_value(bases_prompt, "C")
            if self.base_code in self.bases:
                break
        while True:
            self.setup_file_name = self.get_value(
                "Save setup script to", self.setup_file_name
            )
            if not os.path.exists(self.setup_file_name):
                break
            if self.get_boolean_value(f"Overwrite {self.setup_file_name}"):
                break

    def write(self) -> None:
        with open(self.setup_file_name, "w", encoding="utf_8") as output:

            def w(s) -> int:
                return output.write(s + "\n")

            w("from cx_Freeze import setup, Executable")
            w("")

            w("# Dependencies are automatically detected, but it might need")
            w("# fine tuning.")
            w("build_options = {'packages': [], 'excludes': []}")
            w("")

            if self.base.startswith("Win32"):
                w("import sys")
                w(f"base = {self.base!r} if sys.platform=='win32' else None")
            else:
                w(f"base = {self.base!r}")
            w("")

            w("executables = [")
            if self.executable_name != self.default_executable_name:
                w(
                    f"    Executable({self.script!r}, base=base, "
                    f"target_name = {self.executable_name!r})"
                )
            else:
                w(f"    Executable({self.script!r}, base=base)")
            w("]")
            w("")

            w(
                f"setup(name={self.name!r},\n"
                f"      version = {self.version!r},\n"
                f"      description = {self.description!r},\n"
                "      options = {'build_exe': build_options},\n"
                "      executables = executables)"
            )


def main() -> None:
    """Entry point for cxfreeze-quickstart command line tool."""
    writer = SetupWriter()
    writer.populate_from_command_line()
    writer.write()
    print("")
    print(f"Setup script written to {writer.setup_file_name}; run it as:")
    print(f"    python {writer.setup_file_name} build")
    if writer.get_boolean_value("Run this now"):
        subprocess.call([sys.executable, writer.setup_file_name, "build"])
