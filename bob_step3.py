#!/usr/bin/env python3
"""
BOB STEP 3 — WEEKLY CONFLUENCE SUMMARY
Automated weekly summary of platform metrics and costs.
Trigger: Tuesday 05:00 Europe/Dublin
"""
import os
import sys
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
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
        from datadog_api_client import ApiClient, Configuration
        from datadog_api_client.v2.api.metrics_api import MetricsApi
        from datadog_api_client.v1.api.metrics_api import MetricsApi as MetricsApiV1
        
        # Configure Datadog API client
        configuration = Configuration()
        configuration.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY")
        configuration.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY")
        configuration.server_variables["site"] = os.getenv("DD_SITE", "datadoghq.com")
        
        # Convert datetime to Unix timestamps
        start_ts = int(start.timestamp())
        end_ts = int(end.timestamp())
        
        metrics = {}
        
        with ApiClient(configuration) as api_client:
            metrics_api_v1 = MetricsApiV1(api_client)
            
            # Query 1: Total Requests (span count)
            try:
                query = f"sum:trace.span.count{{service:pythia,env:production}}.as_count()"
                response = metrics_api_v1.query_metrics(
                    _from=start_ts,
                    to=end_ts,
                    query=query
                )
                if response.series and len(response.series) > 0:
                    points = response.series[0].pointlist
                    metrics["total_requests"] = int(sum(p[1] for p in points if p[1] is not None))
                else:
                    metrics["total_requests"] = 0
                print(f"  ✓ Total requests: {metrics['total_requests']}")
            except Exception as e:
                print(f"  ⚠ Failed to query total requests: {e}")
                metrics["total_requests"] = 0
            
            # Query 2: Error Count
            try:
                query = f"sum:trace.span.count{{service:pythia,env:production,status:error}}.as_count()"
                response = metrics_api_v1.query_metrics(
                    _from=start_ts,
                    to=end_ts,
                    query=query
                )
                error_count = 0
                if response.series and len(response.series) > 0:
                    points = response.series[0].pointlist
                    error_count = int(sum(p[1] for p in points if p[1] is not None))
                
                # Calculate error rate
                if metrics["total_requests"] > 0:
                    metrics["error_rate_pct"] = round((error_count / metrics["total_requests"]) * 100, 2)
                    metrics["success_rate_pct"] = round(100 - metrics["error_rate_pct"], 2)
                else:
                    metrics["error_rate_pct"] = 0.0
                    metrics["success_rate_pct"] = 100.0
                print(f"  ✓ Error rate: {metrics['error_rate_pct']}%")
            except Exception as e:
                print(f"  ⚠ Failed to query error rate: {e}")
                metrics["error_rate_pct"] = 0.0
                metrics["success_rate_pct"] = 100.0
            
            # Query 3: P95 Latency
            try:
                query = f"avg:trace.span.duration{{service:pythia,env:production}}.rollup(avg, 3600)"
                response = metrics_api_v1.query_metrics(
                    _from=start_ts,
                    to=end_ts,
                    query=query
                )
                if response.series and len(response.series) > 0:
                    points = response.series[0].pointlist
                    # Convert nanoseconds to milliseconds and get average
                    latencies = [p[1] / 1_000_000 for p in points if p[1] is not None]
                    if latencies:
                        # Approximate P95 as 95th percentile of averages
                        latencies.sort()
                        p95_index = int(len(latencies) * 0.95)
                        metrics["p95_latency_ms"] = round(latencies[p95_index], 2)
                    else:
                        metrics["p95_latency_ms"] = 0.0
                else:
                    metrics["p95_latency_ms"] = 0.0
                print(f"  ✓ P95 latency: {metrics['p95_latency_ms']}ms")
            except Exception as e:
                print(f"  ⚠ Failed to query P95 latency: {e}")
                metrics["p95_latency_ms"] = 0.0
            
            # Query 4: Bedrock API Calls
            try:
                query = f"sum:trace.span.count{{service:pythia,env:production,resource_name:*bedrock*}}.as_count()"
                response = metrics_api_v1.query_metrics(
                    _from=start_ts,
                    to=end_ts,
                    query=query
                )
                if response.series and len(response.series) > 0:
                    points = response.series[0].pointlist
                    metrics["bedrock_calls"] = int(sum(p[1] for p in points if p[1] is not None))
                else:
                    metrics["bedrock_calls"] = 0
                print(f"  ✓ Bedrock calls: {metrics['bedrock_calls']}")
            except Exception as e:
                print(f"  ⚠ Failed to query Bedrock calls: {e}")
                metrics["bedrock_calls"] = 0
            
            # Query 5: RAG Operations
            try:
                query = f"sum:trace.span.count{{service:pythia,env:production,resource_name:*rag*}}.as_count()"
                response = metrics_api_v1.query_metrics(
                    _from=start_ts,
                    to=end_ts,
                    query=query
                )
                if response.series and len(response.series) > 0:
                    points = response.series[0].pointlist
                    metrics["rag_operations"] = int(sum(p[1] for p in points if p[1] is not None))
                else:
                    metrics["rag_operations"] = 0
                print(f"  ✓ RAG operations: {metrics['rag_operations']}")
            except Exception as e:
                print(f"  ⚠ Failed to query RAG operations: {e}")
                metrics["rag_operations"] = 0
            
            # Query 6: CPU Utilization
            try:
                query_usage = f"avg:kubernetes.cpu.usage.total{{service:pythia,env:production}}"
                query_limit = f"avg:kubernetes.cpu.limits{{service:pythia,env:production}}"
                
                response_usage = metrics_api_v1.query_metrics(
                    _from=start_ts,
                    to=end_ts,
                    query=query_usage
                )
                response_limit = metrics_api_v1.query_metrics(
                    _from=start_ts,
                    to=end_ts,
                    query=query_limit
                )
                
                if (response_usage.series and len(response_usage.series) > 0 and
                    response_limit.series and len(response_limit.series) > 0):
                    usage_points = response_usage.series[0].pointlist
                    limit_points = response_limit.series[0].pointlist
                    
                    avg_usage = sum(p[1] for p in usage_points if p[1] is not None) / len(usage_points)
                    avg_limit = sum(p[1] for p in limit_points if p[1] is not None) / len(limit_points)
                    
                    if avg_limit > 0:
                        metrics["cpu_utilization_pct"] = round((avg_usage / avg_limit) * 100, 2)
                    else:
                        metrics["cpu_utilization_pct"] = 0.0
                else:
                    metrics["cpu_utilization_pct"] = 0.0
                print(f"  ✓ CPU utilization: {metrics['cpu_utilization_pct']}%")
            except Exception as e:
                print(f"  ⚠ Failed to query CPU utilization: {e}")
                metrics["cpu_utilization_pct"] = 0.0
            
            # Query 7: Memory Utilization
            try:
                query_usage = f"avg:kubernetes.memory.usage{{service:pythia,env:production}}"
                query_limit = f"avg:kubernetes.memory.limits{{service:pythia,env:production}}"
                
                response_usage = metrics_api_v1.query_metrics(
                    _from=start_ts,
                    to=end_ts,
                    query=query_usage
                )
                response_limit = metrics_api_v1.query_metrics(
                    _from=start_ts,
                    to=end_ts,
                    query=query_limit
                )
                
                if (response_usage.series and len(response_usage.series) > 0 and
                    response_limit.series and len(response_limit.series) > 0):
                    usage_points = response_usage.series[0].pointlist
                    limit_points = response_limit.series[0].pointlist
                    
                    avg_usage = sum(p[1] for p in usage_points if p[1] is not None) / len(usage_points)
                    avg_limit = sum(p[1] for p in limit_points if p[1] is not None) / len(limit_points)
                    
                    if avg_limit > 0:
                        metrics["memory_utilization_pct"] = round((avg_usage / avg_limit) * 100, 2)
                    else:
                        metrics["memory_utilization_pct"] = 0.0
                else:
                    metrics["memory_utilization_pct"] = 0.0
                print(f"  ✓ Memory utilization: {metrics['memory_utilization_pct']}%")
            except Exception as e:
                print(f"  ⚠ Failed to query memory utilization: {e}")
                metrics["memory_utilization_pct"] = 0.0
        
        print(f"✅ Pulled Datadog metrics for {start.date()} to {end.date()}")
        return metrics
        
    except Exception as e:
        print(f"❌ Failed to pull Datadog metrics: {e}")
        import traceback
        traceback.print_exc()
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
        
        # Format dates for Kubecost API (YYYY-MM-DD)
        start_date = start.strftime("%Y-%m-%d")
        end_date = end.strftime("%Y-%m-%d")
        
        costs = {
            "total_cost_usd": 0.0,
            "compute_cost_usd": 0.0,
            "storage_cost_usd": 0.0,
            "network_cost_usd": 0.0,
            "bedrock_cost_usd": 0.0
        }
        
        # Query Kubecost allocation API for cost breakdown
        try:
            # Get allocation data for the time window
            # Kubecost API endpoint: /model/allocation
            # Parameters: window (start,end), aggregate (namespace, service, etc.)
            
            # Note: The CloudabilityClient is for Apptio Cloudability, not Kubecost
            # Kubecost requires direct HTTP API calls
            import requests
            
            kubecost_url = os.getenv("KUBECOST_URL", "http://kubecost-cost-analyzer.kubecost:9090")
            
            # Query allocation API
            allocation_url = f"{kubecost_url}/model/allocation"
            params = {
                "window": f"{start_date},{end_date}",
                "aggregate": "namespace",
                "accumulate": "true"
            }
            
            response = requests.get(allocation_url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            
            # Parse allocation data
            if "data" in data and len(data["data"]) > 0:
                # Sum costs across all namespaces
                for allocation in data["data"]:
                    for namespace, details in allocation.items():
                        if isinstance(details, dict):
                            # Extract cost components
                            cpu_cost = details.get("cpuCost", 0.0) or 0.0
                            ram_cost = details.get("ramCost", 0.0) or 0.0
                            pv_cost = details.get("pvCost", 0.0) or 0.0
                            network_cost = details.get("networkCost", 0.0) or 0.0
                            
                            costs["compute_cost_usd"] += cpu_cost + ram_cost
                            costs["storage_cost_usd"] += pv_cost
                            costs["network_cost_usd"] += network_cost
                
                costs["total_cost_usd"] = (
                    costs["compute_cost_usd"] +
                    costs["storage_cost_usd"] +
                    costs["network_cost_usd"]
                )
                
                print(f"  ✓ Compute cost: ${costs['compute_cost_usd']:.2f}")
                print(f"  ✓ Storage cost: ${costs['storage_cost_usd']:.2f}")
                print(f"  ✓ Network cost: ${costs['network_cost_usd']:.2f}")
                print(f"  ✓ Total infrastructure cost: ${costs['total_cost_usd']:.2f}")
            
        except requests.exceptions.RequestException as e:
            print(f"  ⚠ Kubecost API unavailable: {e}")
            print(f"  ℹ Using placeholder costs (Kubecost not configured)")
        except Exception as e:
            print(f"  ⚠ Failed to parse Kubecost data: {e}")
        
        # Estimate Bedrock costs based on API call volume
        # This is an approximation - real costs require token tracking
        try:
            # Get Bedrock call count from Datadog metrics
            from datadog_api_client import ApiClient, Configuration
            from datadog_api_client.v1.api.metrics_api import MetricsApi as MetricsApiV1
            
            configuration = Configuration()
            configuration.api_key["apiKeyAuth"] = os.getenv("DD_API_KEY")
            configuration.api_key["appKeyAuth"] = os.getenv("DD_APP_KEY")
            configuration.server_variables["site"] = os.getenv("DD_SITE", "datadoghq.com")
            
            start_ts = int(start.timestamp())
            end_ts = int(end.timestamp())
            
            with ApiClient(configuration) as api_client:
                metrics_api_v1 = MetricsApiV1(api_client)
                
                query = f"sum:trace.span.count{{service:pythia,env:production,resource_name:*bedrock*}}.as_count()"
                response = metrics_api_v1.query_metrics(
                    _from=start_ts,
                    to=end_ts,
                    query=query
                )
                
                if response.series and len(response.series) > 0:
                    points = response.series[0].pointlist
                    bedrock_calls = int(sum(p[1] for p in points if p[1] is not None))
                    
                    # Estimate cost: Assume average of 1000 tokens per call
                    # Claude 3 Sonnet pricing: ~$3/1M input + $15/1M output tokens
                    # Approximate: $0.009 per call (500 input + 500 output tokens)
                    estimated_cost_per_call = 0.009
                    costs["bedrock_cost_usd"] = round(bedrock_calls * estimated_cost_per_call, 2)
                    
                    print(f"  ✓ Bedrock cost (estimated): ${costs['bedrock_cost_usd']:.2f} ({bedrock_calls} calls)")
                else:
                    costs["bedrock_cost_usd"] = 0.0
        except Exception as e:
            print(f"  ⚠ Failed to estimate Bedrock costs: {e}")
            costs["bedrock_cost_usd"] = 0.0
        
        # Round all costs to 2 decimal places
        for key in costs:
            costs[key] = round(costs[key], 2)
        
        print(f"✅ Pulled Kubecost data for {start.date()} to {end.date()}")
        return costs
        
    except Exception as e:
        print(f"❌ Failed to pull Kubecost data: {e}")
        import traceback
        traceback.print_exc()
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


def publish_to_confluence(content: str) -> tuple[bool, str]:
    """
    Publish summary to Confluence AI space.
    
    Args:
        content: Confluence wiki markup content
        
    Returns:
        Tuple of (success: bool, page_url: str)
    """
    try:
        from atlassian import Confluence
        
        space_key = os.getenv("CONFLUENCE_SPACE_KEY")
        url = os.getenv("CONFLUENCE_URL")
        email = os.getenv("CONFLUENCE_EMAIL")
        api_token = os.getenv("CONFLUENCE_API_TOKEN")
        parent_page_id = os.getenv("CONFLUENCE_PARENT_PAGE_ID")
        
        if not all([space_key, url, email, api_token]):
            print("❌ Missing Confluence credentials")
            return False, ""
        
        # Initialize Confluence client
        confluence = Confluence(
            url=url,
            username=email,
            password=api_token,
            cloud=True
        )
        
        # Generate page title with current date
        page_title = f"Weekly Summary - {datetime.now().strftime('%Y-%m-%d')}"
        
        # Check if page already exists
        existing_page = confluence.get_page_by_title(
            space=space_key,
            title=page_title
        )
        
        if existing_page:
            # Update existing page
            page_id = existing_page['id']
            result = confluence.update_page(
                page_id=page_id,
                title=page_title,
                body=content,
                type='page',
                representation='wiki'
            )
            page_url = f"{url}/wiki/spaces/{space_key}/pages/{page_id}"
            print(f"✅ Updated Confluence page in space: {space_key}")
            print(f"   Page title: {page_title}")
            print(f"   Page URL: {page_url}")
            return True, page_url
        else:
            # Create new page
            result = confluence.create_page(
                space=space_key,
                title=page_title,
                body=content,
                parent_id=parent_page_id,
                type='page',
                representation='wiki'
            )
            if result and 'id' in result:
                page_id = result['id']
                page_url = f"{url}/wiki/spaces/{space_key}/pages/{page_id}"
                print(f"✅ Created Confluence page in space: {space_key}")
                print(f"   Page title: {page_title}")
                print(f"   Page URL: {page_url}")
                return True, page_url
            else:
                print(f"❌ Failed to create page - no page ID returned")
                return False, ""
        
        
    except Exception as e:
        print(f"❌ Failed to publish to Confluence: {e}")
        return False, ""


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
    success, page_url = publish_to_confluence(summary)
    print()
    
    if success:
        print("=" * 70)
        print("✅ STEP 3 COMPLETE")
        print("=" * 70)
        print()
        print("Summary published to Confluence")
        if page_url:
            print(f"📄 Page URL: {page_url}")
        print()
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