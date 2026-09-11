# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.
"""Documentation gate for the Promethium source tree.

A library is only as usable as its docstrings, and docstrings rot faster than
code because nothing executes them. This is the check that makes the standard
real:

  * every module carries a docstring saying what it is for
  * every public class, function and method carries one
  * every public function that takes arguments documents them under `Args:`
  * every public function that raises documents it under `Raises:`

Private names, meaning those that start with a single underscore, are exempt:
they are implementation and the standard is about what a consumer can rely
on. Dunder methods are exempt for the same reason a reader does not need
`__init__` explained twice when the class docstring already says what the
object is, except that `__init__` itself is checked, because that is where a
caller learns what the constructor takes.

    python scripts/check_docstrings.py
    python scripts/check_docstrings.py --summary

Exit status is 0 when the tree conforms and 1 when it does not.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Directories the standard covers. Everything a consumer can import, plus the
# tests, because a test whose purpose is not written down is a test nobody
# dares change.
INCLUDED = ("src/", "tests/", "scripts/")

# Argument names that are never documented, because they are the object
# itself rather than something the caller passes.
IMPLICIT_ARGS = {"self", "cls"}


@dataclass(frozen=True)
class Problem:
    """One documentation defect.

    Attributes:
        path: Repository relative path of the offending file.
        line: One based line number, or 0 when the defect is whole-file.
        message: What is missing and where.
    """

    path: str
    line: int
    message: str

    def render(self) -> str:
        """Format the problem as a single editor-navigable line."""
        return f"{self.path}:{self.line}: {self.message}"


def tracked_files() -> list[str]:
    """Return every Python file the standard applies to.

    Returns:
        Repository relative paths.

    Raises:
        SystemExit: if git cannot be run. A gate that silently passes when it
            cannot look at anything is worse than no gate.
    """
    try:
        completed = subprocess.run(
            ["git", "ls-files", "*.py"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(
            f"check_docstrings: cannot list files with git: {exc}"
        ) from exc

    return [
        line
        for line in completed.stdout.splitlines()
        if line and line.startswith(INCLUDED)
    ]


def is_public(name: str) -> bool:
    """Report whether a name is part of the surface this gate covers.

    Args:
        name: The identifier.

    Returns:
        True for public names and for `__init__`, which is where a caller
        learns what a constructor takes.
    """
    if name == "__init__":
        return True
    return not name.startswith("_")


def raises_explicitly(node: ast.AST) -> bool:
    """Report whether a function body contains a bare `raise` of its own.

    Args:
        node: The function definition.

    Returns:
        True when the function raises somewhere that is not inside a nested
        definition, which would belong to that definition instead.
    """
    for child in ast.walk(node):
        if (
            isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
            and child is not node
        ):
            continue
        if isinstance(child, ast.Raise) and child.exc is not None:
            return True
    return False


def check_file(relative: str) -> list[Problem]:
    """Check one file against the standard.

    Args:
        relative: Repository relative path.

    Returns:
        Every problem found, in source order.
    """
    path = REPO_ROOT / relative
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except SyntaxError as exc:
        return [Problem(relative, exc.lineno or 0, f"does not parse: {exc.msg}")]

    problems: list[Problem] = []

    if not ast.get_docstring(tree):
        problems.append(
            Problem(relative, 1, "module has no docstring saying what it is for")
        )

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if not is_public(node.name):
            continue

        doc = ast.get_docstring(node)
        kind = "class" if isinstance(node, ast.ClassDef) else "function"

        if not doc:
            problems.append(
                Problem(
                    relative,
                    node.lineno,
                    f"public {kind} '{node.name}' has no docstring",
                )
            )
            continue

        if isinstance(node, ast.ClassDef):
            continue

        named = [
            arg.arg
            for arg in node.args.args + node.args.kwonlyargs
            if arg.arg not in IMPLICIT_ARGS
        ]
        if node.args.vararg:
            named.append(node.args.vararg.arg)
        if node.args.kwarg:
            named.append(node.args.kwarg.arg)

        # A test's parameters are fixtures that pytest injects, not values a
        # caller chooses, so documenting them would describe the framework
        # rather than the test. The docstring is still required: a test whose
        # purpose is not written down is a test nobody dares change.
        if node.name.startswith("test_") or relative.endswith("conftest.py"):
            named = []

        if named and "Args:" not in doc:
            problems.append(
                Problem(
                    relative,
                    node.lineno,
                    f"'{node.name}' takes {', '.join(named)} and has no Args section",
                )
            )

        if raises_explicitly(node) and "Raises:" not in doc:
            problems.append(
                Problem(
                    relative,
                    node.lineno,
                    f"'{node.name}' raises and has no Raises section",
                )
            )

    return sorted(problems, key=lambda p: p.line)


def main() -> int:
    """Check every file and report what is missing.

    Returns:
        0 when the tree conforms, 1 otherwise.
    """
    parser = argparse.ArgumentParser(
        description="Check that the source tree is documented."
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print counts per file instead of every problem.",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Files to check. Defaults to everything git tracks in scope.",
    )
    arguments = parser.parse_args()

    files = arguments.paths or tracked_files()

    problems: list[Problem] = []
    for relative in files:
        problems.extend(check_file(relative))

    if not problems:
        print(f"check_docstrings: {len(files)} files checked, all documented.")
        return 0

    if arguments.summary:
        counts: dict[str, int] = {}
        for problem in problems:
            counts[problem.path] = counts.get(problem.path, 0) + 1
        for name in sorted(counts, key=lambda k: -counts[k]):
            print(f"  {counts[name]:3d}  {name}")
    else:
        for problem in problems:
            print(problem.render(), file=sys.stderr)

    print(
        f"check_docstrings: {len(problems)} problem(s) across "
        f"{len({p.path for p in problems})} file(s).",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
