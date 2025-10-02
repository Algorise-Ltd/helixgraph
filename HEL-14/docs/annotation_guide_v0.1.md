- # Annotation Guide v0.1 — Marketing & Product Performance (tailored)

  ## Purpose

  This guide specifies what to annotate in short example sentences derived from the Marketing & Product Performance dataset. The goal is to create a minimal starter set for NER and EL that covers the project domain: campaigns, products, channels, suppliers, invoices, and relevant roles/teams.

  ## Labels (primary)


  - **CAMPAIGN** — marketing campaign names (e.g., "Campaign Orion", "Q4 Promo")
  - **PRODUCT** — product name or SKU (e.g., "Product X123", "SKU-987")
  - **CHANNEL** — marketing channel (e.g., "Email", "Social", "Search", "Display")
  - **SUPPLIER** — supplier, vendor, or partner company (e.g., "BrightMart Ltd")
  - **INVOICE** — invoice identifiers (e.g., "INV-2041")
  - **PO** — purchase order identifiers (e.g., "PO-4491")
  - **ROLE** — job title mentioned in text (e.g., "Marketing Manager")
  - **TEAM** — organizational unit (e.g., "Growth Team", "Retail Ops")
  - **METRIC** (optional) — named KPIs if useful as entities (e.g., "CTR", "ROI", "Conversion Rate")

  ## Do annotate

  - Specific, named entities that refer to a concrete object/person/org (see label examples above).
  - Campaign names that are used as proper nouns, e.g., "Campaign Nova".
  - Product names and SKUs exactly as they appear in the dataset when they appear in a sentence.
  - Channel names when they indicate the marketing channel used.
  - Invoice / PO IDs when present in the text.

  ## Do NOT annotate

  - Generic words (e.g., "campaign", "product", "supplier") when not referring to a specific name.
  - Numbers that are not identifiers (e.g., 2025 as a year) unless they are an invoice or PO id.
  - Stopwords or phrases that don't add entity semantics.

  ## Examples (format: sentence → labeled spans)

  1. "Campaign Orion increased sales of Product P123 via the Email channel."

     - CAMPAIGN: Campaign Orion
     - PRODUCT: Product P123
     - CHANNEL: Email
  2. "Invoice INV-2041 was issued to BrightMart Ltd for Product P123."

     - INVOICE: INV-2041
     - SUPPLIER: BrightMart Ltd
     - PRODUCT: Product P123
  3. "The Social campaign 'Nova Blast' improved CTR for SKU-987."

     - CHANNEL: Social
     - CAMPAIGN: Nova Blast
     - PRODUCT: SKU-987
     - METRIC: CTR
  4. "PO PO-5678 billed by Supplier Acme Supplies for advertising spend."

     - PO: PO-5678
     - SUPPLIER: Acme Supplies

  ## Notes on span boundaries

  - Try to select the minimal span that uniquely identifies the entity (e.g., "BrightMart Ltd", not "BrightMart Ltd for Product").
  - When a campaign name includes words like "Campaign X", include the whole name (e.g., "Campaign Orion").
  - For product SKUs, include the full SKU token (e.g., "SKU-987").

  ## Conversion / Next steps

  - We will later convert these examples into spaCy training format (.spacy) using a conversion script.
  - Save plain-text sentences to `nlp/training_data/dev/examples_s0.txt` (one sentence per line).
  - Save JSONL with spans to `nlp/training_data/dev/examples_s0.jsonl` for automated conversion:
    - JSON schema per line: `{"text":"...","spans":[{"start":int,"end":int,"label":"PRODUCT"}, ...]}`

  ## Review & acceptance

  - At least **15** short sentences covering CAMPAIGN, PRODUCT, CHANNEL, and SUPPLIER.
  - Examples should include at least 2 occurrences of INVOICE/PO if dataset contains such IDs.
  - Push PR and request a quick review from a teammate (1–2 reviewers).

  # Annotation Guide v0.1 — Marketing & Product Performance (tailored)

  ## Purpose

  This guide specifies what to annotate in short example sentences derived from the Marketing & Product Performance dataset. The goal is to create a minimal starter set for NER and EL that covers the project domain: campaigns, products, channels, suppliers, invoices, and relevant roles/teams.

  ## Labels (primary)

  - **CAMPAIGN** — marketing campaign names (e.g., "Campaign Orion", "Q4 Promo")
  - **PRODUCT** — product name or SKU (e.g., "Product X123", "SKU-987")
  - **CHANNEL** — marketing channel (e.g., "Email", "Social", "Search", "Display")
  - **SUPPLIER** — supplier, vendor, or partner company (e.g., "BrightMart Ltd")
  - **INVOICE** — invoice identifiers (e.g., "INV-2041")
  - **PO** — purchase order identifiers (e.g., "PO-4491")
  - **ROLE** — job title mentioned in text (e.g., "Marketing Manager")
  - **TEAM** — organizational unit (e.g., "Growth Team", "Retail Ops")
  - **METRIC** (optional) — named KPIs if useful as entities (e.g., "CTR", "ROI", "Conversion Rate")

  ## Do annotate

  - Specific, named entities that refer to a concrete object/person/org (see label examples above).
  - Campaign names that are used as proper nouns, e.g., "Campaign Nova".
  - Product names and SKUs exactly as they appear in the dataset when they appear in a sentence.
  - Channel names when they indicate the marketing channel used.
  - Invoice / PO IDs when present in the text.

  ## Do NOT annotate

  - Generic words (e.g., "campaign", "product", "supplier") when not referring to a specific name.
  - Numbers that are not identifiers (e.g., 2025 as a year) unless they are an invoice or PO id.
  - Stopwords or phrases that don't add entity semantics.

  ## Examples (format: sentence → labeled spans)

  1. "Campaign Orion increased sales of Product P123 via the Email channel."

     - CAMPAIGN: Campaign Orion
     - PRODUCT: Product P123
     - CHANNEL: Email
  2. "Invoice INV-2041 was issued to BrightMart Ltd for Product P123."

     - INVOICE: INV-2041
     - SUPPLIER: BrightMart Ltd
     - PRODUCT: Product P123
  3. "The Social campaign 'Nova Blast' improved CTR for SKU-987."

     - CHANNEL: Social
     - CAMPAIGN: Nova Blast
     - PRODUCT: SKU-987
     - METRIC: CTR
  4. "PO PO-5678 billed by Supplier Acme Supplies for advertising spend."

     - PO: PO-5678
     - SUPPLIER: Acme Supplies

  ## Notes on span boundaries

  - Try to select the minimal span that uniquely identifies the entity (e.g., "BrightMart Ltd", not "BrightMart Ltd for Product").
  - When a campaign name includes words like "Campaign X", include the whole name (e.g., "Campaign Orion").
  - For product SKUs, include the full SKU token (e.g., "SKU-987").

  ## Conversion / Next steps

  - We will later convert these examples into spaCy training format (.spacy) using a conversion script.
  - Save plain-text sentences to `nlp/training_data/dev/examples_s0.txt` (one sentence per line).
  - Save JSONL with spans to `nlp/training_data/dev/examples_s0.jsonl` for automated conversion:
    - JSON schema per line: `{"text":"...","spans":[{"start":int,"end":int,"label":"PRODUCT"}, ...]}`

  ## Review & acceptance

  - At least **15** short sentences covering CAMPAIGN, PRODUCT, CHANNEL, and SUPPLIER.
  - Examples should include at least 2 occurrences of INVOICE/PO if dataset contains such IDs.
  - Push PR and request a quick review from a teammate (1–2 reviewers).
