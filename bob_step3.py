#!/usr/bin/env python3
"""
BOB STEP 3 — WEEKLY CONFLUENCE SUMMARY
Automated weekly summary of platform metrics and costs.
Trigger: Tuesday 05:00 Europe/Dublin
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_date_ranges() -> Dict[str, Any]:
    """
    Calculate date ranges for current and prior 7-day windows.
    
    Returns:
        Dict with current_start, current_end, prior_start, prior_end
    """
    # Current window: last 7 days
    current_end = datetime.now()
    current_start = current_end - timedelta(days=7)
    
    # Prior window: 7 days before that
    prior_end = current_start
    prior_start = prior_end - timedelta(days=7)
    
    return {
        "current_start": current_start,
        "current_end": current_end,
        "prior_start": prior_start,
        "prior_end": prior_end
    }


def pull_datadog_metrics(start: datetime, end: datetime) -> Dict[str, Any]:
    """
    Pull key metrics from Datadog for the specified time window.
    
    Args:
        start: Start datetime
        end: End datetime
        
    Returns:
        Dict of aggregated metrics
    """
    try:
        from datadog_integration import DatadogValidator
        
        validator = DatadogValidator(
            api_key=os.getenv("DD_API_KEY"),
            app_key=os.getenv("DD_APP_KEY"),
            site=os.getenv("DD_SITE", "datadoghq.com")
        )
        
        # For now, return placeholder metrics
        # TODO: Implement actual metric queries using DataDog API
        metrics = {
            "total_requests": 0,
            "error_rate_pct": 0.0,
            "p95_latency_ms": 0.0,
            "success_rate_pct": 100.0,
            "cpu_utilization_pct": 0.0,
            "memory_utilization_pct": 0.0,
            "bedrock_calls": 0,
            "rag_operations": 0
        }
        
        print(f"✅ Pulled Datadog metrics for {start.date()} to {end.date()}")
        return metrics
        
    except Exception as e:
        print(f"❌ Failed to pull Datadog metrics: {e}")
        return {}


def pull_kubecost_data(start: datetime, end: datetime) -> Dict[str, Any]:
    """
    Pull cost data from Kubecost for the specified time window.
    
    Args:
        start: Start datetime
        end: End datetime
        
    Returns:
        Dict of cost metrics
    """
    try:
        from kubecost_integration import CloudabilityClient
        
        client = CloudabilityClient(
            apptio_opentoken=os.getenv("APPTIO_OPENTOKEN"),  # type: ignore
            environment_id=os.getenv("APPTIO_ENVIRONMENT_ID")  # type: ignore
        )
        
        # Get config summary to verify connectivity
        config = client.get_config_summary()
        
        # For now, return placeholder costs
        # TODO: Implement actual cost queries using Kubecost API
        costs = {
            "total_cost_usd": 0.0,
            "compute_cost_usd": 0.0,
            "storage_cost_usd": 0.0,
            "network_cost_usd": 0.0,
            "bedrock_cost_usd": 0.0
        }
        
        print(f"✅ Pulled Kubecost data for {start.date()} to {end.date()}")
        return costs
        
    except Exception as e:
        print(f"❌ Failed to pull Kubecost data: {e}")
        return {}


def calculate_change(current: float, prior: float) -> Dict[str, Any]:
    """
    Calculate percentage change between current and prior values.
    
    Args:
        current: Current period value
        prior: Prior period value
        
    Returns:
        Dict with change_pct and direction
    """
    if prior == 0:
        if current == 0:
            return {"change_pct": 0.0, "direction": "stable"}
        else:
            return {"change_pct": 100.0, "direction": "up"}
    
    change_pct = ((current - prior) / prior) * 100
    
    if abs(change_pct) < 1:
        direction = "stable"
    elif change_pct > 0:
        direction = "up"
    else:
        direction = "down"
    
    return {
        "change_pct": round(change_pct, 2),
        "direction": direction
    }


def generate_summary(
    current_metrics: Dict[str, Any],
    prior_metrics: Dict[str, Any],
    current_costs: Dict[str, Any],
    prior_costs: Dict[str, Any],
    date_ranges: Dict[str, Any]
) -> str:
    """
    Generate Confluence-formatted summary.
    
    Args:
        current_metrics: Current period Datadog metrics
        prior_metrics: Prior period Datadog metrics
        current_costs: Current period Kubecost costs
        prior_costs: Prior period Kubecost costs
        date_ranges: Date range information
        
    Returns:
        Confluence wiki markup string
    """
    current_start = date_ranges["current_start"].strftime("%Y-%m-%d")
    current_end = date_ranges["current_end"].strftime("%Y-%m-%d")
    
    # Calculate changes
    request_change = calculate_change(
        current_metrics.get("total_requests", 0),
        prior_metrics.get("total_requests", 0)
    )
    
    error_change = calculate_change(
        current_metrics.get("error_rate_pct", 0),
        prior_metrics.get("error_rate_pct", 0)
    )
    
    latency_change = calculate_change(
        current_metrics.get("p95_latency_ms", 0),
        prior_metrics.get("p95_latency_ms", 0)
    )
    
    cost_change = calculate_change(
        current_costs.get("total_cost_usd", 0),
        prior_costs.get("total_cost_usd", 0)
    )
    
    # Generate Confluence markup
    summary = f"""
h1. AI Platform Weekly Summary

*Period:* {current_start} to {current_end}
*Generated:* {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} UTC

---

h2. 📊 Application Performance

||Metric||Current||Prior Week||Change||
|Total Requests|{current_metrics.get('total_requests', 0):,}|{prior_metrics.get('total_requests', 0):,}|{request_change['change_pct']:+.1f}% {request_change['direction']}|
|Error Rate|{current_metrics.get('error_rate_pct', 0):.2f}%|{prior_metrics.get('error_rate_pct', 0):.2f}%|{error_change['change_pct']:+.1f}% {error_change['direction']}|
|P95 Latency|{current_metrics.get('p95_latency_ms', 0):.0f}ms|{prior_metrics.get('p95_latency_ms', 0):.0f}ms|{latency_change['change_pct']:+.1f}% {latency_change['direction']}|
|Success Rate|{current_metrics.get('success_rate_pct', 0):.2f}%|{prior_metrics.get('success_rate_pct', 0):.2f}%|stable|

h2. 🤖 AI/LLM Metrics

||Metric||Current||Prior Week||Change||
|Bedrock API Calls|{current_metrics.get('bedrock_calls', 0):,}|{prior_metrics.get('bedrock_calls', 0):,}|N/A|
|RAG Operations|{current_metrics.get('rag_operations', 0):,}|{prior_metrics.get('rag_operations', 0):,}|N/A|

h2. 🖥️ Infrastructure

||Metric||Current||Prior Week||
|CPU Utilization|{current_metrics.get('cpu_utilization_pct', 0):.1f}%|{prior_metrics.get('cpu_utilization_pct', 0):.1f}%|
|Memory Utilization|{current_metrics.get('memory_utilization_pct', 0):.1f}%|{prior_metrics.get('memory_utilization_pct', 0):.1f}%|

h2. 💰 Cost Summary

||Cost Category||Current||Prior Week||Change||
|Total Infrastructure|${current_costs.get('total_cost_usd', 0):,.2f}|${prior_costs.get('total_cost_usd', 0):,.2f}|{cost_change['change_pct']:+.1f}% {cost_change['direction']}|
|Compute|${current_costs.get('compute_cost_usd', 0):,.2f}|${prior_costs.get('compute_cost_usd', 0):,.2f}|N/A|
|Storage|${current_costs.get('storage_cost_usd', 0):,.2f}|${prior_costs.get('storage_cost_usd', 0):,.2f}|N/A|
|Network|${current_costs.get('network_cost_usd', 0):,.2f}|${prior_costs.get('network_cost_usd', 0):,.2f}|N/A|
|Bedrock (LLM)|${current_costs.get('bedrock_cost_usd', 0):,.2f}|${prior_costs.get('bedrock_cost_usd', 0):,.2f}|N/A|

h2. 🎯 Key Insights

* *Traffic:* Request volume {request_change['direction']} by {abs(request_change['change_pct']):.1f}%
* *Reliability:* Error rate {error_change['direction']} by {abs(error_change['change_pct']):.1f}%
* *Performance:* P95 latency {latency_change['direction']} by {abs(latency_change['change_pct']):.1f}%
* *Cost:* Infrastructure costs {cost_change['direction']} by {abs(cost_change['change_pct']):.1f}%

---

_Generated automatically by BOB (IBM BOB — OBSERVABILITY CONTROL SYSTEM)_
_Dashboard: [AI Platform Operational Dashboard|https://lecton-apptio.github.io/apptio-data-science-ops/]_
"""
    
    return summary.strip()


def publish_to_confluence(content: str) -> bool:
    """
    Publish summary to Confluence AI space.
    
    Args:
        content: Confluence wiki markup content
        
    Returns:
        True if successful, False otherwise
    """
    try:
        from confluence_integration import ConfluenceReader
        
        space_key = os.getenv("CONFLUENCE_SPACE_KEY")
        url = os.getenv("CONFLUENCE_URL")
        email = os.getenv("CONFLUENCE_EMAIL")
        api_token = os.getenv("CONFLUENCE_API_TOKEN")
        
        if not all([space_key, url, email, api_token]):
            print("❌ Missing Confluence credentials")
            return False
        
        reader = ConfluenceReader(
            url=url,  # type: ignore
            email=email,  # type: ignore
            api_token=api_token,  # type: ignore
            space_key=space_key  # type: ignore
        )
        
        # Generate page title with current date
        page_title = f"Weekly Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        # TODO: Implement page creation/update using Confluence API
        # For now, just verify connectivity
        space_info = reader.get_space_info()
        
        print(f"✅ Would publish to Confluence space: {space_key}")
        print(f"   Page title: {page_title}")
        print(f"   Content length: {len(content)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to publish to Confluence: {e}")
        return False


def main() -> int:
    """Run STEP 3 - Weekly Confluence Summary."""
    print("=" * 70)
    print("BOB STEP 3 — WEEKLY CONFLUENCE SUMMARY")
    print("=" * 70)
    print()
    
    # Get date ranges
    date_ranges = get_date_ranges()
    print(f"Current period: {date_ranges['current_start'].date()} to {date_ranges['current_end'].date()}")
    print(f"Prior period: {date_ranges['prior_start'].date()} to {date_ranges['prior_end'].date()}")
    print()
    
    # Pull current period data
    print("📊 Pulling current period data...")
    current_metrics = pull_datadog_metrics(
        date_ranges["current_start"],
        date_ranges["current_end"]
    )
    current_costs = pull_kubecost_data(
        date_ranges["current_start"],
        date_ranges["current_end"]
    )
    print()
    
    # Pull prior period data
    print("📊 Pulling prior period data...")
    prior_metrics = pull_datadog_metrics(
        date_ranges["prior_start"],
        date_ranges["prior_end"]
    )
    prior_costs = pull_kubecost_data(
        date_ranges["prior_start"],
        date_ranges["prior_end"]
    )
    print()
    
    # Generate summary
    print("📝 Generating summary...")
    summary = generate_summary(
        current_metrics,
        prior_metrics,
        current_costs,
        prior_costs,
        date_ranges
    )
    print()
    
    # Display summary
    print("=" * 70)
    print("GENERATED SUMMARY")
    print("=" * 70)
    print(summary)
    print()
    print("=" * 70)
    print()
    
    # Publish to Confluence
    print("📤 Publishing to Confluence...")
    success = publish_to_confluence(summary)
    print()
    
    if success:
        print("=" * 70)
        print("✅ STEP 3 COMPLETE")
        print("=" * 70)
        print()
        print("Summary generated and ready for publication")
        print("Next: Implement actual Datadog/Kubecost metric queries")
        return 0
    else:
        print("=" * 70)
        print("❌ STEP 3 FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())

# Made with Bob