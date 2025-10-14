"""Generate synthetic marketing dataset aligned with marketing_schema."""
from __future__ import annotations

import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import List

from faker import Faker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from schemas.marketing_schema import (
    MarketingDataset,
    Brand,
    Objective,
    KPI,
    Channel,
    Campaign,
    CampaignChannel,
    CampaignChannelKPI,
    CampaignOrder,
    ChannelType,
    KPIUnit,
    Currency,
)


faker = Faker("en_GB")
random.seed(42)
Faker.seed(42)


def build_brands() -> List[Brand]:
    categories = [
        ("Makeup", "Luma Cosmetics"),
        ("Skincare", "DermaLab"),
        ("Haircare", "Aurora Hair"),
        ("Fragrance", "Noir Essence"),
        ("Wellness", "Pure Botanics"),
        ("Men's Grooming", "Atlas Groom"),
        ("Accessories", "VelvetLane"),
        ("Lifestyle", "Fjord Living"),
        ("Nutrition", "VitaCore"),
        ("Tech Beauty", "PulseSkin"),
    ]
    markets = ["Germany", "France", "United Kingdom", "Italy", "Spain"]
    brands = []
    for idx, (category, name) in enumerate(categories, start=1):
        brands.append(
            Brand(
                brand_id=f"BRD-{idx:03d}",
                name=name,
                category=category,
                market=random.choice(markets),
            )
        )
    return brands


def build_objectives() -> List[Objective]:
    return [
        Objective(
            objective_id="OBJ-AWARENESS",
            name="Brand Awareness",
            description="Increase reach across priority markets",
        ),
        Objective(
            objective_id="OBJ-ACQUISITION",
            name="Customer Acquisition",
            description="Generate new customers from paid channels",
        ),
        Objective(
            objective_id="OBJ-RETENTION",
            name="Retention",
            description="Drive repeat purchases from existing customers",
        ),
        Objective(
            objective_id="OBJ-NEW-LAUNCH",
            name="Product Launch",
            description="Support new product release campaign",
        ),
        Objective(
            objective_id="OBJ-COMMERCE",
            name="E-commerce Revenue",
            description="Maximize online revenue from paid media",
        ),
    ]


def build_kpis() -> List[KPI]:
    return [
        KPI(
            kpi_id="KPI-CTR",
            name="Click Through Rate",
            description="Ratio of clicks to impressions",
            unit=KPIUnit.RATIO,
            direction="higher_is_better",
        ),
        KPI(
            kpi_id="KPI-CVR",
            name="Conversion Rate",
            description="Purchases divided by clicks",
            unit=KPIUnit.RATIO,
            direction="higher_is_better",
        ),
        KPI(
            kpi_id="KPI-ROAS",
            name="Return On Ad Spend",
            description="Revenue divided by advertising spend",
            unit=KPIUnit.CURRENCY,
            direction="higher_is_better",
        ),
        KPI(
            kpi_id="KPI-IMPRESSIONS",
            name="Impressions",
            description="Number of ad impressions",
            unit=KPIUnit.COUNT,
            direction="higher_is_better",
        ),
        KPI(
            kpi_id="KPI-CPA",
            name="Cost Per Acquisition",
            description="Spend divided by conversions",
            unit=KPIUnit.CURRENCY,
            direction="lower_is_better",
        ),
    ]


def build_channels() -> List[Channel]:
    top_channels = [
        ("CH-DIG", "Digital", ChannelType.DIGITAL, None),
        ("CH-SOC", "Social", ChannelType.SOCIAL, "CH-DIG"),
        ("CH-DSP", "Programmatic Display", ChannelType.DISPLAY, "CH-DIG"),
        ("CH-VID", "Online Video", ChannelType.DISPLAY, "CH-DIG"),
        ("CH-SEA", "Paid Search", ChannelType.SEARCH, "CH-DIG"),
        ("CH-EML", "Email", ChannelType.EMAIL, None),
        ("CH-RET", "Retail", ChannelType.RETAIL, None),
        ("CH-PR", "Public Relations", ChannelType.PR, None),
    ]
    return [
        Channel(channel_id=cid, name=name, type=ch_type, parent_id=parent)
        for cid, name, ch_type, parent in top_channels
    ]


def build_campaigns(
    campaign_count: int,
    brands: List[Brand],
    objectives: List[Objective],
    channels: List[Channel],
    kpis: List[KPI],
) -> List[Campaign]:
    campaigns: List[Campaign] = []
    start_reference = date(2025, 1, 1)
    channel_pool = [ch for ch in channels if ch.parent_id is not None or ch.type != ChannelType.DIGITAL]

    for idx in range(1, campaign_count + 1):
        brand = random.choice(brands)
        objective = random.choice(objectives)
        start_delta = random.randint(0, 120)
        duration_days = random.randint(30, 90)
        start_date = start_reference + timedelta(days=start_delta)
        end_date = start_date + timedelta(days=duration_days)
        budget = random.randint(80000, 250000)
        currency = Currency.EUR

        selected_channels = random.sample(channel_pool, k=random.randint(2, 4))
        campaign_channels: List[CampaignChannel] = []
        for channel in selected_channels:
            spend = budget * random.uniform(0.2, 0.5)
            kpi_samples: List[CampaignChannelKPI] = []
            for kpi in kpis:
                if kpi.kpi_id in {"KPI-CTR", "KPI-ROAS", "KPI-CVR", "KPI-CPA"}:
                    value = {
                        "KPI-CTR": random.uniform(0.01, 0.08),
                        "KPI-ROAS": random.uniform(2.0, 5.0),
                        "KPI-CVR": random.uniform(0.01, 0.06),
                        "KPI-CPA": random.uniform(12.0, 45.0),
                    }[kpi.kpi_id]
                else:
                    value = random.randint(100000, 500000)
                kpi_samples.append(
                    CampaignChannelKPI(
                        kpi_id=kpi.kpi_id,
                        value=round(value, 4) if isinstance(value, float) else value,
                        unit=kpi.unit,
                        period_start=start_date,
                        period_end=end_date,
                    )
                )
            campaign_channels.append(
                CampaignChannel(
                    channel_id=channel.channel_id,
                    spend=round(spend, 2),
                    currency=currency,
                    kpis=kpi_samples,
                )
            )

        order_count = random.randint(2, 4)
        orders = []
        for order_idx in range(order_count):
            revenue = random.randint(15000, 85000)
            orders.append(
                CampaignOrder(
                    order_id=f"ORD-{idx:04d}-{order_idx+1:02d}",
                    platform=random.choice(["Shopify", "Magento", "Retail Store", "Amazon"]),
                    revenue=float(revenue),
                    currency=currency,
                    conversion_date=start_date + timedelta(days=random.randint(5, duration_days)),
                )
            )

        campaigns.append(
            Campaign(
                campaign_id=f"CMP-2025-{idx:04d}",
                name=faker.catch_phrase(),
                objective_id=objective.objective_id,
                brand_id=brand.brand_id,
                region=random.choice(["DE", "FR", "UK", "ES", "IT"]),
                start_date=start_date,
                end_date=end_date,
                budget=float(budget),
                currency=currency,
                channels=campaign_channels,
                orders=orders,
            )
        )

    return campaigns


def generate_dataset(campaign_count: int = 600) -> MarketingDataset:
    brands = build_brands()
    objectives = build_objectives()
    kpis = build_kpis()
    channels = build_channels()
    campaigns = build_campaigns(campaign_count, brands, objectives, channels, kpis)
    return MarketingDataset(
        brands=brands,
        objectives=objectives,
        kpis=kpis,
        channels=channels,
        campaigns=campaigns,
    )


def main():
    dataset = generate_dataset()
    output_path = Path("data/marketing/marketing_data.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(dataset.model_dump(mode="json"), f, indent=2, ensure_ascii=False)
    print(f"Generated marketing dataset with {len(dataset.campaigns)} campaigns -> {output_path}")


if __name__ == "__main__":
    main()

