import re
import tomllib
from pathlib import Path

PROJECT_NAME = "gran-calendar"
PROJECT_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"
UV_LOCK_PATH = PROJECT_ROOT / "uv.lock"


def next_install_version(version: str) -> str:
    major, minor, patch = [int(part) for part in version.split(".")]
    if patch >= 99:
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"


def read_project_version() -> str:
    with PYPROJECT_PATH.open("rb") as metadata_file:
        metadata = tomllib.load(metadata_file)
    return metadata["project"]["version"]


def replace_once(path: Path, pattern: str, replacement: str) -> None:
    text = path.read_text()
    updated_text, replacement_count = re.subn(pattern, replacement, text, count=1)
    if replacement_count != 1:
        raise RuntimeError(f"Could not update version in {path}")
    path.write_text(updated_text)


def write_project_version(version: str) -> None:
    replace_once(PYPROJECT_PATH, r'(version = ")[^"]+(")', rf"\g<1>{version}\2")
    package_pattern = rf'(\[\[package\]\]\nname = "{PROJECT_NAME}"\nversion = ")[^"]+(")'
    replace_once(UV_LOCK_PATH, package_pattern, rf"\g<1>{version}\2")


def main() -> None:
    version = next_install_version(read_project_version())
    write_project_version(version)
    print(version)


if __name__ == "__main__":
    main()
