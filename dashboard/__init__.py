"""
Ireland Apptio Operations Dashboard
====================================

Operational Review Dashboard for Apptio AI Platform using IBM Carbon Design System.

Version: 0.0.1
"""

__version__ = "0.0.1"
__author__ = "Ireland Apptio Data Science Team"
__email__ = "data-science@apptio.com"

from dashboard.app import create_app
from dashboard.config import Settings

__all__ = ["create_app", "Settings", "__version__"]
