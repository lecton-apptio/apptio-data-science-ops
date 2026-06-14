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
    """Extract service information from dashboard.json."""
    try:
        # Read dashboard.json from the repository
        dashboard_path = Path(__file__).parent / "dashboard.json"
        
        if not dashboard_path.exists():
            return {
                "status": "UNRESOLVED",
                "error": "dashboard.json not found in repository",
                "target_services": []
            }
        
        with open(dashboard_path, 'r') as f:
            dashboard_data = json.load(f)
        
        # Extract services from dashboard description and widgets
        services_found = set()
        
        # Check description
        description = dashboard_data.get("description", "")
        
        # Check template variables for service definitions
        template_vars = dashboard_data.get("template_variables", [])
        for var in template_vars:
            if var.get("name") == "service":
                default_service = var.get("default", "")
                if default_service and default_service != "*":
                    services_found.add(default_service)
        
        # Parse widgets for service mentions in notes
        widgets = dashboard_data.get("widgets", [])
        for widget in widgets:
            definition = widget.get("definition", {})
            
            # Check note widgets for service lists
            if definition.get("type") == "note":
                content = definition.get("content", "")
                # Look for service mentions in Application Performance section
                if "**Services:**" in content:
                    # Extract services from the line after "**Services:**"
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if "**Services:**" in line:
                            # Next line should contain service names
                            if i + 1 < len(lines):
                                service_line = lines[i + 1]
                                # Parse comma-separated services
                                services = [s.strip() for s in service_line.split(',')]
                                services_found.update(services)
        
        # Known target services from Bob's protocol
        target_services = {
            "pythia", "bifrost", "contextforge", "litellm", "langfuse",
            "expert-guidance-agent", "pythia-slackbot", "pythia-insights"
        }
        
        # Match found services with target services
        tracked_services = []
        for service in sorted(services_found):
            is_target = service in target_services
            tracked_services.append({
                "name": service,
                "is_target_service": is_target,
                "source": "dashboard.json"
            })
        
        return {
            "status": "COMPLETE",
            "dashboard_path": str(dashboard_path),
            "services_in_dashboard": tracked_services,
            "target_services": [s for s in tracked_services if s["is_target_service"]],
            "note": "Services extracted from dashboard.json in repository"
        }
        
    except Exception as e:
        return {
            "status": "UNRESOLVED",
            "error": f"Failed to parse dashboard.json: {str(e)}",
            "target_services": []
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
        if 'dashboard_path' in repos:
            print(f"Dashboard Path: {repos['dashboard_path']}")
        print(f"Target Services Found: {len(repos['target_services'])}")
        for repo in repos['target_services']:
            print(f"  ✅ {repo['name']} (source: {repo.get('source', 'unknown')})")
        if 'services_in_dashboard' in repos:
            non_target = [s for s in repos['services_in_dashboard'] if not s['is_target_service']]
            if non_target:
                print(f"Other Services in Dashboard: {len(non_target)}")
                for svc in non_target[:5]:
                    print(f"  - {svc['name']}")
                if len(non_target) > 5:
                    print(f"  ... and {len(non_target) - 5} more")
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
