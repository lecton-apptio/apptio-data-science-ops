"""Flask application with IBM Carbon Design System."""

from flask import Flask, render_template, jsonify
from flask_cors import CORS
from dashboard.config import settings
from dashboard import __version__


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder="static", template_folder="templates")
    
    # Configuration
    app.config["DEBUG"] = settings.debug
    app.config["ENV"] = settings.environment
    
    # Enable CORS
    CORS(app)
    
    # Register routes
    register_routes(app)
    
    return app


def register_routes(app: Flask) -> None:
    """Register application routes."""
    
    @app.route("/")
    def index() -> str:
        """Render main dashboard page."""
        return render_template(
            "index.html",
            app_name=settings.app_name,
            version=__version__,
            environment=settings.environment,
        )
    
    @app.route("/api/health")
    def health() -> tuple[dict[str, str], int]:
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "version": __version__,
            "environment": settings.environment,
        }), 200
    
    @app.route("/api/metrics")
    def metrics() -> tuple[dict[str, any], int]:
        """Get dashboard metrics."""
        # TODO: Implement actual metrics fetching
        return jsonify({
            "services": settings.services,
            "regions": settings.regions,
            "version": __version__,
        }), 200


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
    )
