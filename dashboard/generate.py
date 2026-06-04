"""Generate dashboard static files."""

import argparse
import sys
from pathlib import Path
from dashboard.app import create_app
from dashboard.config import settings
from dashboard import __version__


def generate_dashboard(dry_run: bool = False) -> int:
    """
    Generate dashboard static files.
    
    Args:
        dry_run: If True, only validate without generating files
        
    Returns:
        Exit code (0 for success, 1 for failure)
    """
    print(f"🚀 Generating Dashboard v{__version__}")
    print(f"Environment: {settings.environment}")
    print(f"DataDog configured: {settings.has_datadog_credentials}")
    print()
    
    if dry_run:
        print("✅ Dry run successful - no files generated")
        return 0
    
    try:
        # Create Flask app
        app = create_app()
        
        # Ensure output directory exists
        output_dir = Path("dist")
        output_dir.mkdir(exist_ok=True)
        
        print(f"📁 Output directory: {output_dir.absolute()}")
        
        # Generate index.html
        with app.test_client() as client:
            response = client.get("/")
            if response.status_code == 200:
                index_file = output_dir / "index.html"
                index_file.write_text(response.data.decode("utf-8"))
                print(f"✅ Generated: {index_file}")
            else:
                print(f"❌ Failed to generate index.html: {response.status_code}")
                return 1
        
        # Copy static assets (if any)
        static_dir = Path("dashboard/static")
        if static_dir.exists():
            import shutil
            dest_static = output_dir / "static"
            if dest_static.exists():
                shutil.rmtree(dest_static)
            shutil.copytree(static_dir, dest_static)
            print(f"✅ Copied static assets to: {dest_static}")
        
        print()
        print("🎉 Dashboard generation complete!")
        print(f"📊 View at: file://{output_dir.absolute()}/index.html")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error generating dashboard: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate operational dashboard static files"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate without generating files",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    args = parser.parse_args()
    return generate_dashboard(dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
