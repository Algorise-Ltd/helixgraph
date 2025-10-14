"""Marketing Loader - loads marketing campaign data into Neo4j."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Any, Optional

from etl.base_loader import BaseLoader
from etl.utils import setup_file_logger, get_project_root
from schemas.marketing_schema import (
    MarketingDataset,
    Campaign,
    CampaignChannel,
    CampaignChannelKPI,
    CampaignOrder,
)


class MarketingLoader(BaseLoader):
    """Domain loader for marketing campaigns, channels, KPIs, and orders."""

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str = "neo4j",
        batch_size: int = 500,
        data_file: Optional[str] = None,
        log_file: Optional[str] = None,
    ):
        if log_file is None:
            log_file = str(get_project_root() / "logs" / "marketing_load.log")
        logger = setup_file_logger("MarketingLoader", log_file)

        super().__init__(uri, user, password, database, batch_size, logger)

        if data_file is None:
            data_file = str(get_project_root() / "data" / "marketing" / "marketing_data.json")
        self.data_file = Path(data_file)
        self.dataset: Optional[MarketingDataset] = None

    def setup_schema(self):
        self.logger.info("Setting up marketing schema constraints and indexes")

        constraints = [
            """CREATE CONSTRAINT marketing_campaign_id_unique IF NOT EXISTS
               FOR (c:MarketingCampaign) REQUIRE c.campaign_id IS UNIQUE""",
            """CREATE CONSTRAINT marketing_brand_id_unique IF NOT EXISTS
               FOR (b:Brand) REQUIRE b.brand_id IS UNIQUE""",
            """CREATE CONSTRAINT marketing_objective_id_unique IF NOT EXISTS
               FOR (o:MarketingObjective) REQUIRE o.objective_id IS UNIQUE""",
            """CREATE CONSTRAINT marketing_channel_id_unique IF NOT EXISTS
               FOR (ch:MarketingChannel) REQUIRE ch.channel_id IS UNIQUE""",
            """CREATE CONSTRAINT marketing_kpi_id_unique IF NOT EXISTS
               FOR (k:MarketingKPI) REQUIRE k.kpi_id IS UNIQUE""",
        ]
        for constraint in constraints:
            self.create_constraint(constraint)

        indexes = [
            """CREATE INDEX marketing_campaign_name IF NOT EXISTS
               FOR (c:MarketingCampaign) ON (c.name)""",
            """CREATE INDEX marketing_campaign_dates IF NOT EXISTS
               FOR (c:MarketingCampaign) ON (c.start_date, c.end_date)""",
            """CREATE INDEX marketing_channel_type IF NOT EXISTS
               FOR (ch:MarketingChannel) ON (ch.type)""",
            """CREATE INDEX marketing_kpi_name IF NOT EXISTS
               FOR (k:MarketingKPI) ON (k.name)""",
        ]
        for index in indexes:
            self.create_index(index)

    def load_data(self):
        self.logger.info(f"Loading marketing dataset from {self.data_file}")
        if not self.data_file.exists():
            raise FileNotFoundError(f"Marketing data file not found: {self.data_file}")

        with self.data_file.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        self.dataset = MarketingDataset(**raw)
        self.logger.info(
            "Loaded marketing dataset: %d campaigns, %d brands",
            len(self.dataset.campaigns),
            len(self.dataset.brands),
        )

    def load_brands(self):
        assert self.dataset is not None
        data = [brand.model_dump(mode="json") for brand in self.dataset.brands]

        cypher = """
            UNWIND $batch AS brand
            MERGE (b:Brand {brand_id: brand.brand_id})
            SET b.name = brand.name,
                b.category = brand.category,
                b.market = brand.market,
                b.created_at = datetime()
        """
        count = self.batch_load(data, cypher, batch_size=200)
        self.stats.add_nodes("Brand", count)

    def load_objectives(self):
        assert self.dataset is not None
        data = [obj.model_dump(mode="json") for obj in self.dataset.objectives]

        cypher = """
            UNWIND $batch AS objective
            MERGE (o:MarketingObjective {objective_id: objective.objective_id})
            SET o.name = objective.name,
                o.description = objective.description,
                o.created_at = datetime()
        """
        count = self.batch_load(data, cypher, batch_size=200)
        self.stats.add_nodes("MarketingObjective", count)

    def load_kpis(self):
        assert self.dataset is not None
        data = [kpi.model_dump(mode="json") for kpi in self.dataset.kpis]

        cypher = """
            UNWIND $batch AS kpi
            MERGE (k:MarketingKPI {kpi_id: kpi.kpi_id})
            SET k.name = kpi.name,
                k.description = kpi.description,
                k.unit = kpi.unit,
                k.direction = kpi.direction,
                k.created_at = datetime()
        """
        count = self.batch_load(data, cypher, batch_size=200)
        self.stats.add_nodes("MarketingKPI", count)

    def load_channels(self):
        assert self.dataset is not None
        data = [channel.model_dump(mode="json") for channel in self.dataset.channels]

        cypher = """
            UNWIND $batch AS channel
            MERGE (ch:MarketingChannel {channel_id: channel.channel_id})
            SET ch.name = channel.name,
                ch.type = channel.type,
                ch.created_at = datetime()
            WITH ch, channel
            WHERE channel.parent_id IS NOT NULL
            MATCH (parent:MarketingChannel {channel_id: channel.parent_id})
            MERGE (ch)-[r:SUB_CHANNEL_OF]->(parent)
            SET r.created_at = datetime()
        """
        count = self.batch_load(data, cypher, batch_size=200)
        self.stats.add_nodes("MarketingChannel", count)

    def load_campaigns(self):
        assert self.dataset is not None
        data = [campaign.model_dump(mode="json") for campaign in self.dataset.campaigns]

        cypher = """
            UNWIND $batch AS campaign
            MERGE (c:MarketingCampaign {campaign_id: campaign.campaign_id})
            SET c.name = campaign.name,
                c.region = campaign.region,
                c.start_date = date(campaign.start_date),
                c.end_date = date(campaign.end_date),
                c.budget = campaign.budget,
                c.currency = campaign.currency,
                c.created_at = datetime()
            WITH c, campaign
            MATCH (b:Brand {brand_id: campaign.brand_id})
            MERGE (c)-[r:FOR_BRAND]->(b)
            SET r.created_at = datetime()
            WITH c, campaign
            MATCH (o:MarketingObjective {objective_id: campaign.objective_id})
            MERGE (c)-[r2:HAS_OBJECTIVE]->(o)
            SET r2.created_at = datetime()
        """
        count = self.batch_load(data, cypher, batch_size=200)
        self.stats.add_nodes("MarketingCampaign", count)
        self.stats.add_relationships("FOR_BRAND", count)
        self.stats.add_relationships("HAS_OBJECTIVE", count)

    def load_campaign_channels(self):
        assert self.dataset is not None

        channel_records: List[Dict[str, Any]] = []
        kpi_records: List[Dict[str, Any]] = []

        for campaign in self.dataset.campaigns:
            for channel in campaign.channels:
                channel_records.append(
                    {
                        "campaign_id": campaign.campaign_id,
                        "channel_id": channel.channel_id,
                        "spend": channel.spend,
                        "currency": channel.currency,
                    }
                )
                for kpi in channel.kpis:
                    kpi_records.append(
                        {
                            "campaign_id": campaign.campaign_id,
                            "channel_id": channel.channel_id,
                            "kpi_id": kpi.kpi_id,
                            "value": kpi.value,
                            "unit": kpi.unit,
                            "period_start": kpi.period_start,
                            "period_end": kpi.period_end,
                        }
                    )

        cypher_channel = """
            UNWIND $batch AS record
            MATCH (c:MarketingCampaign {campaign_id: record.campaign_id})
            MATCH (ch:MarketingChannel {channel_id: record.channel_id})
            MERGE (c)-[r:ACTIVATED_ON]->(ch)
            SET r.spend = record.spend,
                r.currency = record.currency,
                r.created_at = datetime()
        """
        channel_count = self.batch_load(channel_records, cypher_channel, batch_size=500)
        self.stats.add_relationships("ACTIVATED_ON", channel_count)

        cypher_kpi = """
            UNWIND $batch AS record
            MATCH (c:MarketingCampaign {campaign_id: record.campaign_id})
            MATCH (ch:MarketingChannel {channel_id: record.channel_id})
            MATCH (k:MarketingKPI {kpi_id: record.kpi_id})
            MERGE (c)-[r:KPI_RESULT {kpi_id: record.kpi_id, channel_id: record.channel_id, period_start: record.period_start}]->(k)
            SET r.value = record.value,
                r.unit = record.unit,
                r.period_end = record.period_end,
                r.created_at = datetime(),
                r.source = "marketing_data"
        """
        kpi_count = self.batch_load(kpi_records, cypher_kpi, batch_size=1000)
        self.stats.add_relationships("KPI_RESULT", kpi_count)

    def load_orders(self):
        assert self.dataset is not None
        order_records: List[Dict[str, Any]] = []
        for campaign in self.dataset.campaigns:
            for order in campaign.orders:
                order_records.append(
                    {
                        "campaign_id": campaign.campaign_id,
                        "order_id": order.order_id,
                        "platform": order.platform,
                        "revenue": order.revenue,
                        "currency": order.currency,
                        "conversion_date": order.conversion_date,
                    }
                )

        cypher = """
            UNWIND $batch AS order
            MATCH (c:MarketingCampaign {campaign_id: order.campaign_id})
            MERGE (o:CommerceOrder {order_id: order.order_id})
            SET o.platform = order.platform,
                o.revenue = order.revenue,
                o.currency = order.currency,
                o.conversion_date = date(order.conversion_date),
                o.created_at = datetime()
            MERGE (o)-[r:ATTRIBUTED_TO]->(c)
            SET r.created_at = datetime(),
                r.source = "marketing_data"
        """
        count = self.batch_load(order_records, cypher, batch_size=500)
        self.stats.add_nodes("CommerceOrder", count)
        self.stats.add_relationships("ATTRIBUTED_TO", count)

    def load(self):
        self.logger.info("Starting marketing data load")
        try:
            self.load_data()
            self.setup_schema()
            self.load_brands()
            self.load_objectives()
            self.load_kpis()
            self.load_channels()
            self.load_campaigns()
            self.load_campaign_channels()
            self.load_orders()
            self.print_statistics()
            graph_stats = self.get_graph_statistics()
            self.logger.info(
                "Marketing graph totals: %d nodes, %d relationships",
                graph_stats["total_nodes"],
                graph_stats["total_relationships"],
            )
        except Exception as exc:  # pragma: no cover
            self.logger.error("Marketing load failed: %s", exc, exc_info=True)
            raise


def main():
    from etl.utils import get_neo4j_config

    config = get_neo4j_config()
    with MarketingLoader(
        uri=config["uri"],
        user=config["user"],
        password=config["password"],
    ) as loader:
        if not loader.test_connection():
            raise RuntimeError("Failed to connect to Neo4j")
        loader.load()


if __name__ == "__main__":
    main()
