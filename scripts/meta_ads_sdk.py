"""
Meta Ads SDK Helper — Fallback when MCP server is unavailable.
Direct Python SDK operations for Meta Marketing API.
"""

import os
from dotenv import load_dotenv

# Load credentials
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env.agents"))


def init_api():
    """Initialize Meta Marketing API."""
    from facebook_business.api import FacebookAdsApi

    FacebookAdsApi.init(
        app_id=os.getenv("META_APP_ID"),
        app_secret=os.getenv("META_APP_SECRET"),
        access_token=os.getenv("META_ACCESS_TOKEN"),
    )


def get_account():
    """Get the Ad Account object."""
    from facebook_business.adobjects.adaccount import AdAccount

    init_api()
    return AdAccount(os.getenv("META_AD_ACCOUNT_ID"))


def list_campaigns():
    """List all campaigns with status."""
    account = get_account()
    campaigns = account.get_campaigns(
        fields=["name", "status", "objective", "daily_budget", "lifetime_budget"]
    )

    return [
        {
            "id": c["id"],
            "name": c["name"],
            "status": c["status"],
            "objective": c.get("objective", "N/A"),
            "daily_budget": f"${int(c.get('daily_budget', 0)) / 100:.2f}",
        }
        for c in campaigns
    ]


def create_lending_campaign(name, objective="OUTCOME_LEADS"):
    """Create a campaign with CREDIT special ad category (required for lending)."""
    account = get_account()

    campaign = account.create_campaign(params={
        "name": name,
        "objective": objective,
        "status": "PAUSED",
        "special_ad_categories": ["CREDIT"],  # MANDATORY FOR LENDING
    })

    return {"id": campaign["id"], "name": name, "status": "PAUSED"}


def create_ad_set(campaign_id, name, daily_budget_dollars, targeting=None):
    """Create an ad set within a campaign (credit-compliant targeting)."""
    from facebook_business.adobjects.campaign import Campaign

    init_api()
    campaign = Campaign(campaign_id)

    # Default targeting for credit ads (restricted)
    default_targeting = {
        "geo_locations": {"countries": ["US"]},
        # NO age, gender, or zip code targeting for CREDIT category
    }

    ad_set = campaign.create_ad_set(params={
        "name": name,
        "daily_budget": int(daily_budget_dollars * 100),  # In cents
        "billing_event": "IMPRESSIONS",
        "optimization_goal": "LEAD_GENERATION",
        "targeting": targeting or default_targeting,
        "status": "PAUSED",
    })

    return {"id": ad_set["id"], "name": name}


def upload_image(image_path):
    """Upload an image and return image hash."""
    from facebook_business.adobjects.adimage import AdImage

    account = get_account()
    image = AdImage(parent_id=account.get_id())
    image[AdImage.Field.filename] = image_path
    image.remote_create()

    return {
        "hash": image[AdImage.Field.hash],
        "url": image.get(AdImage.Field.url, ""),
    }


def create_ad_creative(name, page_id, image_hash, link, message, headline, description, cta="APPLY_NOW"):
    """Create an ad creative with image."""
    account = get_account()

    creative = account.create_ad_creative(params={
        "name": name,
        "object_story_spec": {
            "page_id": page_id,
            "link_data": {
                "image_hash": image_hash,
                "link": link,
                "message": message,
                "name": headline,
                "description": description,
                "call_to_action": {"type": cta},
            },
        },
    })

    return {"id": creative["id"], "name": name}


def create_ad(ad_set_id, name, creative_id):
    """Create an ad linking creative to ad set."""
    from facebook_business.adobjects.adset import AdSet

    init_api()
    ad_set = AdSet(ad_set_id)

    ad = ad_set.create_ad(params={
        "name": name,
        "creative": {"creative_id": creative_id},
        "status": "PAUSED",
    })

    return {"id": ad["id"], "name": name}


def get_campaign_insights(campaign_id, date_preset="last_7d"):
    """Get campaign performance insights."""
    from facebook_business.adobjects.campaign import Campaign

    init_api()
    campaign = Campaign(campaign_id)

    insights = campaign.get_insights(
        fields=[
            "impressions", "clicks", "ctr", "cpc",
            "spend", "actions", "cost_per_action_type",
            "reach", "frequency",
        ],
        params={"date_preset": date_preset},
    )

    return [dict(insight) for insight in insights]


def get_account_insights(date_preset="last_7d"):
    """Get account-level performance insights."""
    account = get_account()

    insights = account.get_insights(
        fields=[
            "impressions", "clicks", "ctr", "cpc",
            "spend", "actions", "cost_per_action_type",
        ],
        params={
            "date_preset": date_preset,
            "level": "campaign",
        },
    )

    return [dict(insight) for insight in insights]


if __name__ == "__main__":
    print("Meta Ads SDK Helper")
    print("Usage: Import functions from this module")
    print("  from scripts.meta_ads_sdk import list_campaigns, create_lending_campaign")
