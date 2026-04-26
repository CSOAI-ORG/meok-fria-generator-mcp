"""meok-fria-generator — EU AI Act Article 27 FRIA generator. By MEOK AI Labs."""
from .server import mcp


def main():
    mcp.run()


__version__ = "1.0.0"
__all__ = ["mcp", "main"]
