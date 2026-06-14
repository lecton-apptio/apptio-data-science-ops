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
        "CONFLUENCE_PAGE_ID": os.getenv("CONFLUENCE_PAGE_ID") or os.getenv("CONFLUENCE_PARENT_PAGE_ID"),
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
    # Scan parent directory where service repos are located
    github_root = Path("/Users/lecton/Documents/GitHub")
    
    # Known service repos from Bob's protocol
    target_services = {
        "pythia", "bifrost", "contextforge", "litellm", "langfuse",
        "expert-guidance-agent", "pythia-slackbot"
    }
    
    # Known non-service directories to exclude
    exclude_dirs = {
        ".git", ".github", ".ruff_cache", "__pycache__", ".DS_Store",
        "dashboard", "ireland_apptio_ops_dashboard.egg-info",
        ".venv", "venv", "node_modules", ".vscode", ".deepeval",
        "apptio-data-science-ops", "operational-dashboard"
    }
    
    service_repos = []
    excluded = []
    
    if not github_root.exists():
        return {
            "status": "UNRESOLVED",
            "error": f"GitHub root directory not found: {github_root}",
            "service_repos": [],
            "excluded": []
        }
    
    # List all directories at GitHub root
    for item in github_root.iterdir():
        if not item.is_dir() or item.name in exclude_dirs or item.name.startswith('.'):
            continue
            
        # Check if it's a service repo (has source code)
        has_python = list(item.glob("**/*.py"))[:100]  # Limit to first 100 for performance
        has_go = list(item.glob("**/*.go"))[:100]
        has_js = list(item.glob("**/*.js"))[:50] or list(item.glob("**/*.ts"))[:50]
        
        if has_python or has_go or has_js:
            is_target = item.name in target_services
            service_repos.append({
                "name": item.name,
                "path": str(item),
                "is_target_service": is_target,
                "languages": {
                    "python": len(has_python),
                    "go": len(has_go),
                    "javascript": len(has_js)
                }
            })
        else:
            excluded.append({"name": item.name, "reason": "No source code files found"})
    
    # Separate target services from other repos
    target_repos = [r for r in service_repos if r["is_target_service"]]
    other_repos = [r for r in service_repos if not r["is_target_service"]]
    
    return {
        "status": "COMPLETE",
        "github_root": str(github_root),
        "target_services": target_repos,
        "other_repos": other_repos,
        "excluded": excluded,
        "note": "Metric inventory scanning not yet implemented"
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
    if repos['status'] == 'COMPLETE':
        print(f"GitHub Root: {repos['github_root']}")
        print(f"Target Services Found: {len(repos['target_services'])}")
        for repo in repos['target_services']:
            print(f"  ✅ {repo['name']}: {repo['languages']}")
        if repos['other_repos']:
            print(f"Other Repos Found: {len(repos['other_repos'])}")
            for repo in repos['other_repos'][:5]:  # Show first 5
                print(f"  - {repo['name']}: {repo['languages']}")
            if len(repos['other_repos']) > 5:
                print(f"  ... and {len(repos['other_repos']) - 5} more")
    else:
        print(f"Error: {repos.get('error')}")
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
