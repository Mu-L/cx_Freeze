"""Helper module to build tests on Linux, Windows and macOS.

Also works with variants like conda-forge and MSYS2 (Windows).
"""
from __future__ import annotations

# ruff: noqa: D103
import argparse
import contextlib
import json
import os
import re
import subprocess
import sys
import zipfile
from importlib import import_module
from pathlib import Path
from shutil import which
from sysconfig import (
    get_config_var,
    get_path,
    get_platform,
    get_python_version,
)
from urllib.request import urlcleanup, urlretrieve


class Requirement:
    """fake."""

    def __init__(self, requirement_string: str) -> None:
        self.name = requirement_string

    def __str__(self) -> str:
        return self.name


def import_module_or_none(module_name):
    try:
        return import_module(module_name)
    except ImportError:
        return None


def reload_setuptools():
    # pylint: disable-next=global-statement
    global Requirement  # noqa: PLW0603
    packaging = import_module_or_none("setuptools.extern.packaging")
    if packaging:
        __import__("setuptools.extern.packaging.requirements")
        Requirement = packaging.requirements.Requirement


CI = bool(os.environ.get("CI", "") == "true")
CI_DIR = Path(sys.argv[0]).parent.resolve()
TOP_DIR = CI_DIR.parent
PLATFORM = get_platform()
IS_LINUX = PLATFORM.startswith("linux")
IS_MACOS = PLATFORM.startswith("macos")
IS_MINGW = PLATFORM.startswith("mingw")
IS_WINDOWS = PLATFORM.startswith("win")
IS_FINAL_VERSION = sys.version_info.releaselevel == "final"
IS_MANYLINUX = os.environ.get("AUDITWHEEL_PLAT", "").startswith("manylinux")

RE_PYTHON_VERSION = re.compile(r"\s*\"*\'*(\d+)\.*(\d*)\.*(\d*)\"*\'*")
RE_CONDA_BUILD_PYVER = re.compile(r"(py)(\d*)\s*")

IS_CONDA = Path(sys.prefix, "conda-meta").is_dir()
CONDA_EXE = os.environ.get("CONDA_EXE", "conda")
MINGW_PACKAGE_PREFIX = os.environ.get("MINGW_PACKAGE_PREFIX", "")
PIP_UPGRADE = os.environ.get("PIP_UPGRADE", False)
PIPENV_ACTIVE = bool(os.environ.get("PIPENV_ACTIVE", 0))


def is_supported_platform(
    platform: str | list[str] | None, platform_in_use: str | None = None
) -> bool:
    if isinstance(platform, str):
        platform = platform.split(",")
    if not platform:  # if not specified, all platforms are supported
        return True
    if platform_in_use is None:
        if IS_MACOS:
            platform_in_use = "macos"
        elif IS_MINGW:
            platform_in_use = "mingw"
        elif IS_WINDOWS:
            platform_in_use = "windows"
        else:
            platform_in_use = "linux"
    platform_support = {"linux", "macos", "mingw", "windows"}
    platform_yes = {plat for plat in platform if not plat.startswith("!")}
    if platform_yes:
        platform_support = platform_yes
    platform_not = {plat[1:] for plat in platform if plat.startswith("!")}
    if platform_not:
        platform_support -= platform_not
    return platform_in_use in platform_support


def is_supported_python(python_version: str) -> bool:
    python_version_in_use = sys.version_info[:3]
    numbers = RE_PYTHON_VERSION.split(python_version)
    operator = numbers[0]
    python_version_required = tuple(int(num) for num in numbers[1:] if num)
    evaluate = f"{python_version_in_use}{operator}{python_version_required}"
    return eval(evaluate)  # pylint: disable=eval-used # noqa: PGH001


def install_requirements(
    requires: str | list[str] | set[str],
    extra_index_url: list[str] | None = None,
    find_links: list[str] | None = None,
) -> list[str]:
    if isinstance(requires, str):
        requires = requires.split(",")
    if isinstance(requires, list):
        requires = set(requires)

    pip_install = [sys.executable, "-m", "pip", "install"]
    pipenv_install = ["pipenv", "install"]
    pacman_args = ["pacman", "--noconfirm", "--needed", "-S"]
    pacman_search = ["pacman", "--noconfirm", "-Ss"]
    conda_install = [CONDA_EXE, "install", "--prefix", sys.prefix, "-y", "-q"]
    conda_install += ["--no-channel-priority", "-S"]
    conda_search = [CONDA_EXE, "search", "--override-channels"]

    installed_packages = []
    conda_pkgs = []
    pip_pkgs = []
    for req in requires:
        installed = False
        alias_for_conda = None
        alias_for_mingw = None
        no_deps = False
        platform = None
        python_version = None
        only_binary = False
        pre_release = False
        prefer_binary = False
        require: Requirement | None = None
        upgrade = PIP_UPGRADE
        for req_data in req.split(" "):
            if req_data.startswith("--conda="):
                # alias_for_conda accepts version
                alias_for_conda = req_data.split("=", 1)[1]
            elif req_data.startswith("--mingw="):
                # alias_for_mingw discards version
                alias_for_mingw = req_data.split("=", 1)[1]
            elif req_data == "--no-deps":
                no_deps = True
            elif req_data.startswith("--platform="):
                platform = req_data.split("=")[1]
            elif req_data.startswith("--python-version"):
                python_version = req_data[len("--python-version") :]
            elif req_data == "--only-binary":
                only_binary = True
            elif req_data == "--pre":
                pre_release = True
            elif req_data == "--prefer-binary":
                prefer_binary = True
            elif req_data == "--upgrade":
                upgrade = True
            elif req_data:
                require = Requirement(req_data)
        if not is_supported_platform(platform):
            continue
        if python_version and not is_supported_python(python_version):
            continue
        if IS_CONDA:
            # minimal support for conda
            # NOTE: do not implement: no-deps, find-links
            if alias_for_conda is not None:
                if alias_for_conda == "":
                    continue
                require = Requirement(alias_for_conda)
            elif require is None:
                continue
            args = []
            if extra_index_url:
                for extra in extra_index_url:
                    packages_url = extra[:-1] if extra[-1] == "/" else extra
                    args2 = [
                        "-c",
                        f"{packages_url}/conda",
                        require.name,
                        "--json",
                    ]
                    process = subprocess.run(
                        conda_search + args2,
                        check=False,
                        stdout=subprocess.PIPE,
                    )
                    if process.returncode == 0:
                        output = json.loads(process.stdout)
                        pyver = get_config_var("py_version_nodot")
                        for file in output[require.name]:
                            build = file["build"]
                            match = RE_CONDA_BUILD_PYVER.search(build)
                            if match and match.group(2) == pyver:
                                args = [file["url"]]
                                break
            if args:
                process = subprocess.run(conda_install + args, check=False)
                if process.returncode == 0:
                    installed_packages.extend(args)
                    installed = True
                continue
            conda_pkgs.append(str(require))
            continue
        if IS_MINGW:
            # create a list of possible names of the package, because in
            # MSYS2 some packages are mapped to python-package or
            # lowercased, etc, for instance:
            # Cython is not mapped
            # cx_Logging is python-cx-logging
            # Pillow is python-Pillow
            # and so on.
            # TODO: emulate find_links support
            # TODO: emulate no_deps support only for python packages
            if alias_for_mingw is not None:
                if alias_for_mingw == "":
                    continue
                require = Requirement(alias_for_mingw)
            elif require is None:
                continue
            package = require.name
            packages = [f"python-{package}", package]
            if not package.islower():
                for package_name in packages[:]:
                    packages.append(package_name.lower())
            if "_" in package:
                for package_name in packages[:]:
                    packages.append(package_name.replace("_", "-"))
            elif "-" in package:
                for package_name in packages[:]:
                    packages.append(package_name.replace("-", "_"))
            for package_name in packages:
                package = f"{MINGW_PACKAGE_PREFIX}-{package_name}"
                args = [*pacman_search, package]
                process = subprocess.run(
                    args, stdout=subprocess.PIPE, encoding="utf_8", check=False
                )
                if process.returncode == 1:
                    continue  # does not exist with this name
                if process.returncode == 0 and "installed" in process.stdout:
                    installed_packages.append(package)
                    installed = True
                    break
                process = subprocess.run([*pacman_args, package], check=False)
                if process.returncode == 0:
                    installed_packages.append(package)
                    installed = True
                    break
            if installed:
                continue
        # use pip
        if require is None:
            continue
        args = []
        if no_deps and not PIPENV_ACTIVE:
            args.append("--no-deps")
        if only_binary and not PIPENV_ACTIVE:
            if 0:  # pylint: disable=using-constant-test
                # if IS_LINUX:
                # prefer manylinux2014 wheels
                platform = get_platform()
                for mod in ["_2_17_", "2014_", "_2_5_", "1_", "_2_28_"]:
                    linux2014 = platform.replace("-", mod)
                    args.append(f"--platform=many{linux2014}")
                args.append(f"--python-version={get_python_version()}")
                args.append("--only-binary=:all:")
                target = get_path("platlib")
                args.append(f"--target={target}")
                # FIXME: without '--upgrade' causes a bug with pyqt5.
                # FIXME: '--upgrade' causes a bug with pyqt6.
                # args.append("--upgrade")
                # args.append("--upgrade-strategy=eager")
            else:
                args.append(f"--only-binary={require.name}")
        if pre_release:
            args.append("--pre")
        if prefer_binary and not PIPENV_ACTIVE:
            args.append("--prefer-binary")
        if upgrade:
            args.append("--upgrade")
        if args:
            if PIPENV_ACTIVE:
                if extra_index_url:
                    args += [f"--index={extra_index_url[0]}"]
                args = pipenv_install[:] + args + [str(require)]
            else:
                if extra_index_url:
                    args += [
                        f"--extra-index-url={url}" for url in extra_index_url
                    ]
                if find_links:
                    args += [f"--find-links={link}" for link in find_links]
                args = pip_install + args + [str(require)]
            print("args", args)
            process = subprocess.run(args, check=False)
            if process.returncode == 0:
                installed_packages.append(require.name)
                installed = True
            elif not IS_FINAL_VERSION and not pre_release:
                # in python preview, try a pre-release of the package too
                args.append("--pre")
                process = subprocess.run(args, check=False)
                if process.returncode == 0:
                    installed_packages.append(require.name)
                    installed = True
        else:
            pip_pkgs.append(str(require))
    if pip_pkgs:
        if extra_index_url:
            args = [f"--extra-index-url={extra}" for extra in extra_index_url]
        else:
            args = []
        if find_links:
            args = [f"--find-links={link}" for link in find_links] + args
        if PIPENV_ACTIVE:
            # ignore extra args
            args = pipenv_install[:] + pip_pkgs
        else:
            args = pip_install[:] + args + pip_pkgs
        print("args", args)
        process = subprocess.run(args, check=False)
        if process.returncode == 0:
            installed_packages.extend(pip_pkgs)
    if conda_pkgs:
        conda_forge = ["--override-channels", "-c", "conda-forge"]
        process = subprocess.run(
            conda_install + conda_forge + conda_pkgs, check=False
        )
        if process.returncode == 0:
            installed_packages.extend(conda_pkgs)
        # TODO: fallback to pip on error
    return installed_packages


def cx_freeze_status() -> tuple[str, bool]:
    # working in samples directory
    importlib_metadata = import_module("setuptools.extern.importlib_metadata")
    try:
        version = importlib_metadata.version("cx_Freeze")
        installed = True
    except importlib_metadata.PackageNotFoundError:
        cx_freeze = TOP_DIR / "cx_Freeze" / "__init__.py"
        version = ""
        for line in cx_freeze.read_text(encoding="utf_8").splitlines():
            if line.startswith("__version__"):
                version = line.split("=")[1].replace("-", ".")
                break
        version = version.strip().replace('"', "")
        installed = False
    return version, installed


def cibuildwheel_only() -> str:
    pyver = get_python_version().replace(".", "")
    platform = PLATFORM.replace("linux", "manylinux").replace("-", "_")
    return f"cp{pyver}-{platform}"


def cibuildwheel_file() -> Path | None:
    pyver = get_python_version().replace(".", "")
    platform = PLATFORM.replace("linux", "manylinux").replace("-", "*_")
    cx_freeze_version, _ = cx_freeze_status()
    pattern = f"cx_Freeze-{cx_freeze_version}-*-cp{pyver}-{platform}.whl"
    files = sorted(TOP_DIR.joinpath("wheelhouse").glob(pattern), reverse=True)
    return files[0] if files else None


def install_requires(
    test_data: dict | None = None,
    extra_index_url: list | None = None,
    find_links: list | None = None,
    requirements: list | None = None,
    develop: bool = False,
    editable: bool = False,
    latest: bool = False,
    debug: bool = False,  # noqa: ARG001
    verbose: bool = False,
):
    """Process the install requirements."""
    # Check for pyproject.toml
    pyproject_toml = TOP_DIR / "pyproject.toml"
    if not pyproject_toml.exists():
        print("pyproject.toml not found", file=sys.stderr)
        sys.exit(1)

    basic_requirements = set()
    installed_packages = []
    if IS_MINGW:
        basic_requirements.add("ca-certificates")

    # tomllib saga
    tomllib = import_module_or_none("tomllib")
    if tomllib is None:
        basic_requirements.add("setuptools --upgrade")
        installed_packages += install_requirements(basic_requirements)
        reload_setuptools()
        tomllib = import_module_or_none("setuptools.extern.tomli")
    if tomllib is None:
        basic_requirements.add("tomli")
        installed_packages += install_requirements(basic_requirements)
        tomllib = import_module_or_none("tomli")

    if not PIPENV_ACTIVE:
        basic_requirements.add("pip --upgrade")
        installed_packages += install_requirements(basic_requirements)

    # Get the basic requirements from pyproject.toml
    config = tomllib.loads(pyproject_toml.read_bytes().decode())
    try:
        dependencies: list[str] = config["build-system"]["requires"]
        dependencies += config["project"]["dependencies"]
        for dependency in dependencies:
            if ";sys_platform == 'linux'" in dependency:
                add_platform = "--platform=linux"
            elif ";sys_platform == 'win32'" in dependency:
                add_platform = "--platform=windows,mingw"
            else:
                add_platform = ""
            package = dependency.partition(";")[0] + add_platform
            if package.startswith("lief"):
                package += " --conda=py-lief --only-binary"
            basic_requirements.add(package)
    except KeyError:
        pass

    packages_index_url = ["https://marcelotduarte.github.io/packages/"]
    installed_packages += install_requirements(
        basic_requirements, extra_index_url=packages_index_url
    )
    reload_setuptools()

    # install cx_Freeze and requirements for sample
    cx_freeze_version, cx_freeze_installed = cx_freeze_status()
    if test_data:
        # uninstall
        if cx_freeze_installed:
            if IS_CONDA:
                conda_remove = [CONDA_EXE, "remove", "-p", sys.prefix, "-y"]
                process = subprocess.run(
                    [*conda_remove, "--force-remove", "cx_freeze"], check=False
                )
            elif IS_MINGW:
                pacman_remove = ["pacman", "--noconfirm", "-R"]
                package = f"{MINGW_PACKAGE_PREFIX}-python-cx-freeze"
                process = subprocess.run(
                    [*pacman_remove, package], check=False
                )

            cmd = [sys.executable, "-m", "pip", "uninstall", "-y", "cx_Freeze"]
            process = subprocess.run(cmd, check=False)
            # remove files from editable wheel
            dynload = TOP_DIR / "cx_Freeze/bases/lib-dynload"
            if dynload.is_dir():
                # delete modules that exist in bases/lib-dynload
                ext_suffix = get_config_var("EXT_SUFFIX")
                for file in dynload.glob(f"*{ext_suffix}"):
                    file.unlink()
        # cx_freeze in development mode?
        if develop or editable:
            # install editable
            cmd = [sys.executable, "-m", "pip", "install", "-e", "."]
            cmd += ["--no-build-isolation", "--no-deps"]
            if verbose:
                cmd.append("--verbose")
            env = os.environ.copy()
            if IS_WINDOWS and bool(env.get("CI", None)):
                env["CIBUILDWHEEL"] = "1"  # to force build_ext in GHA
            process = subprocess.run(
                cmd, check=False, cwd=os.fspath(TOP_DIR), env=env
            )
            if editable and (
                (IS_LINUX and not IS_MANYLINUX and not IS_CONDA) or IS_MACOS
            ):
                wheelfile = cibuildwheel_file()
                if wheelfile is None:
                    # build a manylinux to extract the binaries
                    # (simulate editable)
                    installed_packages += install_requirements("cibuildwheel")
                    cmd = [sys.executable, "-m", "cibuildwheel"]
                    cmd += ["--only", cibuildwheel_only()]
                    if not IS_FINAL_VERSION:
                        cmd.append("--prerelease-pythons")
                    if IS_LINUX and which("podman"):
                        env["CIBW_CONTAINER_ENGINE"] = "podman"
                    process = subprocess.run(
                        cmd, check=False, cwd=TOP_DIR, env=env
                    )
                    wheelfile = cibuildwheel_file()
                if wheelfile:
                    with zipfile.ZipFile(wheelfile) as wheelzip:
                        for info in wheelzip.infolist():
                            if info.filename.startswith("cx_Freeze/bases/"):
                                wheelzip.extract(info.filename, TOP_DIR)
        # cx_freeze latest
        elif latest:
            # install from official repository
            installed_packages += install_requirements("cx_Freeze")
        # update the status
        cx_freeze_version, cx_freeze_installed = cx_freeze_status()
        if not cx_freeze_installed:
            # install cx_Freeze from packages
            if IS_MINGW:
                # download and install
                packages_url = packages_index_url[0][:-1]
                package = f"{MINGW_PACKAGE_PREFIX}-python-cx-freeze"
                filename = f"{package}-{cx_freeze_version}-1-any.pkg.tar.zst"
                file_url = f"{packages_url}/msys2/{filename}"
                print("download:", file_url)
                file_tmp, headers = urlretrieve(file_url)
                print(headers)
                cmd = ["pacman", "--noconfirm", "-U", file_tmp]
                process = subprocess.run(cmd, check=False)
                if process.returncode == 0:
                    installed_packages.append(package)
                urlcleanup()
            else:
                if IS_CONDA:
                    require = "cx_freeze"
                else:
                    require = f"cx_Freeze~={cx_freeze_version[:-1]}0"
                installed_packages += install_requirements(
                    f"{require} --pre --no-deps",
                    extra_index_url=packages_index_url,
                )

        # install requirements for sample
        if requirements:
            installed_packages += install_requirements(
                requirements, extra_index_url or [], find_links or []
            )

        if 0:  # pylint: disable=using-constant-test
            # code disabled for now
            # if require not in installed_packages:
            if IS_CONDA:
                platform_opt = "--platform=darwin,linux"
                conda_requirements = [f"c-compiler {platform_opt}"]
                installed_packages += install_requirements(conda_requirements)
                cmd = [sys.executable, "-m", "pip", "install"]
                cmd += [".", "--no-deps", "--no-cache-dir", "-vvv"]
                process = subprocess.run(cmd, cwd=TOP_DIR, check=False)
            if process.returncode == 0:
                # update the status
                cx_freeze_version, cx_freeze_installed = cx_freeze_status()

    if installed_packages:
        print("Requirements installed:", " ".join(installed_packages))


@contextlib.contextmanager
def pushd(target):
    saved = os.getcwd()
    os.chdir(target)
    try:
        yield saved
    finally:
        os.chdir(saved)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("sample")
    parser.add_argument("--basic-requirements", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--develop", action="store_true")
    parser.add_argument("--editable", action="store_true")
    parser.add_argument("--latest", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()
    path = TOP_DIR / "samples" / args.sample
    test_sample = path.name

    # verify if platform to run is in use
    test_json = CI_DIR / "build-test.json"
    test_data = {"test_app": f"test_{test_sample}"}  # default test_data
    test_data = json.loads(test_json.read_bytes()).get(test_sample, test_data)
    if not is_supported_platform(test_data.get("platform")):
        return -1
    # check parameters
    if args.basic_requirements:
        install_requires()
        return 0
    if PIPENV_ACTIVE and args.develop:
        print("--develop option not valid using pipenv")
        return -1
    if PIPENV_ACTIVE and args.editable:
        print("--editable option not valid using pipenv")
        return -1
    kw = {
        "extra_index_url": test_data.pop("extra_index_url", None),
        "find_links": test_data.pop("find_links", None),
        "requirements": test_data.pop("requirements", None),
        "develop": args.develop,
        "editable": args.editable,
        "latest": args.latest,
        "debug": args.debug,
        "verbose": args.verbose,
    }

    print("args:", args)
    print("data:", test_data)
    print("kw:", kw)

    # work in samples directory
    with pushd(path):
        install_requires(test_data, **kw)
        return None


if __name__ == "__main__":
    sys.exit(main())