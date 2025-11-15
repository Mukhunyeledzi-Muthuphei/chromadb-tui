"""ChromaDB TUI Application Entry Point."""

import sys
from .tui_rich import ChromaTUI


def main():
    """Main entry point."""
    try:
        app = ChromaTUI()
        app.main_loop()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


def run():
    """Entry point function for compatibility."""
    main()


if __name__ == "__main__":
    main()
