# Procurement Data Generation Documentation

This document outlines the process for generating the procurement dataset using the `procurement_data_generator.py` script.

## 1. Data Generation

The main script for data generation is `procurement_data_generator.py`. It generates synthetic data for suppliers, products, purchase orders, and invoices. The script uses the Faker library and the Ollama model to generate realistic data.

### Execution

To run the data generation process, execute the following command from the root directory:

```bash
python data/raw/procurement_data_generator.py
```

This will generate the following files in the `data/raw` directory:

- `suppliers.csv`
- `products.csv`
- `purchase_orders.csv`
- `invoices.csv`
- `risks.csv`

### Purchase Order Generation Details

#### Marketing Campaign Integration

The script integrates marketing campaign data from `data/processed/marketing/campaigns_v1.csv` to generate realistic marketing-related purchase orders. 

- The linkage between campaigns and POs is based on the `ad_group_id`.
- The purchase order `description` is enriched with details from the campaign, such as `ad_group_id`, `media_platform`, `channel`, and `ad_placement`, to provide context for the Ollama model to assign a relevant L4 category.

#### Spend Balancing

A spend balancing mechanism is in place to ensure a realistic distribution of spend across the main L1 procurement categories. The target distribution is defined in the script and the process iteratively adds or removes POs to meet the targets. 

#### Supplier-Product Matching

1.  **Product-First Selection:** The process starts by selecting a product.
2.  **Hierarchical Search:** It then searches for a suitable supplier by matching the product's category against the supplier's category in a specific order:
    -   **L4 Match:** An exact match on the most specific category level (L4).
    -   **L3 Fallback:** If no L4 match is found, it searches for suppliers in the same L3 category.
    -   **L2 Fallback:** If still no match, it broadens the search to the L2 category.
3.  **New Supplier Generation:** If no suitable supplier is found even at the L2 level, a new supplier is generated on-the-fly with the correct category to fulfill the PO.

#### Contract Assignment

Contract assignment logic is supplier-centric:

-   Each supplier has a 70% chance of having a **Master Contract**.
-   When a PO is generated for a supplier with a Master Contract, there is a **90% chance** it will be assigned to that contract.
-   The remaining 10% of POs (and POs for suppliers without a master contract) may be assigned a random, one-off contract number.

#### Purchase Order Logic

- **Multi-line POs:** Approximately 10% of purchase orders are generated with multiple line items (between 2 and 4 lines) to simulate more complex orders.
- **Quantity Distribution:** The quantity for each PO line item is determined by its L1 category:
    - For 'Direct Materials' & 'Technical Materials', quantities follow a geometric distribution to simulate bulk orders.
    - For 'Indirect Services and Materials', the quantity is always 1.

## 2. Dictionary Creation

After the raw data is generated, the script automatically creates several JSON dictionary files in the `data/dictionaries/procurement` directory. These dictionaries are intended for entity linking and other downstream tasks.

The following dictionaries are created:

- `suppliers.json`: Contains a mapping of supplier legal names to their vendor codes and aliases.
- `pos.json`: Contains a mapping of purchase order numbers to their descriptions.
- `contracts.json`: Contains a list of unique contract references found in the purchase orders.

## 3. Data Integrity Check

Finally, after the data and dictionaries are generated, the script automatically runs a data integrity check using the `etl/procurement/procurement_data_integrity_checker.py` script.

This script performs the following checks:

- **Null Primary Keys:** Ensures that primary key columns in the generated files do not contain null values.
- **Referential Integrity:**
    - Verifies that all `supplierVendorCode` values in `purchase_orders.csv` exist in `suppliers.csv`.
    - Verifies that all `productSku` values in `purchase_orders.csv` exist in `products.csv`.
    - Verifies that all `po_id` values in `invoices.csv` exist in `purchase_orders.csv`.
- **Campaign PO Integrity:**
    - Verifies that all active/completed ad groups have at least one PO.
    - Verifies that campaign PO totals align with their budget/spend.
- **PO Total Integrity:**
    - Verifies that the sum of `(quantity * unitPrice)` for all line items of a purchase order equals the PO's total value.

The results of the integrity check are printed to the console.