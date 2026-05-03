#!/usr/bin/env python3

import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = PROJECT_ROOT / "app"

LEGACY_IMPORT_PREFIXES = (
    "app.core",
    "app.router",
    "app.schema",
    "app.service",
    "app.model",
    "app.ws",
    "app.dragonfly",
    "app.typesense",
)


def _imports_from_file(path: Path) -> list[tuple[int, str]]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError as exc:
        return [(exc.lineno or 1, f"syntax error: {exc.msg}")]

    imports: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append((node.lineno, alias.name))
        elif isinstance(node, ast.ImportFrom):
            if node.level != 0:
                continue
            if node.module:
                imports.append((node.lineno, node.module))
    return imports


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
    except ValueError:
        return False
    return True


def main() -> int:
    errors: list[str] = []
    files = sorted(APP_ROOT.rglob("*.py"))
    for file_path in files:
        imports = _imports_from_file(file_path)
        is_platform_file = _is_relative_to(file_path, APP_ROOT / "platform")
        for lineno, imported in imports:
            if imported.startswith(LEGACY_IMPORT_PREFIXES):
                errors.append(
                    f"{file_path.relative_to(PROJECT_ROOT)}:{lineno}: "
                    f"legacy import path is forbidden: {imported}"
                )

            if is_platform_file and imported.startswith("app.modules."):
                errors.append(
                    f"{file_path.relative_to(PROJECT_ROOT)}:{lineno}: "
                    f"platform layer cannot import domain modules: {imported}"
                )

    if errors:
        print("Architecture import boundary violations detected:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Architecture import boundaries: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
