## Create Marketing Gazetteers & Dictionaries

**Context & Goal**

Comprehensive vocabularies of brands, channels, and campaigns that serve as both NER training data and entity linking dictionaries. These are the "building blocks" of marketing domain understanding.

**Requirements:**

Create 3 JSON dictionaries:

 **1. Brands Dictionary (** `data/dictionaries/marketing/brands.json`):

* 100+ brands across categories (Sports, Tech, Fashion, Food, etc.)
* Include aliases: "Nike" → ["Nike Inc", "NIKE", "Nike Corporation"]
* Add category tags for organization

Example:

```
[
  {
    "id": "BRAND_001",
    "name": "Nike",
    "aliases": ["Nike Inc", "NIKE", "Nike Corporation", "Nike Sportswear"],
    "category": "Sports Apparel",
    "country": "USA"
  },
  {
    "id": "BRAND_002",
    "name": "Adidas",
    "aliases": ["Adidas AG", "adidas", "ADIDAS"],
    "category": "Sports Apparel",
    "country": "Germany"
  }
]
```

 **2. Channels Dictionary (** `data/dictionaries/marketing/channels.json`):

* 10+ marketing channels with subcategories
* Include digital and traditional channels

Example:

```
[
  {
    "id": "CH_001",
    "name": "Social Media",
    "subcategories": ["Facebook", "Instagram", "TikTok", "LinkedIn", "Twitter", "YouTube"],
    "type": "Digital"
  },
  {
    "id": "CH_002",
    "name": "Email Marketing",
    "subcategories": ["Newsletter", "Promotional", "Transactional", "Drip Campaign"],
    "type": "Digital"
  },
  {
    "id": "CH_003",
    "name": "Display Advertising",
    "subcategories": ["Banner Ads", "Video Ads", "Native Ads"],
    "type": "Digital"
  }
]
```

 **3. Campaigns Dictionary (** `data/dictionaries/marketing/campaigns.json`):

* 30 realistic campaign names
* Include metadata: channel, objective, budget range

Example:

```
[
  {
    "id": "CAMP_001",
    "name": "Spring Launch 2024",
    "channel": "Social Media",
    "objective": "Awareness",
    "start_date": "2024-03-01",
    "end_date": "2024-05-31"
  }
]
```

Create Weak Supervision Patterns (`data/dictionaries/marketing/patterns.jsonl`

**Acceptance Criteria**

* 100+ brands with aliases
* 10+ channels with subcategories
* 30 campaigns with metadata
* Weak supervision patterns file
* All JSON files validated (no syntax errors)

## Generate Marketing Synthetic Data

**Context & Goal**

Realistic marketing and eCommerce datasets with proper conversion funnels and business relationships.

**Requirements:**

**1. Campaigns (30 campaigns):** Generate `data/processed/marketing/campaigns_v1.csv`:

```
import pandas as pd
import numpy as np
from faker import Faker

fake = Faker()

campaigns = []
for i in range(30):
    budget = np.random.lognormal(10, 0.8) * 1000  # $5K-$200K range
    impressions = int(budget * np.random.uniform(10, 30))  # CPM-based
    clicks = int(impressions * np.random.uniform(0.02, 0.08))  # 2-8% CTR
    conversions = int(clicks * np.random.uniform(0.01, 0.05))  # 1-5% conversion
    revenue = conversions * np.random.uniform(30, 200)  # $30-200 per order
  
    campaigns.append({
        'id': f'CAMP_{i+1:03d}',
        'name': f'{fake.word().title()} {fake.word().title()} 2024',
        'channel': random.choice(['Social Media', 'Email', 'Display', 'Search', 'TV']),
        'budget': round(budget, 2),
        'start_date': fake.date_between(start_date='-6m', end_date='today'),
        'end_date': fake.date_between(start_date='today', end_date='+3m'),
        'impressions': impressions,
        'clicks': clicks,
        'conversions': conversions,
        'revenue': round(revenue, 2)
    })

df = pd.DataFrame(campaigns)
df.to_csv('data/processed/marketing/campaigns_v1.csv', index=False)
```

**2. Products (200 products):** Generate `data/processed/marketing/products_v1.csv`

**3. Orders (500 orders):** Generate `data/processed/marketing/orders_v1.csv`:

* Link to campaigns and products
* Realistic order quantities and revenue
* Date within campaign period

**Acceptance Criteria**

* 30 campaigns with logical conversion funnels
* 200 products with realistic prices
* 500 orders linking campaigns to products
* All referential integrity valid
* Data validation passes

## Support Yixuan with NER Annotations

**Context & Goal**

150 annotated sentences focused on marketing entities to supplement Yixuan's training dataset.

**Requirements:**

* Create 150 sentences with realistic marketing language
* Focus on: CAMPAIGN, PRODUCT, BRAND, CHANNEL entities
* Include edge cases: SKUs, abbreviations, campaign codes
* Review 50 of Yixuan's annotations for consistency

**Example Sentences:**

```
sentences = [
    ("Nike's Spring Campaign on Instagram drove 50K clicks to Product SKU-4422.",
     [(0, 4, "BRAND"), (7, 22, "CAMPAIGN"), (26, 35, "CHANNEL"), (56, 65, "PRODUCT")]),
  
    ("The Q4 Initiative marketed Product Alpha via Email and generated $200K revenue.",
     [(4, 18, "CAMPAIGN"), (28, 41, "PRODUCT"), (46, 51, "CHANNEL")]),
]
```

**Acceptance Criteria**

* 150 marketing-focused sentences
* Mix of simple and complex sentences
* 20+ edge cases included
* Quality review completed
* Feedback document created

## Streamlit UI Development

**Context & Goal**

Complete Streamlit application structure with navigation, branding, and API integration.

**Requirements:**

Create `app/streamlit_app.py`

**Success Criteria:**

* App runs without errors
* Sidebar navigation works
* Branding applied (logo, colors)
* Graph stats displayed
* Both pages loadable:

```
# Load pages
if mode == "Fixed Queries":
    from pages import fixed_queries
    fixed_queries.show()
else:
    from pages import rag_chat
    rag_chat.show()
```

## Streamlit UI Development - Fixed Query View

**Context & Goal**

Interactive UI for executing predefined Cypher queries with visualizations.

Create `app/pages/fixed_queries.py`.

**Success Criteria:**

* All 4 queries selectable
* Parameters configurable
* Results display as tables
* At least 1 visualization
* Error handling works

## Streamlit UI Development - Implement RAG Chat Interface

**Context & Goal**

Conversational interface for RAG queries with chat history.

Create `app/pages/rag_chat.py`.

**Acceptance Criteria**

* Chat interface working
* Example questions clickable
* Chat history preserved
* Metadata displayed
* Error handling works

## Streamlit UI Development - Create Neo4j Bloom Visualizations

**Context & Goal**

Beautiful graph visualizations showing cross-domain relationships.

**Requirements:**

**Create 2 Bloom Perspectives:**

1. **Marketing View:**
   * Start with high-ROI campaigns
   * Color campaigns by channel
   * Size by revenue
   * Show: Campaign → Product → Order paths
2. **Procurement View:**
   * Start with high-spend suppliers
   * Color by risk score (green=low, red=high)
   * Size by total spend
   * Show: Supplier → PO → Campaign paths

**Steps:**

1. Open Neo4j Bloom
2. Create new perspective
3. Set color rules (by property)
4. Set size rules (by metric)
5. Save perspective
6. Take screenshots
7. Export perspective JSON

**Acceptance Criteria**

* 2 perspectives created and saved
* Colors applied meaningfully
* Sizes show importance
* Screenshots in `docs/bloom_screenshots/`
* Setup guide written
