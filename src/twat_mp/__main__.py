"""Command-line entry point for twat-mp."""

from __future__ import annotations

from twat_mp import __version__


def main() -> None:
    """Print package information for the lightweight twat-mp CLI."""
    print(f"twat-mp v{__version__}")


if __name__ == "__main__":
    main()
