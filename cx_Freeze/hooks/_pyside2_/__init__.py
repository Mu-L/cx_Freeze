"""A collection of functions which are triggered automatically by finder when
PySide2 package is included.
"""

from __future__ import annotations

import importlib.resources as importlib_resources
from textwrap import dedent
from typing import TYPE_CHECKING

from cx_Freeze._compat import IS_MACOS, IS_MINGW
from cx_Freeze.hooks.qthooks import copy_qt_files
from cx_Freeze.hooks.qthooks import load_qt_qtcore as load_pyside2_qtcore
from cx_Freeze.hooks.qthooks import (
    load_qt_qtdesigner as load_pyside2_qtdesigner,
)
from cx_Freeze.hooks.qthooks import load_qt_qtgui as load_pyside2_qtgui
from cx_Freeze.hooks.qthooks import (
    load_qt_qtmultimedia as load_pyside2_qtmultimedia,
)
from cx_Freeze.hooks.qthooks import load_qt_qtnetwork as load_pyside2_qtnetwork
from cx_Freeze.hooks.qthooks import (
    load_qt_qtpositioning as load_pyside2_qtpositioning,
)
from cx_Freeze.hooks.qthooks import (
    load_qt_qtprintsupport as load_pyside2_qtprintsupport,
)
from cx_Freeze.hooks.qthooks import load_qt_qtqml as load_pyside2_qtqml
from cx_Freeze.hooks.qthooks import load_qt_qtscript as load_pyside2_qtscript
from cx_Freeze.hooks.qthooks import load_qt_qtsql as load_pyside2_qtsql
from cx_Freeze.hooks.qthooks import (
    load_qt_qtwebenginecore as _load_qt_qtwebenginecore,
)
from cx_Freeze.hooks.qthooks import (
    load_qt_qtwebenginewidgets as load_pyside2_qtwebenginewidgets,
)
from cx_Freeze.hooks.qthooks import load_qt_qtwidgets as load_pyside2_qtwidgets
from cx_Freeze.hooks.qthooks import load_qt_uic as load_pyside2_uic

if TYPE_CHECKING:
    from cx_Freeze.finder import ModuleFinder
    from cx_Freeze.module import Module


def load_pyside2(finder: ModuleFinder, module: Module) -> None:
    """Inject code in PySide2 __init__ to locate and load plugins and
    resources. Also, this fixes issues with conda-forge versions.
    """
    distribution = module.distribution
    environment = (distribution and distribution.installer) or "pip"
    # Activate the optimized mode by default in pip environments
    if environment == "pip":
        if module.name in finder.zip_exclude_packages:
            print(f"WARNING: zip_exclude_packages={module.name} ignored.")
        if module.name in finder.zip_include_packages:
            print(f"WARNING: zip_include_packages={module.name} ignored.")
        module.in_file_system = 2

    # Include a module that inject an optional debug code
    qt_debug = importlib_resources.files(__package__) / "_debug.py"
    finder.include_file_as_module(qt_debug, "PySide2._cx_freeze_debug")

    # Include a resource with qt.conf (Prefix = lib/PySide2) for conda-forge
    if environment == "conda":
        resource = importlib_resources.files(__package__) / "_resource.py"
        finder.include_file_as_module(resource, "PySide2._cx_freeze_resource")

    # Include a qt.conf in the module path (Prefix = lib/PySide2) for msys2
    if IS_MINGW:
        qt_conf = importlib_resources.files(__package__) / "qt.conf"
        finder.include_files(qt_conf, qt_conf.name)

    # Include an optional qt.conf to be used by QtWebEngine (Prefix = ..)
    copy_qt_files(finder, "PySide2", "LibraryExecutablesPath", "qt.conf")

    # Inject code to init
    code_string = module.file.read_text(encoding="utf_8")
    code_string += dedent(
        f"""
        # cx_Freeze patch start
        import os, sys
        if {environment == "conda"}:  # conda-forge linux, macos and windows
            import PySide2._cx_freeze_resource
        elif {IS_MACOS}:  # macos using 'pip install pyside2'
            # Support for QtWebEngine (bdist_mac differs from build_exe)
            helpers = os.path.join(os.path.dirname(sys.prefix), "Helpers")
            if not os.path.isdir(helpers):
                helpers = os.path.join(sys.prefix, "share")
            os.environ["QTWEBENGINEPROCESS_PATH"] = os.path.join(
                helpers,
                "QtWebEngineProcess.app/Contents/MacOS/QtWebEngineProcess"
            )
            os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--single-process"
        else:
            # Support for QtWebEngine (linux and windows using pip)
            os.environ["QTWEBENGINE_DISABLE_SANDBOX"] = "1"
        import PySide2._cx_freeze_debug
        # cx_Freeze patch end
        """
    )
    module.code = compile(
        code_string,
        module.file.as_posix(),
        "exec",
        dont_inherit=True,
        optimize=finder.optimize,
    )

    # small tweaks for shiboken2
    if module.in_file_system == 2:
        shiboken2 = finder.include_package("shiboken2")
        shiboken2.in_file_system = 2
    finder.include_module("inspect")


def load_pyside2_qtwebenginecore(finder: ModuleFinder, module: Module) -> None:
    """Include module dependency and QtWebEngineProcess files."""
    _load_qt_qtwebenginecore(finder, module)
    distribution = module.parent.distribution
    environment = (distribution and distribution.installer) or "pip"
    if IS_MACOS and environment == "pip":
        # duplicate resource files
        for source, target in finder.included_files[:]:
            if any(
                filter(source.match, ("Resources/*.pak", "Resources/*.dat"))
            ):
                finder.include_files(
                    source,
                    target.parent.parent / target.name,
                    copy_dependent_files=False,
                )


__all__ = [
    "load_pyside2",
    "load_pyside2_qtcore",
    "load_pyside2_qtdesigner",
    "load_pyside2_qtgui",
    "load_pyside2_qtmultimedia",
    "load_pyside2_qtnetwork",
    "load_pyside2_qtpositioning",
    "load_pyside2_qtprintsupport",
    "load_pyside2_qtqml",
    "load_pyside2_qtscript",
    "load_pyside2_qtsql",
    "load_pyside2_qtwebenginecore",
    "load_pyside2_qtwebenginewidgets",
    "load_pyside2_qtwidgets",
    "load_pyside2_uic",
]
