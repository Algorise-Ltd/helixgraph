"""Generate synthetic procurement dataset aligned with procurement_schema."""
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

from schemas.procurement_schema import (
    ProcurementDataset,
    Supplier,
    SupplierTier,
    Contract,
    RiskScore,
    RiskCategory,
    PurchaseOrder,
    PurchaseOrderLine,
    Currency,
)


faker = Faker("en_GB")
random.seed(1234)
Faker.seed(1234)


def build_suppliers(count: int = 150) -> List[Supplier]:
    industries = [
        "Electronics",
        "Metals",
        "Chemicals",
        "Logistics",
        "Packaging",
        "IT Services",
        "Consulting",
        "Raw Materials",
        "Components",
        "Facilities",
    ]
    tiers = list(SupplierTier)

    suppliers = []
    for idx in range(1, count + 1):
        suppliers.append(
            Supplier(
                supplier_id=f"SUP-{idx:04d}",
                name=faker.company(),
                country=faker.country_code(representation="alpha-2"),
                industry=random.choice(industries),
                tier=random.choice(tiers),
                onboarding_date=faker.date_between(start_date="-8y", end_date="-30d"),
            )
        )
    return suppliers


def build_contracts(suppliers: List[Supplier]) -> List[Contract]:
    contracts: List[Contract] = []
    categories = [
        "PCB Assembly",
        "Machining",
        "Logistics",
        "Consulting",
        "Software Licenses",
        "Facility Services",
        "Packaging",
        "Steel Raw Materials",
        "Injection Molding",
        "3D Printing",
    ]

    for supplier in suppliers:
        contract_count = random.randint(1, 3)
        for _ in range(contract_count):
            start_date = faker.date_between(start_date="-3y", end_date="-60d")
            end_date = None if random.random() < 0.25 else faker.date_between(start_date="today", end_date="+2y")
            value = random.uniform(150000, 5000000)
            contracts.append(
                Contract(
                    contract_id=f"CON-{len(contracts)+1:05d}",
                    supplier_id=supplier.supplier_id,
                    category=random.choice(categories),
                    start_date=start_date,
                    end_date=end_date,
                    value=round(value, 2),
                    currency=Currency.EUR,
                )
            )
    return contracts


def build_risk_scores(suppliers: List[Supplier]) -> List[RiskScore]:
    risk_scores: List[RiskScore] = []
    for supplier in suppliers:
        categories = random.sample(list(RiskCategory), k=random.randint(2, len(RiskCategory)))
        for category in categories:
            score = random.uniform(45.0, 95.0)
            notes = faker.sentence(nb_words=8)
            risk_scores.append(
                RiskScore(
                    supplier_id=supplier.supplier_id,
                    category=category,
                    score=round(score, 1),
                    assessed_date=faker.date_between(start_date="-120d", end_date="today"),
                    notes=notes,
                )
            )
    return risk_scores


def build_purchase_orders(
    suppliers: List[Supplier],
    contracts: List[Contract],
    avg_orders_per_supplier: int = 12,
) -> List[PurchaseOrder]:
    contracts_by_supplier = {}
    for contract in contracts:
        contracts_by_supplier.setdefault(contract.supplier_id, []).append(contract)

    purchase_orders: List[PurchaseOrder] = []
    for supplier in suppliers:
        supplier_contracts = contracts_by_supplier.get(supplier.supplier_id, [])
        if not supplier_contracts:
            continue

        order_count = max(3, int(random.gauss(avg_orders_per_supplier, 4)))
        for _ in range(order_count):
            issue_date = faker.date_between(start_date="-180d", end_date="today")
            delivery_date = issue_date + timedelta(days=random.randint(7, 60))
            status = random.choices(
                population=["Open", "Approved", "Delivered", "Closed"],
                weights=[0.3, 0.2, 0.3, 0.2],
                k=1,
            )[0]

            lines: List[PurchaseOrderLine] = []
            line_count = random.randint(1, 4)
            for line_idx in range(line_count):
                contract = random.choice(supplier_contracts)
                quantity = random.uniform(5, 5000)
                unit_price = random.uniform(20, 3500)
                lines.append(
                    PurchaseOrderLine(
                        line_id=f"POL-{len(purchase_orders)+1:05d}-{line_idx+1}",
                        contract_id=contract.contract_id,
                        product_category=contract.category,
                        quantity=round(quantity, 2),
                        unit_price=round(unit_price, 2),
                        currency=Currency.EUR,
                    )
                )

            purchase_orders.append(
                PurchaseOrder(
                    po_id=f"PO-{len(purchase_orders)+1:05d}",
                    supplier_id=supplier.supplier_id,
                    issue_date=issue_date,
                    expected_delivery_date=delivery_date,
                    status=status,
                    lines=lines,
                )
            )

    return purchase_orders


def generate_dataset() -> ProcurementDataset:
    suppliers = build_suppliers()
    contracts = build_contracts(suppliers)
    risk_scores = build_risk_scores(suppliers)
    purchase_orders = build_purchase_orders(suppliers, contracts)
    return ProcurementDataset(
        suppliers=suppliers,
        contracts=contracts,
        risk_scores=risk_scores,
        purchase_orders=purchase_orders,
    )


def main():
    dataset = generate_dataset()
    output_path = Path("data/procurement/procurement_data.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(dataset.model_dump(mode="json"), f, indent=2, ensure_ascii=False)
    print(
        "Generated procurement dataset with "
        f"{len(dataset.suppliers)} suppliers and {len(dataset.purchase_orders)} purchase orders "
        f"-> {output_path}"
    )


if __name__ == "__main__":
    main()

