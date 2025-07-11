"""Source of samples to tests."""

from __future__ import annotations

# Each test description is a list of 5 items:
#
# 1. a module name that will be imported by ModuleFinder
# 2. a list of module names that ModuleFinder is required to find
# 3. a list of module names that ModuleFinder should complain
#    about because they are not found
# 4. a list of module names that ModuleFinder should complain
#    about because they MAY be not found
# 5. a string specifying packages to create; the format is obvious imo.

ABSOLUTE_IMPORT_TEST = [
    "a.module",
    ["a", "a.module", "b", "b.x", "b.y", "b.z", "__future__", "sys", "gc"],
    ["blahblah", "z"],
    [],
    """\
mymodule.py
a/__init__.py
a/module.py
    from __future__ import absolute_import
    import sys # sys
    import blahblah # fails
    import gc # gc
    import b.x # b.x
    from b import y # b.y
    from b.z import * # b.z.*
a/gc.py
a/sys.py
    import mymodule
a/b/__init__.py
a/b/x.py
a/b/y.py
a/b/z.py
b/__init__.py
    import z
b/unused.py
b/x.py
b/y.py
b/z.py
""",
]

BYTECODE_TEST = ["a", ["a"], [], [], ""]

CODING_DEFAULT_UTF8_TEST = [
    "a_utf8",
    ["a_utf8", "b_utf8"],
    [],
    [],
    """\
a_utf8.py
    # use the default of utf8
    print('Unicode test A code point 2090 \u2090 that is not valid in cp1252')
    import b_utf8
b_utf8.py
    # use the default of utf8
    print('Unicode test B code point 2090 \u2090 that is not valid in cp1252')
""",
]

CODING_EXPLICIT_CP1252_TEST = [
    "a_cp1252",
    ["a_cp1252", "b_utf8"],
    [],
    [],
    """\
a_cp1252.py
    # coding=cp1252
    # 0xe2 is not allowed in utf8
    print('CP1252 test P\xe2t\xe9')
    import b_utf8
b_utf8.py
    # use the default of utf8
    print('Unicode test A code point 2090 \u2090 that is not valid in cp1252')
""",
]

CODING_EXPLICIT_UTF8_TEST = [
    "a_utf8",
    ["a_utf8", "b_utf8"],
    [],
    [],
    """\
a_utf8.py
    # coding=utf8
    print('Unicode test A code point 2090 \u2090 that is not valid in cp1252')
    import b_utf8
b_utf8.py
    # use the default of utf8
    print('Unicode test B code point 2090 \u2090 that is not valid in cp1252')
""",
]

EXTENDED_OPARGS_TEST = [
    "a",
    ["a", "b"],
    [],
    [],
    f"""\
a.py
    {list(range(2**16))!r}
    import b
b.py
""",
]  # 2**16 constants

FIND_SPEC_TEST = [
    "find_spec",
    [],
    [],
    [],
    """\
find_spec/dummypackage/__init__.py
    print("Hi, I'm a package!")
    raise Exception("package-level exception should not occur during freeze")
    from . import dummymodule
find_spec/dummypackage/dummymodule.py
    print("Hi, I'm a module!")
    raise Exception("module-level exception should not occur during freeze")
find_spec/hello.py
    import dummypackage.dummymodule
    print("Hi, I'm a program.")
    raise Exception("This exception is fine.")
""",
]

IMPORT_CALL_TEST = [
    "testpkg1",
    ["testpkg1", "fake_pkgutil"],
    [],
    [],
    """\
testpkg1/__init__.py
    __path__ = __import__('fake_pkgutil').extend_path(__path__, __name__)
fake_pkgutil.py
""",
]

INVALID_MODULE_NAME_TEST = [
    "testpkg1",
    [],
    [],
    [],
    """\
testpkg1/__init__.py
testpkg1/invalid-identifier.py
    # Since this is a python module, we try to import it even though its name
    # is not a valid identifier (required for e.g. win32com.gen_py.*)
testpkg1/not.importable.py
    # The . in the filename means this file cannot be imported as a module.
testpkg1/submod.py
    a = 2
""",
]

MAYBE_TEST = [
    "a.module",
    ["a", "a.module", "sys", "b"],
    ["c"],
    ["b.something"],
    """\
a/__init__.py
a/module.py
    from b import something
    from c import something
b/__init__.py
    from sys import *
""",
]

MAYBE_TEST_NEW = [
    "a.module",
    ["a", "a.module", "sys", "b", "__future__"],
    ["c"],
    ["b.something"],
    """\
a/__init__.py
a/module.py
    from b import something
    from c import something
b/__init__.py
    from __future__ import absolute_import
    from sys import *
""",
]

NAMESPACE_TEST = [
    "main",
    ["main", "namespace.package"],
    [],
    [],
    """\
main.py
    import namespace.package
namespace/package/__init__.py
    print('This is namespace.package')
""",
]

NESTED_NAMESPACE_TEST = [
    "main",
    ["main", "namespace.package.one", "namespace.package.two"],
    [],
    [],
    """\
main.py
    import namespace.package.one
    import namespace.package.two
namespace/package/one.py
    print('This is namespace.package module one')
namespace/package/two.py
    print('This is namespace.package module two')
""",
]

PACKAGE_TEST = [
    "a.module",
    ["a", "a.b", "a.c", "a.module", "mymodule", "sys"],
    ["blahblah", "c"],
    [],
    """\
mymodule.py
a/__init__.py
    import blahblah
    from a import b
    import c
a/module.py
    import sys
    from a import b as x
    from a.c import sillyname
a/b.py
a/c.py
    from a.module import x
    import mymodule as sillyname
    from sys import version_info
""",
]

RELATIVE_IMPORT_TEST = [
    "a.module",
    [
        "__future__",
        "a",
        "a.module",
        "a.b",
        "a.b.y",
        "a.b.z",
        "a.b.c",
        "a.b.c.moduleC",
        "a.b.c.d",
        "a.b.c.e",
        "a.b.x",
        "gc",
    ],
    [],
    [],
    """\
mymodule.py
a/__init__.py
    from .b import y, z # a.b.y, a.b.z
a/module.py
    from __future__ import absolute_import # __future__
    import gc # gc
a/gc.py
a/sys.py
a/b/__init__.py
    from ..b import x # a.b.x
    #from a.b.c import moduleC
    from .c import moduleC # a.b.moduleC
a/b/x.py
a/b/y.py
a/b/z.py
a/b/g.py
a/b/c/__init__.py
    from ..c import e # a.b.c.e
a/b/c/moduleC.py
    from ..c import d # a.b.c.d
a/b/c/d.py
a/b/c/e.py
a/b/c/x.py
""",
]

RELATIVE_IMPORT_TEST_2 = [
    "a.module",
    [
        "a",
        "a.module",
        "a.sys",
        "a.b",
        "a.b.y",
        "a.b.z",
        "a.b.c",
        "a.b.c.d",
        "a.b.c.e",
        "a.b.c.moduleC",
        "a.b.c.f",
        "a.b.x",
        "a.another",
    ],
    [],
    [],
    """\
mymodule.py
a/__init__.py
    from . import sys # a.sys
a/another.py
a/module.py
    from .b import y, z # a.b.y, a.b.z
a/gc.py
a/sys.py
a/b/__init__.py
    from .c import moduleC # a.b.c.moduleC
    from .c import d # a.b.c.d
a/b/x.py
a/b/y.py
a/b/z.py
a/b/c/__init__.py
    from . import e # a.b.c.e
a/b/c/moduleC.py
    #
    from . import f   # a.b.c.f
    from .. import x  # a.b.x
    from ... import another # a.another
a/b/c/d.py
a/b/c/e.py
a/b/c/f.py
""",
]

RELATIVE_IMPORT_TEST_3 = [
    "a.module",
    ["a", "a.module"],
    ["a.bar"],
    [],
    """\
a/__init__.py
    def foo(): pass
a/module.py
    from . import foo
    from . import bar
""",
]

RELATIVE_IMPORT_TEST_4 = [
    "a.module",
    ["a", "a.module"],
    [],
    [],
    """\
a/__init__.py
    def foo(): pass
a/module.py
    from . import *
""",
]

SAME_NAME_AS_BAD_TEST = [
    "a.module",
    ["a", "a.module", "b", "b.c"],
    ["c"],
    [],
    """\
a/__init__.py
a/module.py
    import c
    from b import c
b/__init__.py
b/c.py
""",
]


SCAN_CODE_TEST = [
    "imports_sample",
    ["imports_sample"],
    [],
    [],
    """\
imports_sample.py
    import moda
    from modb import b
    from . import modc
    from .modd import d
    from mode import *
    from ..modf import *
    import modg.submod
    try: pass
    finally: import modh
""",
]

SYNTAX_ERROR_TEST = [
    "invalid_syntax",
    [],
    [],
    [],
    """\
invalid_syntax.py
    raise = 2
""",
]

SYNTAX_ERROR_TEST_2 = [
    "a.module",
    ["a", "a.module", "b"],
    ["b.module"],
    [],
    """\
a/__init__.py
a/module.py
    import b.module
b/__init__.py
b/module.py
    ?  # SyntaxError: invalid syntax
""",
]

SUB_PACKAGE_TEST = [
    "main",
    ["p", "p.p1", "p.q", "p.q.q1", "main"],
    [],
    [],
    """\
main.py
    import p.p1
    import p.q.q1
p/__init__.py
p/p1.py
    print('This is p.p1')
p/q/__init__.py
p/q/q1.py
    print('This is p.q.q1')
setup.py
    from cx_Freeze import setup
    setup(
        name="test",
        version="0.1",
        description="Sample for test with cx_Freeze",
        executables=["main.py"],
    )
""",
]

EDITABLE_PACKAGE_TEST = [
    "main",
    ["foobar", "foobar.baz", "main"],
    [],
    [],
    """\
main.py
    import foobar.baz
foo-bar/setup.py
    from distutils.core import setup
    setup(name="foo-bar", version="0.0.1", packages=["foobar"])
foo-bar/foobar/__init__.py
    print('This is foobar')
foo-bar/foobar/baz.py
    print('This is foobar.baz')
""",
]
