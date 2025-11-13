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