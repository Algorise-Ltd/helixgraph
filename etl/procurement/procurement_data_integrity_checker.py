import pandas as pd
import os
import numpy as np

def check_campaign_po_integrity(campaigns_data_dir, procurement_data_dir):
    """
    Checks that active/completed campaigns have POs and that their spend aligns with the budget.
    """
    print("\n--- Checking Campaign PO Integrity ---")
    try:
        campaigns_df = pd.read_csv(os.path.join(campaigns_data_dir, 'campaigns_v1.csv'))
        po_df = pd.read_csv(os.path.join(procurement_data_dir, 'purchase_orders.csv'))
    except FileNotFoundError as e:
        print(f"Warning: Could not load campaign or PO files for integrity check: {e}")
        return

    # Clean column names
    campaigns_df.columns = campaigns_df.columns.str.strip()

    # Check for necessary columns
    if 'budget' not in campaigns_df.columns or 'actual_spend' not in campaigns_df.columns:
        print("(FAILED) Check 5: 'budget' or 'actual_spend' columns not found in campaigns_v1.csv.")
        return

    # Extract ad_group_id from PO description
    po_df['ad_group_id'] = po_df['description'].str.extract(r'Ad Group: ([A-Z0-9_]+)')
    
    # Filter for POs linked to campaigns
    campaign_po_df = po_df.dropna(subset=['ad_group_id'])

    # 1. Coverage Check
    active_completed_campaigns = campaigns_df[campaigns_df['status'].isin(['active', 'completed'])].copy()
    linked_ad_group_ids = set(campaign_po_df['ad_group_id'].unique())
    
    campaigns_with_no_pos = []
    for ad_group_id in active_completed_campaigns['ad_group_id'].unique():
        if ad_group_id not in linked_ad_group_ids:
            campaigns_with_no_pos.append(ad_group_id)

    if not campaigns_with_no_pos:
        print("(PASSED) Check 4: All active/completed ad groups have at least one PO.")
    else:
        print(f"(FAILED) Check 4: Found {len(campaigns_with_no_pos)} active/completed ad groups with no associated POs.")
        print("Ad groups with no POs:", campaigns_with_no_pos)

    # 2. Budget Check
    # First, create the cleaned columns on the slice
    active_completed_campaigns['budget_cleaned'] = pd.to_numeric(active_completed_campaigns['budget'].replace({r'[\$,]': ''}, regex=True), errors='coerce').fillna(0)
    active_completed_campaigns['spend_cleaned'] = pd.to_numeric(active_completed_campaigns['actual_spend'].replace({r'[\$,]': ''}, regex=True), errors='coerce').fillna(0)

    # Then, aggregate them by ad_group_id
    campaign_agg_df = active_completed_campaigns.groupby('ad_group_id').agg(
        budget_cleaned=('budget_cleaned', 'sum'),
        spend_cleaned=('spend_cleaned', 'sum')
    ).reset_index()

    # Calculate total PO value per ad_group_id
    po_spend_per_campaign = campaign_po_df.groupby('ad_group_id')['orderTotalValue'].sum().reset_index()
    
    merged_df = pd.merge(po_spend_per_campaign, campaign_agg_df, on='ad_group_id')
    
    budget_mismatches = []
    for index, row in merged_df.iterrows():
        target_spend = row['spend_cleaned'] if row['spend_cleaned'] > 0 else row['budget_cleaned']
        po_total = row['orderTotalValue']
        
        # Allow a small tolerance (e.g., 1%) for floating point inaccuracies
        if not np.isclose(target_spend, po_total, rtol=0.01):
            budget_mismatches.append({
                'ad_group_id': row['ad_group_id'],
                'expected_spend': target_spend,
                'actual_po_spend': po_total
            })

    if not budget_mismatches:
        print("(PASSED) Check 5: Campaign PO totals align with their budget/spend.")
    else:
        print(f"(FAILED) Check 5: Found {len(budget_mismatches)} campaigns where PO totals do not align with budget/spend.")
        for mismatch in budget_mismatches[:5]: # Print first 5 mismatches
            print(f"  - Ad Group {mismatch['ad_group_id']}: Expected ~${mismatch['expected_spend']:.2f}, Found PO Total ${mismatch['actual_po_spend']:.2f}")


def check_po_total_integrity(po_df):
    """
    Checks that for each PO, the sum of (quantity * unitPrice) for all lines equals the sum of orderTotalValue.
    """
    print("\n--- Checking PO Total Integrity ---")
    
    # Calculate the total value for each line
    po_df['calculated_line_total'] = po_df['quantity'] * po_df['unitPrice']
    
    # Group by PO number and sum the values
    po_grouped = po_df.groupby('orderNumber').agg(
        calculated_po_total=('calculated_line_total', 'sum'),
        actual_po_total=('orderTotalValue', 'sum')
    ).reset_index()
    
    # Find mismatches, allowing for a small tolerance
    mismatches = po_grouped[~np.isclose(po_grouped['calculated_po_total'], po_grouped['actual_po_total'], rtol=0.01)]
    
    if mismatches.empty:
        print("(PASSED) Check 6: All PO totals are correct.")
    else:
        print(f"(FAILED) Check 6: Found {len(mismatches)} POs where the sum of line totals does not equal the sum of orderTotalValue.")
        for index, row in mismatches.head().iterrows():
            print(f"  - PO {row['orderNumber']}: Expected ${row['calculated_po_total']:.2f}, Found ${row['actual_po_total']:.2f}")

def check_data_integrity():
    """
    Validates the integrity of the generated procurement dataset.
    Checks for null primary keys and validates foreign key linkages.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    procurement_data_dir = os.path.join(script_dir, '../../data/raw')
    campaigns_data_dir = os.path.join(script_dir, '../../data/processed/marketing')

    try:
        suppliers_df = pd.read_csv(os.path.join(procurement_data_dir, 'suppliers.csv'))
        products_df = pd.read_csv(os.path.join(procurement_data_dir, 'products.csv'))
        po_df = pd.read_csv(os.path.join(procurement_data_dir, 'purchase_orders.csv'))
        invoices_df = pd.read_csv(os.path.join(procurement_data_dir, 'invoices.csv'))
    except FileNotFoundError as e:
        print(f"Error loading data files: {e}")
        return

    print("--- Starting Data Integrity Checks ---")

    # --- Null Checks ---
    print("\n--- Checking for Null Primary Keys ---")
    if suppliers_df['vendorCode'].isnull().any():
        print("(FAILED) suppliers.csv contains null vendor codes.")
    else:
        print("(PASSED) suppliers.csv has no null vendor codes.")

    if po_df['orderNumber'].isnull().any():
        print("(FAILED) purchase_orders.csv contains null order numbers.")
    else:
        print("(PASSED) purchase_orders.csv has no null order numbers.")

    if invoices_df['invoiceNumber'].isnull().any():
        print("(FAILED) invoices.csv contains null invoice IDs.")
    else:
        print("(PASSED) invoices.csv has no null invoice IDs.")

    # --- Referential Integrity Checks ---
    print("\n--- Checking Referential Integrity ---")

    # Check 1: Every supplierVendorCode in Purchase Orders exists in Suppliers
    po_suppliers = set(po_df['supplierVendorCode'].unique())
    all_suppliers = set(suppliers_df['vendorCode'].unique())
    missing_suppliers = po_suppliers - all_suppliers

    if not missing_suppliers:
        print("(PASSED) Check 1: All supplierVendorCodes in Purchase Orders exist in Suppliers.")
    else:
        print(f"(FAILED) Check 1: Found {len(missing_suppliers)} supplierVendorCodes in Purchase Orders that are not in Suppliers.")
        print("Missing supplierVendorCodes:", missing_suppliers)

    # Check 2: Every productSku in Purchase Orders exists in Products
    po_products = set(po_df.dropna(subset=['productSku'])['productSku'].unique())
    all_products = set(products_df['sku'].unique())
    missing_products = po_products - all_products

    if not missing_products:
        print("(PASSED) Check 2: All productSkus in Purchase Orders exist in Products.")
    else:
        print(f"(FAILED) Check 2: Found {len(missing_products)} productSkus in Purchase Orders that are not in Products.")
        print("Missing productSkus:", missing_products)

    # Check 3: Every po_id in Invoices exists in Purchase Orders
    inv_pos = set(invoices_df.dropna(subset=['po_id'])['po_id'].unique())
    all_pos = set(po_df['orderNumber'].unique())
    missing_pos = inv_pos - all_pos

    if not missing_pos:
        print("(PASSED) Check 3: All po_ids in Invoices exist in Purchase Orders.")
    else:
        print(f"(FAILED) Check 3: Found {len(missing_pos)} po_ids in Invoices that are not in Purchase Orders.")
        print("Missing po_ids:", missing_pos)

    # --- Campaign PO Integrity Checks ---
    check_campaign_po_integrity(campaigns_data_dir, procurement_data_dir)

    # --- PO Total Integrity Check ---
    check_po_total_integrity(po_df)

    print("\n--- Data Integrity Checks Complete ---")

if __name__ == '__main__':
    check_data_integrity()
