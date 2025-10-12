## Sprint Plan: Procurement Ontology, Data Generation, and Risk Models

This plan focuses on iterating the existing Procurement Ontology v0.1 to v0.9, developing a baseline risk model, and generating the necessary synthetic datasets.

----------

## Next Steps 🚀

### 1. Finalize Risk Score Calculation

-   **Action:** Update the risk score calculation in `generate_with_ollama.py` to use the actual generated transactional data instead of dummy data for `critical_items`.
-   **Method:**
    -   After generating all the data (suppliers, products, POs), calculate the `critical_items` for each supplier.
    -   This involves identifying which products are critical, finding the POs for those products for each supplier, and then calculating the supplier's spend vs. the total category spend for each critical item.
    -   The following code snippet shows the planned implementation for this logic within the main execution block of the script:

    ```python
    # Calculate total spend per category for critical items
    po_df = pd.DataFrame(po_data)
    products_df = pd.DataFrame(products_data)
    suppliers_df = pd.DataFrame(suppliers_data)

    critical_products = products_df[products_df['isCritical']]
    merged_df = pd.merge(po_df, critical_products, left_on='productSku', right_on='sku')
    total_category_spend = merged_df.groupby('category_L4')['orderTotalValue'].sum().to_dict()

    for i, supplier in suppliers_df.iterrows():
        supplier_pos = po_df[po_df['supplierVendorCode'] == supplier['vendorCode']]
        supplier_critical_items = pd.merge(supplier_pos, critical_products, left_on='productSku', right_on='sku')
        
        critical_items_for_risk_calc = []
        if not supplier_critical_items.empty:
            for category, group in supplier_critical_items.groupby('category_L4'):
                supplier_spend_in_cat = group['orderTotalValue'].sum()
                total_spend_in_cat = total_category_spend.get(category, 0)
                critical_items_for_risk_calc.append({
                    'supplier_spend': supplier_spend_in_cat,
                    'total_category_spend': total_spend_in_cat
                })

        supplier_risk_data = {
            'country': supplier['country'],
            'financial_health_status': supplier['financialHealth'],
            'total_spend': supplier_pos['orderTotalValue'].sum(),
            'critical_items': critical_items_for_risk_calc
        }
        suppliers_df.at[i, 'riskScore'] = risk_calculator.calculate_supplier_risk(supplier_risk_data)
    ```

### 2. Improve Spend Distribution Logic

-   **Action:** Update the `check_spend_distribution` function to be more efficient.
-   **Method:** Instead of restarting the entire data generation process if the spend distribution is not met, the function should intelligently add more POs for the underrepresented categories or remove some from the overrepresented ones until the balance is achieved.

### 3. Implement Append Mode for Data Generation

-   **Action:** Add a global variable (e.g., `APPEND_MODE = True/False`) to the data generation scripts.
-   **Method:** When `APPEND_MODE` is `True`, the script should read the existing CSV files, and append the newly generated data to them instead of overwriting. This will require adding logic to read the existing data at the beginning of the script.

### 4. Data Integrity Checks

-   **Action:** Validate the integrity of the foreign key linkages in the generated dataset.
-   **Checks:**
    -   Every `supplierVendorCode` in the Purchase Orders dataset exists in the Suppliers dataset.
    -   Every `productSku` in the Purchase Orders dataset exists in the Products dataset.
    -   Every `poOrderNumber` in the Invoices dataset exists in the Purchase Orders dataset.

### 5. Final Documentation

-   **Action:** Collate all deliverables into a single documentation package.
-   **Contents:**
    -   Final **Ontology v0.9** schema and definitions.
    -   The multi-level **Category Taxonomy**.
    -   The **Risk Scoring Model** logic and code.
    -   Summary statistics of the generated datasets.