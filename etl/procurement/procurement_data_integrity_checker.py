import pandas as pd
import os

def check_data_integrity():
    """
    Validates the integrity of foreign key linkages in the generated dataset.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, '../../data/raw')

    try:
        suppliers_df = pd.read_csv(os.path.join(data_dir, 'suppliers.csv'))
        products_df = pd.read_csv(os.path.join(data_dir, 'products.csv'))
        po_df = pd.read_csv(os.path.join(data_dir, 'purchase_orders.csv'))
        invoices_df = pd.read_csv(os.path.join(data_dir, 'invoices.csv'))
    except FileNotFoundError as e:
        print(f"Error loading data files: {e}")
        return

    print("--- Starting Data Integrity Checks ---")

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
    po_products = set(po_df['productSku'].unique())
    all_products = set(products_df['sku'].unique())
    missing_products = po_products - all_products

    if not missing_products:
        print("(PASSED) Check 2: All productSkus in Purchase Orders exist in Products.")
    else:
        print(f"(FAILED) Check 2: Found {len(missing_products)} productSkus in Purchase Orders that are not in Products.")
        print("Missing productSkus:", missing_products)

    # Check 3: Every poOrderNumber in Invoices exists in Purchase Orders
    inv_pos = set(invoices_df['poOrderNumber'].unique())
    all_pos = set(po_df['orderNumber'].unique())
    missing_pos = inv_pos - all_pos

    if not missing_pos:
        print("(PASSED) Check 3: All poOrderNumbers in Invoices exist in Purchase Orders.")
    else:
        print(f"(FAILED) Check 3: Found {len(missing_pos)} poOrderNumbers in Invoices that are not in Purchase Orders.")
        print("Missing poOrderNumbers:", missing_pos)

    print("\n--- Data Integrity Checks Complete ---")

if __name__ == '__main__':
    check_data_integrity()
