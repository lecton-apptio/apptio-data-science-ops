"""Build dashboard for deployment."""

import sys
from pathlib import Path

from dashboard import __version__


def build_dashboard() -> int:
    """
    Build dashboard for deployment.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print(f"🔨 Building Dashboard v{__version__}")
    print()

    try:
        dist_dir = Path("dist")

        if not dist_dir.exists():
            print("❌ dist/ directory not found. Run generate first.")
            return 1

        # Verify required files
        required_files = ["index.html"]
        missing_files = []

        for file in required_files:
            file_path = dist_dir / file
            if not file_path.exists():
                missing_files.append(file)
            else:
                print(f"✅ Found: {file}")

        if missing_files:
            print(f"\n❌ Missing files: {', '.join(missing_files)}")
            return 1

        print()
        print("🎉 Build complete!")
        print(f"📦 Artifacts in: {dist_dir.absolute()}")

        return 0

    except Exception as e:
        print(f"❌ Build failed: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point."""
    return build_dashboard()


if __name__ == "__main__":
    sys.exit(main())
