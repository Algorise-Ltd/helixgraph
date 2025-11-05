
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

The results of the integrity check are printed to the console.
