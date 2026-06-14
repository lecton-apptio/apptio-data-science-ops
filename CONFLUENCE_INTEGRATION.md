# Confluence Integration Guide

Complete guide for integrating and using Confluence documentation publishing with the Apptio Data Science Ops Dashboard.

## Overview

The Confluence integration allows you to automatically publish dashboard documentation to your team's Confluence space. This includes:

- ✅ **Automatic Permission Validation**: Tests CREATE, READ, UPDATE, DELETE permissions
- 📝 **Markdown to Confluence**: Converts README.md to Confluence storage format
- 🔄 **Update Existing Pages**: Automatically updates if page already exists
- 🧹 **Clean Test Pages**: Auto-cleanup of permission test pages
- 🎯 **Flexible Publishing**: Dry-run mode, custom titles, parent pages

## Prerequisites

- Python 3.11+
- Confluence Cloud account with API access
- Confluence space with write permissions

## Installation

The Confluence integration is automatically installed when you install the dashboard dependencies:

```bash
pip install -e .
```

This installs:
- `confluence-integration` package from GitHub
- `atlassian-python-api` for Confluence API access
- All required dependencies

## Configuration

### 1. Get Confluence API Token

1. Visit https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Name it (e.g., "Dashboard Documentation")
4. Copy and save the token securely (you won't see it again)

### 2. Configure Environment Variables

Add these variables to your `.env` file:

```bash
# Confluence Configuration
CONFLUENCE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_EMAIL=your.email@company.com
CONFLUENCE_API_TOKEN=your_api_token_here
CONFLUENCE_SPACE_KEY=YOUR_SPACE
```

**Important Notes:**
- `CONFLUENCE_URL`: Must include `/wiki` at the end
- `CONFLUENCE_EMAIL`: The email you use to log into Confluence
- `CONFLUENCE_API_TOKEN`: The API token you created (not your password)
- `CONFLUENCE_SPACE_KEY`: The space key (visible in Confluence URL)

### 3. Verify Configuration

Copy the example file and edit it:

```bash
cp .env.example .env
# Edit .env with your credentials
```

## Usage

### Test Confluence Access

Before publishing, validate your Confluence API access and permissions:

```bash
# Basic test
python test_confluence_access.py

# With verbose output
python test_confluence_access.py --verbose
```

**What it tests:**
1. **CREATE** - Can create new pages
2. **READ** - Can read page content
3. **UPDATE** - Can update existing pages
4. **READ_VERIFY** - Can verify updates
5. **DELETE** - Can delete pages
6. **DELETE_VERIFY** - Can verify deletion

**Expected Output:**
```
🔍 Testing Confluence API Access
======================================================================
URL: https://your-domain.atlassian.net/wiki
Email: your.email@company.com
Space: YOUR_SPACE
======================================================================

Test Results:
----------------------------------------------------------------------
1. CREATE          ✅ PASS
   Successfully created page '[PERMISSION TEST] 2026-06-13 09:00:00'

2. READ            ✅ PASS
   Successfully read page (version 1)

3. UPDATE          ✅ PASS
   Successfully updated page to version 2

4. READ_VERIFY     ✅ PASS
   Successfully verified update (version 2)

5. DELETE          ✅ PASS
   Successfully deleted page '[PERMISSION TEST] 2026-06-13 09:00:00'

6. DELETE_VERIFY   ✅ PASS
   Successfully verified page deletion (page not found)

======================================================================
🎉 SUCCESS! All tests passed!
======================================================================

Your Confluence API access is fully configured:
✅ Connection established
✅ CREATE permission verified
✅ READ permission verified
✅ UPDATE permission verified
✅ DELETE permission verified

You can now run: python publish_to_confluence.py
```

### Publish Documentation

#### Dry Run (Preview)

See what will be published without making changes:

```bash
python publish_to_confluence.py --dry-run
```

**Output:**
```
📝 Publishing to Confluence
======================================================================
URL: https://your-domain.atlassian.net/wiki
Space: YOUR_SPACE
Dry Run: True
======================================================================

📄 Page Title: Apptio Data Science Ops Dashboard - 2026-06-13

🔍 DRY RUN MODE - No changes will be made

Would publish:
  - Title: Apptio Data Science Ops Dashboard - 2026-06-13
  - Space: YOUR_SPACE
  - Content: 11309 characters
```

#### Publish with Default Settings

Publish README.md to Confluence with auto-generated title:

```bash
python publish_to_confluence.py
```

#### Publish with Custom Title

```bash
python publish_to_confluence.py --page-title "Ops Dashboard - Q1 2026"
```

#### Publish as Child Page

Publish under a specific parent page:

```bash
python publish_to_confluence.py --parent-page-id "123456789"
```

#### Validate Permissions Only

Test permissions without publishing:

```bash
python publish_to_confluence.py --validate-only
```

## Features

### Automatic Permission Validation

Before publishing, the script automatically validates all required permissions:

```python
# Validates these permissions:
- CREATE: Can create new pages
- READ: Can read page content  
- UPDATE: Can modify existing pages
- DELETE: Can remove pages
```

If any permission fails, publishing is aborted with a clear error message.

### Markdown to Confluence Conversion

The script converts Markdown syntax to Confluence Storage Format:

| Markdown | Confluence |
|----------|------------|
| `# Header` | `<h1>Header</h1>` |
| `## Header` | `<h2>Header</h2>` |
| `**bold**` | `<strong>bold</strong>` |
| `*italic*` | `<em>italic</em>` |
| `` `code` `` | `<code>code</code>` |
| ` ```code block``` ` | `<ac:structured-macro>...</ac:structured-macro>` |
| `[link](url)` | `<a href="url">link</a>` |

### Update Existing Pages

If a page with the same title already exists:
- The script updates it instead of creating a duplicate
- Version number is automatically incremented
- Previous content is replaced

### Clean Test Pages

Permission test pages are automatically deleted after validation:
- Test pages are named `[PERMISSION TEST] timestamp`
- Deleted immediately after tests complete
- No manual cleanup required

## Troubleshooting

### Common Issues

#### 403 Forbidden Error

**Problem:**
```
❌ FAILED! Could not publish to Confluence
Error: 403 FORBIDDEN "Request rejected because caller cannot access Confluence"
```

**Solutions:**
1. Generate a new API token at https://id.atlassian.com/manage-profile/security/api-tokens
2. Verify you're using the correct email address (the one you log into Confluence with)
3. Check that you have access to the specified Confluence space
4. Ensure the space key is correct (case-sensitive)
5. Verify your Confluence account has write permissions in the space

#### 404 Not Found Error

**Problem:**
```
Error: 404 NOT FOUND "Space not found"
```

**Solutions:**
1. Verify the space key is correct (check in Confluence URL: `/wiki/spaces/SPACEKEY/`)
2. Ensure you have permission to view the space
3. Check that the Confluence URL is correct
4. Confirm the space exists and is not archived

#### Connection Timeout

**Problem:**
```
Error: Connection timeout
```

**Solutions:**
1. Check your internet connection
2. Verify the Confluence URL is correct and accessible
3. Check if there's a firewall blocking the connection
4. Ensure you're using `https://` in the URL
5. Try accessing Confluence in a web browser to confirm it's available

#### Missing Environment Variables

**Problem:**
```
❌ Missing required environment variables:
   CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_API_TOKEN, CONFLUENCE_SPACE_KEY
```

**Solutions:**
1. Create a `.env` file in the project root
2. Copy from `.env.example`: `cp .env.example .env`
3. Fill in all required Confluence variables
4. Ensure no extra spaces around `=` signs
5. Don't use quotes around values

#### Import Error

**Problem:**
```
❌ Required package not installed.
   Run: pip install -e .
```

**Solutions:**
1. Install the package: `pip install -e .`
2. Activate your virtual environment if using one
3. Verify Python version is 3.11+
4. Check that `pyproject.toml` includes the confluence-integration dependency

### Debug Mode

For detailed error information, use verbose mode:

```bash
# Test with verbose output
python test_confluence_access.py --verbose

# Publish with validation
python publish_to_confluence.py --validate-only
```

## Advanced Usage

### Custom Markdown Conversion

The `publish_to_confluence.py` script includes a basic Markdown to Confluence converter. For more advanced conversions, you can:

1. Modify the `convert_markdown_to_confluence()` function
2. Use a dedicated library like `markdown2confluence`
3. Pre-process your Markdown before publishing

### Automated Publishing

Integrate publishing into your CI/CD pipeline:

```yaml
# .github/workflows/publish-docs.yml
name: Publish to Confluence

on:
  push:
    branches: [main]
    paths:
      - 'README.md'
      - 'docs/**'

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: pip install -e .
      
      - name: Publish to Confluence
        env:
          CONFLUENCE_URL: ${{ secrets.CONFLUENCE_URL }}
          CONFLUENCE_EMAIL: ${{ secrets.CONFLUENCE_EMAIL }}
          CONFLUENCE_API_TOKEN: ${{ secrets.CONFLUENCE_API_TOKEN }}
          CONFLUENCE_SPACE_KEY: ${{ secrets.CONFLUENCE_SPACE_KEY }}
        run: python publish_to_confluence.py
```

### Multiple Spaces

To publish to multiple Confluence spaces:

```bash
# Space 1
CONFLUENCE_SPACE_KEY=TEAM1 python publish_to_confluence.py --page-title "Dashboard - Team 1"

# Space 2
CONFLUENCE_SPACE_KEY=TEAM2 python publish_to_confluence.py --page-title "Dashboard - Team 2"
```

## API Reference

### test_confluence_access.py

```bash
usage: test_confluence_access.py [-h] [--verbose]

Test Confluence API access and permissions

options:
  -h, --help     show this help message and exit
  --verbose, -v  Show detailed test information
```

### publish_to_confluence.py

```bash
usage: publish_to_confluence.py [-h] [--dry-run] [--page-title PAGE_TITLE]
                                [--parent-page-id PARENT_PAGE_ID]
                                [--validate-only]

Publish Apptio Data Science Ops Dashboard documentation to Confluence

options:
  -h, --help            show this help message and exit
  --dry-run             Show what would be published without actually publishing
  --page-title PAGE_TITLE
                        Custom title for the Confluence page
  --parent-page-id PARENT_PAGE_ID
                        ID of parent page (optional)
  --validate-only       Only validate Confluence permissions without publishing
```

## Security Best Practices

1. **Never commit API tokens** to version control
2. **Use environment variables** for sensitive data
3. **Rotate API tokens** regularly (every 90 days recommended)
4. **Limit token scope** to only required permissions
5. **Use separate tokens** for different environments (dev, staging, prod)
6. **Store tokens securely** in password managers or secret management systems

## Support

For issues or questions:

1. Check this guide's troubleshooting section
2. Review the confluence-integration package documentation
3. Verify Confluence API status: https://status.atlassian.com/
4. Contact the AI Platform team

## Related Documentation

- [Main README](README.md) - Project overview and setup
- [Setup Guide](SETUP.md) - Detailed setup instructions
- [Confluence Integration Package](https://github.com/lecton-apptio/confluence-integration) - Source code and documentation

---

**Version**: 1.0.0  
**Last Updated**: 2026-06-13  
**Maintainer**: Ireland Data Science Team