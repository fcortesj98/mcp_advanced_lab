"""Filesystem roots: keep every file operation inside one workspace folder."""

from pathlib import Path


class Workspace:
    """A directory that acts as the server's security boundary (its "root")."""

    def __init__(self, root: Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def resolve(self, relative_path: str) -> Path:
        """Turn a user-supplied path into an absolute path inside the root.

        Raises PermissionError for anything that escapes the root, such as
        "/etc/passwd" or "../../secret.txt".
        """
        path = (self.root / relative_path).resolve()
        if not path.is_relative_to(self.root):
            raise PermissionError("Access denied - path outside workspace roots")
        return path

    def relative(self, path: Path) -> Path:
        """Show a path relative to the root (for friendly output)."""
        return path.relative_to(self.root)
