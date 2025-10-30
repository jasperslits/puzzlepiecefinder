"""Something about Piece."""

from pathlib import Path
import sys

class Piece:
    """Piece info."""
    path: str | None = None
    name: str | None = None

    def __init__(self,filename):
        """Removebg info."""
        self.path = filename
        p = Path(filename)
        if p.exists() is False:
            print(f"Piece file {filename} not found")
            sys.exit(1)
        self.name = p.stem


    def cleanup(self) -> None:
        """Cleanup info."""
        print("Hoi!")

    def removebg(self) -> None:
        """Removebg info."""
        print("Remove")

