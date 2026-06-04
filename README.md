# Apptio Data Science Ops Dashboard

Production-grade operational dashboard for the Apptio AI Platform, automatically deployed via GitHub Actions with IBM Carbon Design System.

## Overview

This dashboard provides real-time monitoring and observability for AI Platform services including Pythia, Bifrost, ContextForge, LiteLLM, and Langfuse across multiple regions (uw2p, uw2d, uw2s).

**Key Features:**
- 🚀 Automated deployment via GitHub Actions
- 🎨 IBM Carbon Design System UI
- 📊 Real-time DataDog metrics integration
- 🌍 Multi-region monitoring
- 🔄 Static site generation for GitHub Pages
- ✅ Production-ready with linting, type checking, and testing

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     GitHub Actions Workflow                  │
│  (Triggers on push to main or manual dispatch from any branch)│
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Build & Quality Checks                    │
│  • Python 3.11 setup                                         │
│  • Install dependencies (pyproject.toml)                     │
│  • Ruff linting                                              │
│  • Black formatting check                                    │
│  • MyPy type checking                                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                   Dashboard Generation                       │
│  • Flask app fetches DataDog metrics                         │
│  • Renders IBM Carbon UI templates                           │
│  • Generates static HTML                                     │
│  • Validates build output                                    │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Pages Deployment                   │
│  • Deploys to gh-pages branch                                │
│  • Accessible at: https://<org>.github.io/<repo>             │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites
- Python 3.11+
- DataDog Access Token (see [SETUP.md](SETUP.md))
- GitHub repository with Actions enabled

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd apptio-data-science-ops
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -e .
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your DataDog credentials
   ```

4. **Run locally:**
   ```bash
   python -m dashboard
   # Or for development:
   python -m dashboard.generate --dry-run
   ```

### GitHub Actions Deployment

See [SETUP.md](SETUP.md) for complete setup instructions including:
- GitHub secrets configuration
- Workflow triggers (automatic and manual)
- Testing from feature branches
- Troubleshooting

## Project Structure

```
apptio-data-science-ops/
├── .github/
│   └── workflows/
│       ├── generate-dashboard.yml    # Main deployment workflow
│       └── dashboard-report.yml      # Reporting workflow
├── dashboard/
│   ├── __init__.py
│   ├── __main__.py                   # CLI entry point
│   ├── app.py                        # Flask application
│   ├── config.py                     # Pydantic settings
│   ├── generate.py                   # Static site generator
│   ├── build.py                      # Build validation
│   └── templates/
│       └── index.html                # IBM Carbon UI template
├── pyproject.toml                    # Project configuration
├── .gitignore
├── README.md                         # This file
└── SETUP.md                          # Setup guide
```

## Configuration

### Environment Variables

Required in GitHub Secrets and local `.env`:

```bash
DD_ACCESS_TOKEN=your_datadog_access_token
SERVICES=pythia,bifrost,contextforge,litellm,langfuse
REGIONS=uw2p,uw2d,uw2s
APP_VERSION=0.0.1
ENVIRONMENT=production
```

### Services Monitored

- **Pythia**: AI agent orchestration
- **Bifrost**: API gateway
- **ContextForge**: Context management
- **LiteLLM**: LLM proxy
- **Langfuse**: Observability platform

### Regions

- **uw2p**: US West 2 Production
- **uw2d**: US West 2 Development
- **uw2s**: US West 2 Staging

## Development

### Code Quality

The project uses modern Python tooling:

```bash
# Linting
ruff check .

# Formatting
black --check .

# Type checking
mypy dashboard/

# Run all checks
make lint  # If Makefile exists
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=dashboard
```

### Local Testing

```bash
# Dry run (no actual generation)
python -m dashboard.generate --dry-run

# Generate static site locally
python -m dashboard.generate

# Validate build
python -m dashboard.build
```

## Deployment

### Automatic Deployment

Pushes to `main` branch automatically trigger the workflow:

```bash
git add .
git commit -m "Update dashboard"
git push origin main
```

### Manual Deployment

Trigger from any branch via GitHub Actions UI:

1. Go to `Actions` tab
2. Select `Generate Dashboard` workflow
3. Click `Run workflow`
4. Select your branch
5. Click `Run workflow` button

### Deployment Verification

After deployment:
1. Check workflow run status in Actions tab
2. Visit GitHub Pages URL
3. Verify dashboard loads with current data
4. Check browser console for errors

## Monitoring & Metrics

The dashboard displays:

### Service Health
- Status indicators (🟢 Healthy, 🟡 Warning, 🔴 Critical)
- P95 latency
- Error rates
- Request throughput

### Regional Performance
- Latency by region
- Error rates by region
- Service availability

### System Metrics
- CPU utilization
- Memory usage
- Network I/O

## Troubleshooting

### Common Issues

**Workflow fails with authentication error:**
- Verify `DD_ACCESS_TOKEN` is set in GitHub secrets
- Check token has not expired
- Ensure token has read permissions for metrics API

**Dashboard shows no data:**
- Verify service names match DataDog tags
- Check time range in queries
- Review DataDog API status

**Build fails locally:**
- Ensure Python 3.11+ is installed
- Activate virtual environment
- Run `pip install -e .`

**Type checking errors:**
- Run `mypy dashboard/` to see specific issues
- Check `pyproject.toml` for mypy configuration

See [SETUP.md](SETUP.md) for detailed troubleshooting.

## Contributing

### Development Workflow

1. Create feature branch
2. Make changes
3. Test locally with `--dry-run`
4. Run quality checks (ruff, black, mypy)
5. Commit and push
6. Test via manual workflow trigger
7. Create PR to main

### Code Standards

- Follow PEP 8 style guide
- Use type hints for all functions
- Write docstrings for public APIs
- Keep functions focused and small
- Add tests for new features

## Version History

- **v0.0.1** (2026-06-04): Initial release
  - GitHub Actions deployment
  - IBM Carbon Design System UI
  - DataDog integration
  - Multi-region support

## Support

For issues or questions:
1. Check [SETUP.md](SETUP.md) troubleshooting section
2. Review workflow logs in Actions tab
3. Verify DataDog connectivity
4. Contact AI Platform team

## License

Internal use only - Apptio AI Platform Team

---

**Version**: 0.0.1  
**Last Updated**: 2026-06-04  
**Maintainer**: Ireland Data Science Team