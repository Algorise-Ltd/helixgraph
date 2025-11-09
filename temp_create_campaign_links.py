
import pandas as pd

def create_campaign_po_links(input_path, output_path):
    try:
        po_df = pd.read_csv(input_path)
    except FileNotFoundError:
        print(f"Error: {input_path} not found.")
        return

    campaign_links = po_df[po_df['campaign_id'].notna()][['campaign_id', 'orderNumber']]
    
    # Rename orderNumber to po_id
    campaign_links = campaign_links.rename(columns={'orderNumber': 'po_id'})
    
    # Limit to 50-100 links as per sprint plan
    if len(campaign_links) > 100:
        campaign_links = campaign_links.sample(n=100, random_state=1)
    elif len(campaign_links) < 50:
        print(f"Warning: Only {len(campaign_links)} campaign links were found, which is less than the desired 50.")

    campaign_links.to_csv(output_path, index=False)
    print(f"Successfully created {output_path} with {len(campaign_links)} links.")

if __name__ == "__main__":
    input_csv_path = "data/raw/purchase_orders.csv"
    output_csv_path = "data/processed/campaign_po_links.csv"
    create_campaign_po_links(input_csv_path, output_csv_path)
