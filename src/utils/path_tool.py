"""Path helpers for resolving project-relative files."""

import os


def get_project_root() -> str:
    current_file = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_file)
    return os.path.dirname(os.path.dirname(current_dir))


def get_abs_path(relative_path: str) -> str:
    """Return an absolute path from a project-relative path."""
    project_root = get_project_root()
    return os.path.join(project_root, relative_path)


if __name__ == "__main__":
    print(get_abs_path("config/config.txt"))
