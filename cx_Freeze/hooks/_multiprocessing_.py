"""A collection of functions which are triggered automatically by finder when
multiprocessing package is included.
"""

from __future__ import annotations

import sys
from textwrap import dedent
from typing import TYPE_CHECKING

from cx_Freeze._compat import IS_MINGW, IS_WINDOWS
from cx_Freeze.hooks.global_names import MULTIPROCESSING_GLOBAL_NAMES
from cx_Freeze.module import ModuleHook

if TYPE_CHECKING:
    from cx_Freeze.finder import ModuleFinder
    from cx_Freeze.module import Module

__all__ = ["Hook"]

# Notes:
# - fork in Unix (including macOS) is native
# - spawn in Windows is native since 4.3.4, but was improved in v6.2
# - spawn and forkserver in Unix is implemented in v6.15.4 #1956
# - monkeypatch context to do automatic freeze_support in v7.1 #2382
# - monkeypatch context to fix bug introduced in Python 3.13.4 in v8.4 #3009


class Hook(ModuleHook):
    """The Module Hook class."""

    def multiprocessing(self, finder: ModuleFinder, module: Module) -> None:
        """The forkserver method calls utilspawnv_passfds in ensure_running to
        pass a command line to python. In cx_Freeze the running executable
        is called, then we need to catch this and use exec function.
        For the spawn method there are a similar process to resource_tracker.

        Note: Using multiprocessing.spawn.freeze_support directly because it
        works for all OS, not only Windows.
        """
        # Ignore names that should not be confused with modules to be imported
        module.global_names.update(MULTIPROCESSING_GLOBAL_NAMES)

        if module.file.suffix == ".pyc":  # source unavailable
            return
        if IS_MINGW or IS_WINDOWS:
            return
        source = rf"""
        # cx_Freeze patch start
        import re as _re
        import sys as _sys
        if len(_sys.argv) >= 2 and _sys.argv[-2] == "-c":
            cmd = _sys.argv[-1]
            if _re.search(r"^from {module.name}.* import main.*", cmd):
                exec(cmd)
                _sys.exit()
        # workaround: inject freeze_support call to avoid an infinite loop
        from {module.name}.spawn import is_forking as _spawn_is_forking
        if _spawn_is_forking(_sys.argv):
            main_module = _sys.modules["__main__"]
            main_spec = main_module.__spec__
            main_code = main_spec.loader.get_code(main_spec.name)
            _names = main_code.co_names
            del main_module, main_spec, main_code
            if "freeze_support" not in _names:
                import BUILD_CONSTANTS as _constants
                _ignore = getattr(
                    _constants, "ignore_freeze_support_message", 0
                )
                if not _ignore:
                    print(
        '''
            An attempt has been made to start a new process before the
            current process has finished its bootstrapping phase.

            This probably means that you are not using fork to start your
            child processes and you have forgotten to use the proper idiom
            in the main module:

                if __name__ == "__main__":
                    freeze_support()
                    ...

            To fix this issue (hide this message), refer to the documentation:
                \
        https://cx-freeze.readthedocs.io/en/stable/faq.html#multiprocessing-support
        ''', file=_sys.stderr)
                #import os, signal
                #os.kill(os.getppid(), signal.SIGHUP)
                #_sys.exit(os.EX_SOFTWARE)
                from {module.name}.spawn import freeze_support as _freeze_support
                _freeze_support()
        # cx_Freeze patch end
        """
        code_string = module.file.read_text(encoding="utf_8") + dedent(source)
        module.code = compile(
            code_string,
            module.file.as_posix(),
            "exec",
            dont_inherit=True,
            optimize=finder.optimize,
        )

    def multiprocessing_context(
        self, finder: ModuleFinder, module: Module
    ) -> None:
        """Monkeypath context to do automatic freeze_support on Linux and
        MacOS. Also, fix Python 3.13.4+ bug introduced by gh-80334 on Windows.
        """
        if module.file.suffix == ".pyc":  # source unavailable
            return
        if IS_MINGW or IS_WINDOWS:
            if sys.version_info[:3] >= (3, 13, 4):
                source = rf"""
                # cx_Freeze patch start
                def _freeze_support(self):
                    from {module.root.name}.spawn import freeze_support
                    freeze_support()
                BaseContext.freeze_support = _freeze_support
                # cx_Freeze patch end
                """
            else:
                return
        else:
            source = rf"""
            # cx_Freeze patch start
            def _freeze_support(self):
                from {module.root.name}.spawn import freeze_support
                freeze_support()
            BaseContext.freeze_support = _freeze_support

            BaseContext._get_base_context = BaseContext.get_context
            def _get_base_context(self, method=None):
                self.freeze_support()
                return self._get_base_context(method)
            BaseContext.get_context = _get_base_context

            DefaultContext._get_default_context = DefaultContext.get_context
            def _get_default_context(self, method=None):
                self.freeze_support()
                return self._get_default_context(method)
            DefaultContext.get_context = _get_default_context
            # cx_Freeze patch end
            """
        code_string = module.file.read_text(encoding="utf_8") + dedent(source)
        module.code = compile(
            code_string,
            module.file.as_posix(),
            "exec",
            dont_inherit=True,
            optimize=finder.optimize,
        )

    def multiprocessing_synchronize(
        self,
        finder: ModuleFinder,  # noqa: ARG002
        module: Module,
    ) -> None:
        """Ignore modules not found in current OS."""
        module.ignore_names.update(
            {f"_{module.root.name}.SemLock", f"_{module.root.name}.sem_unlink"}
        )
