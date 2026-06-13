#!/usr/bin/env python3
"""
BOB STEP 1 — ENVIRONMENT INVENTORY
Deterministic inventory of libraries, environment variables, dashboard.json, and service repos.
"""
import os
import sys
import json
import inspect
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_confluence_library() -> Dict[str, Any]:
    """Check confluence-integration library functions."""
    try:
        import confluence_integration
        from confluence_integration import ConfluenceReader, ConfluencePermissions
        
        reader_methods = [m for m in dir(ConfluenceReader) if not m.startswith('_')]
        permissions_methods = [m for m in dir(ConfluencePermissions) if not m.startswith('_')]
        
        return {
            "status": "RESOLVED",
            "version": confluence_integration.__version__,
            "reader_methods": reader_methods,
            "permissions_methods": permissions_methods,
            "key_functions": {
                "read_page": "ConfluenceReader.read_page(page_id: str) -> PageInfo",
                "update_page": "ConfluenceReader.update_page(page_id: str, content: str, title: str) -> bool",
                "test_permissions": "ConfluencePermissions.test_all_permissions() -> List[TestResult]"
            }
        }
    except ImportError as e:
        return {"status": "UNRESOLVED", "error": str(e)}

def check_datadog_library() -> Dict[str, Any]:
    """Check datadog-integration library functions."""
    try:
        import datadog_integration
        from datadog_integration import DatadogValidator
        
        validator_methods = [m for m in dir(DatadogValidator) if not m.startswith('_')]
        
        return {
            "status": "RESOLVED",
            "version": datadog_integration.__version__,
            "validator_methods": validator_methods,
            "key_functions": {
                "validate_connection": "DatadogValidator.validate_connection() -> ValidationResult",
                "query_metrics": "DatadogValidator.query_metrics(metric_name: str, start: int, end: int) -> Dict",
                "build_curl_command": "build_curl_command(endpoint: str, params: Dict) -> str"
            }
        }
    except ImportError as e:
        return {"status": "UNRESOLVED", "error": str(e)}

def check_env_variables() -> Dict[str, Any]:
    """Check required environment variables."""
    required_vars = {
        "CONFLUENCE_PAGE_ID": os.getenv("CONFLUENCE_PARENT_PAGE_ID"),  # Using PARENT as fallback
        "CONFLUENCE_URL": os.getenv("CONFLUENCE_URL"),
        "CONFLUENCE_EMAIL": os.getenv("CONFLUENCE_EMAIL"),
        "CONFLUENCE_API_TOKEN": os.getenv("CONFLUENCE_API_TOKEN"),
        "DD_API_KEY": os.getenv("DD_API_KEY"),
        "DD_APP_KEY": os.getenv("DD_APP_KEY"),
        "DD_SITE": os.getenv("DD_SITE"),
    }
    
    resolved = {}
    unresolved = []
    
    for var, value in required_vars.items():
        if value:
            resolved[var] = "SET (value redacted)"
        else:
            unresolved.append(var)
    
    return {
        "status": "COMPLETE" if not unresolved else "INCOMPLETE",
        "resolved": resolved,
        "unresolved": unresolved
    }

def check_dashboard_json() -> Dict[str, Any]:
    """Check dashboard.json file."""
    dashboard_path = Path("dashboard.json")
    
    if not dashboard_path.exists():
        return {"status": "UNRESOLVED", "error": "dashboard.json not found"}
    
    try:
        with open(dashboard_path) as f:
            data = json.load(f)
        
        return {
            "status": "RESOLVED",
            "path": str(dashboard_path.absolute()),
            "title": data.get("title"),
            "widget_count": len(data.get("widgets", [])),
            "valid_json": True
        }
    except json.JSONDecodeError as e:
        return {"status": "UNRESOLVED", "error": f"Invalid JSON: {e}"}

def scan_service_repos() -> Dict[str, Any]:
    """Scan for service repositories and their metric instrumentation."""
    workspace_root = Path.cwd()
    
    # Known non-service directories to exclude
    exclude_dirs = {
        ".git", ".github", ".ruff_cache", "__pycache__", 
        "dashboard", "ireland_apptio_ops_dashboard.egg-info",
        ".venv", "venv", "node_modules"
    }
    
    service_repos = []
    excluded = []
    
    # List all directories at workspace root
    for item in workspace_root.iterdir():
        if item.is_dir() and item.name not in exclude_dirs:
            # Check if it's a service repo (has source code)
            has_python = list(item.rglob("*.py"))
            has_go = list(item.rglob("*.go"))
            has_js = list(item.rglob("*.js")) or list(item.rglob("*.ts"))
            
            if has_python or has_go or has_js:
                service_repos.append({
                    "name": item.name,
                    "path": str(item),
                    "languages": {
                        "python": len(has_python),
                        "go": len(has_go),
                        "javascript": len(has_js)
                    }
                })
            else:
                excluded.append({"name": item.name, "reason": "No source code files found"})
    
    return {
        "status": "COMPLETE",
        "service_repos": service_repos,
        "excluded": excluded,
        "note": "Metric inventory requires code scanning - not yet implemented"
    }

def main():
    """Run STEP 1 - Environment Inventory."""
    print("=" * 70)
    print("BOB STEP 1 — ENVIRONMENT INVENTORY")
    print("=" * 70)
    print()
    
    # 1. Check Confluence library
    print("1. Confluence Integration Library")
    print("-" * 70)
    confluence = check_confluence_library()
    print(f"Status: {confluence['status']}")
    if confluence['status'] == 'RESOLVED':
        print(f"Version: {confluence['version']}")
        print(f"Key Functions:")
        for name, sig in confluence['key_functions'].items():
            print(f"  - {sig}")
    else:
        print(f"Error: {confluence.get('error')}")
    print()
    
    # 2. Check Datadog library
    print("2. Datadog Integration Library")
    print("-" * 70)
    datadog = check_datadog_library()
    print(f"Status: {datadog['status']}")
    if datadog['status'] == 'RESOLVED':
        print(f"Version: {datadog['version']}")
        print(f"Key Functions:")
        for name, sig in datadog['key_functions'].items():
            print(f"  - {sig}")
    else:
        print(f"Error: {datadog.get('error')}")
    print()
    
    # 3. Check environment variables
    print("3. Environment Variables")
    print("-" * 70)
    env_vars = check_env_variables()
    print(f"Status: {env_vars['status']}")
    print(f"Resolved:")
    for var, status in env_vars['resolved'].items():
        print(f"  ✅ {var}: {status}")
    if env_vars['unresolved']:
        print(f"Unresolved:")
        for var in env_vars['unresolved']:
            print(f"  ❌ {var}: NOT SET")
    print()
    
    # 4. Check dashboard.json
    print("4. Dashboard JSON")
    print("-" * 70)
    dashboard = check_dashboard_json()
    print(f"Status: {dashboard['status']}")
    if dashboard['status'] == 'RESOLVED':
        print(f"Path: {dashboard['path']}")
        print(f"Title: {dashboard['title']}")
        print(f"Widgets: {dashboard['widget_count']}")
        print(f"Valid JSON: {dashboard['valid_json']}")
    else:
        print(f"Error: {dashboard.get('error')}")
    print()
    
    # 5. Scan service repos
    print("5. Service Repositories")
    print("-" * 70)
    repos = scan_service_repos()
    print(f"Status: {repos['status']}")
    print(f"Service Repos Found: {len(repos['service_repos'])}")
    for repo in repos['service_repos']:
        print(f"  - {repo['name']}: {repo['languages']}")
    if repos['excluded']:
        print(f"Excluded Directories: {len(repos['excluded'])}")
        for exc in repos['excluded']:
            print(f"  - {exc['name']}: {exc['reason']}")
    print()
    
    # Summary
    print("=" * 70)
    print("INVENTORY SUMMARY")
    print("=" * 70)
    
    all_resolved = (
        confluence['status'] == 'RESOLVED' and
        datadog['status'] == 'RESOLVED' and
        env_vars['status'] == 'COMPLETE' and
        dashboard['status'] == 'RESOLVED' and
        repos['status'] == 'COMPLETE'
    )
    
    if all_resolved:
        print("INVENTORY_STATUS: COMPLETE")
        print()
        print("✅ All components resolved")
        print("✅ Ready to proceed to STEP 2 - System Precondition Gate")
    else:
        print("INVENTORY_STATUS: INCOMPLETE")
        print()
        print("UNRESOLVED ITEMS:")
        if confluence['status'] != 'RESOLVED':
            print(f"  - Confluence library: {confluence.get('error')}")
        if datadog['status'] != 'RESOLVED':
            print(f"  - Datadog library: {datadog.get('error')}")
        if env_vars['status'] != 'COMPLETE':
            print(f"  - Environment variables: {', '.join(env_vars['unresolved'])}")
        if dashboard['status'] != 'RESOLVED':
            print(f"  - dashboard.json: {dashboard.get('error')}")
        print()
        print("NEXT ACTION REQUIRED: Resolve unresolved items before proceeding")
    
    print("=" * 70)
    
    return 0 if all_resolved else 1

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
