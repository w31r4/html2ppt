"""Command-line interface for HTML2PPT."""

import sys


def main() -> int:
    """Main entry point for the CLI.

    Returns:
        Exit code
    """
    import uvicorn

    from html2ppt.config.settings import get_settings

    settings = get_settings()

    print(f"Starting HTML2PPT server at http://{settings.host}:{settings.port}")
    print("Press Ctrl+C to stop")

    uvicorn.run(
        "html2ppt.api.app:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
