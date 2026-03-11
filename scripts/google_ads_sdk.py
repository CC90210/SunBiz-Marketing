"""
Google Ads SDK Helper — Fallback when MCP server is unavailable.
Direct Python SDK operations for Google Ads API.
"""

import os
from dotenv import load_dotenv

# Load credentials
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.agents"))


def get_client():
    """Initialize Google Ads client from environment variables."""
    from google.ads.googleads.client import GoogleAdsClient

    credentials = {
        "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
        "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
        "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
        "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
        "login_customer_id": os.getenv("GOOGLE_ADS_CUSTOMER_ID"),
        "use_proto_plus": True,
    }

    return GoogleAdsClient.load_from_dict(credentials)


def list_campaigns(customer_id=None):
    """List all campaigns with basic metrics."""
    client = get_client()
    cid = customer_id or os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT campaign.name, campaign.status, campaign.id,
               metrics.impressions, metrics.clicks, metrics.ctr,
               metrics.average_cpc, metrics.conversions, metrics.cost_micros
        FROM campaign
        WHERE campaign.status != 'REMOVED'
        ORDER BY metrics.cost_micros DESC
    """

    response = ga_service.search_stream(customer_id=cid, query=query)

    campaigns = []
    for batch in response:
        for row in batch.results:
            campaigns.append({
                "id": row.campaign.id,
                "name": row.campaign.name,
                "status": row.campaign.status.name,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "ctr": f"{row.metrics.ctr:.2%}",
                "avg_cpc": row.metrics.average_cpc / 1_000_000,
                "conversions": row.metrics.conversions,
                "cost": row.metrics.cost_micros / 1_000_000,
            })

    return campaigns


def create_campaign(name, daily_budget_dollars, bidding_strategy="MAXIMIZE_CONVERSIONS"):
    """Create a new search campaign with budget."""
    client = get_client()
    cid = os.getenv("GOOGLE_ADS_CUSTOMER_ID")

    # Create budget
    campaign_budget_service = client.get_service("CampaignBudgetService")
    budget_operation = client.get_type("CampaignBudgetOperation")
    budget = budget_operation.create
    budget.name = f"{name} Budget"
    budget.amount_micros = int(daily_budget_dollars * 1_000_000)
    budget.delivery_method = client.enums.BudgetDeliveryMethodEnum.STANDARD

    budget_response = campaign_budget_service.mutate_campaign_budgets(
        customer_id=cid, operations=[budget_operation]
    )
    budget_resource = budget_response.results[0].resource_name

    # Create campaign
    campaign_service = client.get_service("CampaignService")
    campaign_operation = client.get_type("CampaignOperation")
    campaign = campaign_operation.create
    campaign.name = name
    campaign.status = client.enums.CampaignStatusEnum.PAUSED
    campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
    campaign.campaign_budget = budget_resource

    # Set bidding strategy
    if bidding_strategy == "MAXIMIZE_CONVERSIONS":
        campaign.maximize_conversions.target_cpa_micros = 0
    elif bidding_strategy == "MAXIMIZE_CLICKS":
        campaign.maximize_clicks.cpc_bid_ceiling_micros = 0

    campaign.network_settings.target_google_search = True
    campaign.network_settings.target_search_network = True

    response = campaign_service.mutate_campaigns(
        customer_id=cid, operations=[campaign_operation]
    )

    return response.results[0].resource_name


def get_campaign_report(customer_id=None, date_range="LAST_7_DAYS"):
    """Get detailed campaign performance report."""
    client = get_client()
    cid = customer_id or os.getenv("GOOGLE_ADS_CUSTOMER_ID")
    ga_service = client.get_service("GoogleAdsService")

    query = f"""
        SELECT campaign.name, campaign.status,
               segments.date,
               metrics.impressions, metrics.clicks, metrics.ctr,
               metrics.average_cpc, metrics.conversions,
               metrics.cost_micros, metrics.conversions_value
        FROM campaign
        WHERE segments.date DURING {date_range}
          AND campaign.status != 'REMOVED'
        ORDER BY segments.date DESC
    """

    response = ga_service.search_stream(customer_id=cid, query=query)

    results = []
    for batch in response:
        for row in batch.results:
            results.append({
                "campaign": row.campaign.name,
                "date": row.segments.date,
                "impressions": row.metrics.impressions,
                "clicks": row.metrics.clicks,
                "ctr": f"{row.metrics.ctr:.2%}",
                "avg_cpc": f"${row.metrics.average_cpc / 1_000_000:.2f}",
                "conversions": row.metrics.conversions,
                "cost": f"${row.metrics.cost_micros / 1_000_000:.2f}",
            })

    return results


if __name__ == "__main__":
    print("Google Ads SDK Helper")
    print("Usage: Import functions from this module")
    print("  from scripts.google_ads_sdk import list_campaigns, create_campaign")
