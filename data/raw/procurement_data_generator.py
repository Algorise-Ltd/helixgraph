import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import json
from json import JSONDecodeError
import ollama
from faker import Faker
import random
import pandas as pd
from math import floor
import os
import uuid
import re
import ast
from datetime import datetime, timedelta
from etl.procurement.risk_calculator import RiskCalculator
from etl.procurement import procurement_data_integrity_checker
import numpy as np

OLLAMA_MODEL = 'granite4:micro'

NUM_PRODUCTS = 300
NUM_PURCHASES = 600
NUM_SUPPLIERS = 200
APPEND_MODE = False
OVER_REP_PERCENT = 50
UNDER_REP_PERCENT = 15


# --- Comprehensive country -> Faker locale mapping ---
country_locales = {
    # Western / Central Europe
    'Germany': 'de_DE', 'France': 'fr_FR', 'Italy': 'it_IT', 'United Kingdom': 'en_GB',
    'Spain': 'es_ES', 'Netherlands': 'nl_NL', 'Belgium': 'fr_BE', 'Austria': 'de_AT',
    'Switzerland': 'de_CH', 'Portugal': 'pt_PT', 'Ireland': 'en_IE', 'Luxembourg': 'fr_LU',
    'Denmark': 'da_DK', 'Norway': 'nb_NO', 'Sweden': 'sv_SE', 'Finland': 'fi_FI',
    'Poland': 'pl_PL', 'Czech Republic': 'cs_CZ', 'Slovakia': 'sk_SK', 'Hungary': 'hu_HU',
    'Romania': 'ro_RO', 'Bulgaria': 'bg_BG', 'Croatia': 'hr_HR', 'Slovenia': 'sl_SI',
    'Estonia': 'et_EE', 'Latvia': 'lv_LV', 'Lithuania': 'lt_LT', 'Greece': 'el_GR',

    # Americas
    'United States': 'en_US', 'Canada': 'en_CA', 'Mexico': 'es_MX', 'Brazil': 'pt_BR',
    'Argentina': 'es_AR', 'Chile': 'es_CL', 'Colombia': 'es_CO', 'Peru': 'es_',
    'Venezuela': 'es_VE', 'Uruguay': 'es_UY',

    # Asia & Oceania
    'China': 'zh_CN', 'Japan': 'ja_JP', 'South Korea': 'ko_KR', 'India': 'en_IN',
    'Indonesia': 'id_ID', 'Malaysia': 'ms_MY', 'Singapore': 'en_SG', 'Thailand': 'th_TH',
    'Vietnam': 'vi_VN', 'Philippines': 'en_PH', 'Pakistan': 'en_PK', 'Bangladesh': 'bn_BD',
    'Sri Lanka': 'si_LK', 'Australia': 'en_AU', 'New Zealand': 'en_NZ',

    # Middle East & North Africa / Africa
    'Turkey': 'tr_TR', 'Israel': 'he_IL', 'United Arab Emirates': 'ar_AE', 'Saudi Arabia': 'ar_SA',
    'Egypt': 'ar_EG', 'Morocco': 'fr_MA', 'Algeria': 'fr_DZ', 'Tunisia': 'fr_TN',
    'South Africa': 'en_ZA', 'Nigeria': 'en_NG', 'Kenya': 'en_KE', 'Ghana': 'en_GH'
}

# --- Region groups to build sampled countries with adjustable weights ---
domestic = ['Germany']

europe = [
    'France','Italy','United Kingdom','Spain','Netherlands','Belgium','Austria',
    'Switzerland','Portugal','Ireland','Denmark','Norway','Sweden','Finland','Poland',
    'Czech Republic','Slovakia','Hungary','Romania','Bulgaria','Croatia','Slovenia',
    'Estonia','Latvia','Lithuania','Greece','Luxembourg'
]

americas = [
    'United States','Canada','Mexico','Brazil','Argentina','Chile','Colombia','Peru',
    'Venezuela','Uruguay'
]

asia_oceania = [
    'China','Japan','South Korea','India','Indonesia','Malaysia','Singapore','Thailand',
    'Vietnam','Philippines','Pakistan','Bangladesh','Sri Lanka','Australia','New Zealand'
]

mena_africa = [
    'Turkey','Israel','United Arab Emirates','Saudi Arabia','Egypt','Morocco','Algeria',
    'Tunisia','South Africa','Nigeria','Kenya','Ghana'
]

region_shares = {
    'domestic': 0.60,
    'europe': 0.30,
    'americas': 0.07,
    'asia_oceania': 0.02,
    'mena_africa': 0.01
}

region_map = {
    'domestic': domestic,
    'europe': europe,
    'americas': americas,
    'asia_oceania': asia_oceania,
    'mena_africa': mena_africa
}

# --- explicit overrides for known-problem locales ---
explicit_overrides = {
    # country : preferred-fallback-locale
    'Peru': 'es_ES',            # es_PE often unsupported -> use es_ES
    'Norway': 'no_NO',          # nb_NO sometimes missing -> try no_NO
    'Tunisia': 'fr_FR',         # fr_TN unsupported -> use fr_FR (French)
    'Morocco': 'fr_FR',         # fr_MA sometimes unsupported -> use fr_FR
    'Algeria': 'fr_FR',         # fr_DZ -> fr_FR
    'United Arab Emirates': 'en_US',  # ar_AE may be missing -> fallback to en_US
    # add more country-specific fallbacks here if you see failures
}

def sanitize_country_locales(mapping, default_locale='en_US'):
    """
    Sanitize mapping by trying to instantiate Faker for each locale.
    Returns cleaned mapping and a report.
    """
    cleaned = {}
    report = {'unchanged': [], 'changed': [], 'forced_default': []}

    # helper to try a candidate locale
    def try_locale(candidate):
        try:
            Faker(candidate)
            return True
        except Exception:
            return False

    for country, orig_loc in mapping.items():
        chosen = None
        tried = []

        # 1) explicit override per-country (highest priority)
        override = explicit_overrides.get(country)
        if override:
            tried.append(('override', override))
            if try_locale(override):
                chosen = override

        # 2) build candidate list (if not chosen yet)
        if not chosen:
            candidates = []
            if orig_loc:
                candidates.append(orig_loc)

                # replace underscore/hyphen variations and common case variants
                if '-' in orig_loc:
                    candidates.append(orig_loc.replace('-', '_'))
                if '_' in orig_loc:
                    candidates.append(orig_loc.replace('_', '-'))
                candidates.append(orig_loc.lower())
                candidates.append(orig_loc.upper())

                # language-only (first segment before '_' or '-')
                lang = orig_loc.split('_')[0].split('-')[0]
                if lang and lang not in candidates:
                    candidates.append(lang)

                # language-specific common regional fallbacks
                lang_fallbacks = {
                    'es': ['es_ES', 'es'],
                    'pt': ['pt_BR', 'pt_PT', 'pt'],
                    'fr': ['fr_FR', 'fr_BE', 'fr_CA', 'fr'],
                    'no': ['no_NO', 'nb_NO'],
                    'nb': ['nb_NO', 'no_NO'],
                    'zh': ['zh_CN', 'zh_TW'],
                    'ar': ['ar_SA', 'ar_EG', 'ar'],
                    'en': ['en_US', 'en_GB', 'en'],
                    'de': ['de_DE', 'de_AT', 'de_CH'],
                    'it': ['it_IT'],
                    'pl': ['pl_PL'],
                }
                if lang in lang_fallbacks:
                    for c in lang_fallbacks[lang]:
                        if c not in candidates:
                            candidates.append(c)

            broad_fallbacks = ['en_US', 'en']
            for b in broad_fallbacks:
                if b not in candidates:
                    candidates.append(b)

            # try candidates in order
            for cand in candidates:
                tried.append(cand)
                if try_locale(cand):
                    chosen = cand
                    break

        # 3) if nothing worked, force default_locale
        if not chosen:
            tried.append(default_locale)
            chosen = default_locale
            report['forced_default'].append((country, orig_loc, tried))

        cleaned[country] = chosen
        if chosen == orig_loc:
            report['unchanged'].append((country, orig_loc))
        else:
            report['changed'].append((country, orig_loc, chosen, tried))


    print("Locale sanitization summary:")
    print(f"  total countries: {len(mapping)}")
    print(f"  unchanged: {len(report['unchanged'])}")
    print(f"  changed: {len(report['changed'])}")
    if report['changed']:
        print("  Changes:")
        for country, orig, new, tried in report['changed']:
            print(f"    - {country}: {orig} -> {new} (tried: {tried})")
    if report['forced_default']:
        print(f"  forced default for {len(report['forced_default'])} countries: {report['forced_default']}")

    return cleaned, report

def parse_categories(markdown_file):
    """
    Parses the category taxonomy from the markdown file.
    """
    taxonomy = parse_ontology_taxonomy(markdown_file)
    categories = []
    for l1, l2_dict in taxonomy.items():
        for l2, l3_dict in l2_dict.items():
            for l3, l4_list in l3_dict.items():
                for l4 in l4_list:
                    categories.append({
                        'L1CategoryName': l1,
                        'L2CategoryName': l2,
                        'L3CategoryName': l3,
                        'L4CategoryName': l4,
                    })
    return categories

def generate_with_ollama(prompt, system_message=None, retries=3):
    """
    Sends a prompt to the Ollama API and gets a response with retry mechanism.
    """
    for i in range(retries):
        try:
            messages = [{'role': 'user', 'content': prompt}]
            if system_message:
                messages.insert(0, {'role': 'system', 'content': system_message})
            
            response = ollama.chat(model=OLLAMA_MODEL, messages=messages)
            response_str = response['message']['content']

            try:
                # First, try to load as-is, assuming perfect JSON
                return json.loads(response_str)
            except json.JSONDecodeError:
                # If that fails, try to extract from markdown
                match = re.search(r"```json\n(.*)\n```", response_str, re.DOTALL)
                if match:
                    json_str = match.group(1)
                    try:
                        return json.loads(json_str)
                    except json.JSONDecodeError:
                        # Fall through to the next method if markdown extraction fails
                        pass
                
                # If still not parsed, try the ast.literal_eval trick
                try:
                    # Find the dict-like string
                    json_start = response_str.find('{')
                    json_end = response_str.rfind('}') + 1
                    if json_start != -1 and json_end != 0:
                        dict_str = response_str[json_start:json_end]
                        # ast.literal_eval can safely evaluate Python literals
                        return ast.literal_eval(dict_str)
                except (ValueError, SyntaxError):
                    print(f"Could not parse JSON from Ollama response, retrying... ({i+1}/{retries})")

        except Exception as e:
            print(f"Error interacting with Ollama: {e}, retrying... ({i+1}/{retries})")
            
    return None

def parse_ontology_taxonomy(markdown_file):
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()

    taxonomy = {}
    current_l1 = None
    current_l2 = None
    current_l3 = None

    for line in content.splitlines():
        if not line.strip():
            continue

        # Check for L1 header
        l1_match = re.match(r'### L1: (.*)', line.strip())
        if l1_match:
            current_l1 = l1_match.group(1).strip()
            taxonomy[current_l1] = {}
            current_l2 = None
            current_l3 = None
            continue

        # Check for L2 header
        l2_match = re.match(r'-\s+\*\*L2: (.*)\*\*', line.strip())
        if l2_match and current_l1:
            current_l2 = l2_match.group(1).strip()
            taxonomy[current_l1][current_l2] = {}
            current_l3 = None
            continue

        # Check for L3 header
        l3_match = re.match(r'-\s+\*\*L3: (.*)\*\*', line.strip())
        if l3_match and current_l1 and current_l2:
            current_l3 = l3_match.group(1).strip()
            taxonomy[current_l1][current_l2][current_l3] = []
            continue

        # Check for L4 item
        l4_match = re.match(r'-\s+L4: (.*)', line.strip())
        if l4_match and current_l1 and current_l2 and current_l3:
            l4_category = l4_match.group(1).strip()
            taxonomy[current_l1][current_l2][current_l3].append(l4_category)
            
    return taxonomy

def generate_mitigation_plan(risk_type, risk_score):
    """
    Generates a realistic mitigation plan using Ollama based on risk type and score.
    """
    prompt = f"Generate a brief, one-sentence mitigation plan for a supplier risk of type '{risk_type}' with a score of {risk_score}. The plan should be actionable and concise."
    system_message = "You are a helpful assistant that only outputs JSON. Your response should be a single JSON object with a single key 'mitigation_plan'."
    
    mitigation_data = generate_with_ollama(prompt, system_message=system_message)
    
    if mitigation_data and 'mitigation_plan' in mitigation_data:
        return mitigation_data['mitigation_plan']
    else:
        return "Develop a contingency plan." # Fallback

def generate_suppliers_with_ollama(num_suppliers):
    """
    Generates a list of synthetic suppliers using Ollama for realistic data.
    """
    # Compute quotas and integer floors
    quotas = {k: num_suppliers * v for k, v in region_shares.items()}
    floors = {k: floor(q) for k, q in quotas.items()}
    assigned = sum(floors.values())
    remainder = num_suppliers - assigned

    # Distribute remainder by largest fractional parts (deterministic ordering)
    fractional_parts = sorted(
        ((k, quotas[k] - floors[k]) for k in region_shares.keys()),
        key=lambda kv: (kv[1], kv[0]),
        reverse=True
    )
    region_counts = floors.copy()
    idx = 0
    while remainder > 0:
        key = fractional_parts[idx % len(fractional_parts)][0]
        region_counts[key] += 1
        remainder -= 1
        idx += 1

    # ---------- Build country_list using region country lists ----------
    country_list = []
    for region_key, count in region_counts.items():
        if count <= 0:
            continue
        choices_from = region_map.get(region_key)
        if not choices_from:
            raise KeyError(f"Unknown region key in region_map: {region_key}")
        country_list += random.choices(choices_from, k=count)

    # Last sanity: ensure length matches
    if len(country_list) != num_suppliers:
        # if rounding drifted (shouldn't), fix by trimming or padding with domestic
        if len(country_list) > num_suppliers:
            country_list = country_list[:num_suppliers]
        else:
            country_list += random.choices(domestic, k=(num_suppliers - len(country_list)))

    random.shuffle(country_list)

    suppliers = []

    # Parse the ontology to get the category taxonomy
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ontology_path = os.path.join(script_dir, '../../ontologies/procurement_v0.9.md')
    taxonomy = parse_ontology_taxonomy(ontology_path)

    # Define high-level category distribution from sprint plan
    high_level_categories = {
        "IT Services": 0.2,
        "Marketing & Sales": 0.15,
        "Office Supplies": 0.25,
        "Logistics": 0.15,
        "Consulting": 0.1,
        "Manufacturing": 0.15
    }

    # Map high-level categories to ontology structure
    category_mapping = {
        "IT Services": taxonomy.get("Indirect Services and Materials", {}).get("IT & Technology", {}),
        "Marketing & Sales": taxonomy.get("Indirect Services and Materials", {}).get("Marketing & Sales", {}),
        "Office Supplies": taxonomy.get("Indirect Services and Materials", {}).get("Facility Services", {}),
        "Logistics": taxonomy.get("Indirect Services and Materials", {}).get("Logistics", {}),
        "Consulting": taxonomy.get("Indirect Services and Materials", {}).get("Corporate & Professional Services", {}),
        "Manufacturing": {**taxonomy.get("Direct Materials", {}), **taxonomy.get("Technical Materials", {})}
    }

    def get_all_l4(sub_taxonomy):
        l4_list = []
        for key, value in sub_taxonomy.items():
            if isinstance(value, list):
                # This is an L3 -> [L4] mapping
                l4_list.extend(value)
            elif isinstance(value, dict):
                # This is an L2 -> {L3 -> [L4]} mapping
                for l3, l4_items in value.items():
                    l4_list.extend(l4_items)
        return l4_list

    for i in range(num_suppliers):
        country = country_list[i]
        locale = country_locales.get(country, 'en_US')
        fake = Faker(locale)
        raw_address = fake.address()
        # normalize multi-line addresses to a single-line string
        address = " ".join(line.strip() for line in raw_address.splitlines() if line.strip())
        
        # Select a high-level category
        high_level_cat = random.choices(list(high_level_categories.keys()), weights=list(high_level_categories.values()), k=1)[0]
        
        # Get all L4 categories for the selected high-level category
        l4_pool = get_all_l4(category_mapping.get(high_level_cat, {}))
        
        if not l4_pool:
            # Fallback to a random L4 category if the mapping is empty
            all_l4 = get_all_l4(taxonomy.get("Indirect Services and Materials", {})) + get_all_l4(taxonomy.get("Direct Materials", {})) + get_all_l4(taxonomy.get("Technical Materials", {}))
            if not all_l4:
                category = "General" # Ultimate fallback
            else:
                category = random.choice(all_l4)
        else:
            category = random.choice(l4_pool)

        payment_terms = random.choice(['Net 30', 'Net 60', 'Net 90'])

        print(f"Generating supplier {i+1}/{num_suppliers} for country: {country}, category: {category}...")

        prompt = f"Generate a realistic and unique supplier name and a contact person's full name for a company that is a '{category}' supplier located at this address in {country}: {address}. Output the result in JSON format with keys: 'name', 'contact_person'."
        system_message = "You are a helpful assistant that only outputs JSON. Your response should be a single JSON object with keys 'name' and 'contact_person'."
        supplier_data = generate_with_ollama(prompt, system_message=system_message)

        if supplier_data:
            name = supplier_data.get('name') if isinstance(supplier_data.get('name'), str) else 'N/A'
            contact_person = supplier_data.get('contact_person') if isinstance(supplier_data.get('contact_person'), str) else 'N/A'

            suppliers.append({
                'vendorCode': f"SUP-{str(uuid.uuid4().hex)[:8]}",
                'legalName': name,
                'category': category,
                'address': address,
                'country': country,
                'contactPerson': contact_person,
                'isActive': random.choices([True, False], weights=[0.9, 0.1], k=1)[0],
                'financialHealth': random.choices(['High', 'Medium', 'Low'], weights=[0.1, 0.3, 0.6], k=1)[0],
                'paymentTerms': payment_terms,
            })
        else:
            print(f"Failed to generate data for supplier {i+1}.")

    return suppliers

def generate_products_with_ollama(categories, num_products=50):
    """
    Generates a list of synthetic products using Ollama, with specified category distribution.
    """
    products = []
    
    direct_materials = [c for c in categories if c['L1CategoryName'] == 'Direct Materials']
    technical_materials = [c for c in categories if c['L1CategoryName'] == 'Technical Materials']
    indirect_materials = [c for c in categories if c['L1CategoryName'] == 'Indirect Services and Materials']

    num_direct = int(num_products * 0.1)
    num_technical = int(num_products * 0.2)
    num_indirect = num_products - num_direct - num_technical

    for i in range(num_products):
        if i < num_direct and direct_materials:
            category = random.choice(direct_materials)
        elif i < num_direct + num_technical and technical_materials:
            category = random.choice(technical_materials)
        elif indirect_materials:
            category = random.choice(indirect_materials)
        else:
            category = random.choice(categories) # Fallback

        print(f"Generating product {i+1}/{num_products} for category: {category['L4CategoryName']}...")
        
        prompt = f"Generate a realistic product name and a brief, one-sentence description for a product in the category '{category['L4CategoryName']}'. Output the result in JSON format with keys: 'name', 'description'."
        system_message = "You are a helpful assistant that only outputs JSON. Your response should be a single JSON object with keys 'name' and 'description'."
        product_data = generate_with_ollama(prompt, system_message=system_message)
        
        if product_data:
            products.append({
                'sku': f"PROD-{str(uuid.uuid4().hex)[:6]}",
                'name': product_data.get('name'),
                'description': product_data.get('description'),
                'unitOfMeasure': random.choice(['Piece', 'KG', 'Box', 'Set']),
                'isCritical': random.choices([True, False], weights=[0.2, 0.8], k=1)[0],
                'category_L1': category['L1CategoryName'],
                'category_L2': category['L2CategoryName'],
                'category_L3': category['L3CategoryName'],
                'category_L4': category['L4CategoryName'],
            })
        else:
            print(f"Failed to generate data for product {i+1}.")
            
    return products

def generate_purchase_orders(suppliers, products, num_pos=600):
    """
    Generates a list of synthetic purchase orders with realistic distributions.
    """
    fake = Faker()
    purchase_orders = []

    # 1. Supplier-PO Relationship Distribution
    num_suppliers = len(suppliers)
    high_volume_suppliers = int(0.2 * num_suppliers)
    regular_suppliers = int(0.5 * num_suppliers)
    occasional_suppliers = num_suppliers - high_volume_suppliers - regular_suppliers

    shuffled_suppliers = random.sample(suppliers, k=num_suppliers)
    
    high_volume_pool = shuffled_suppliers[:high_volume_suppliers]
    regular_pool = shuffled_suppliers[high_volume_suppliers : high_volume_suppliers + regular_suppliers]
    occasional_pool = shuffled_suppliers[high_volume_suppliers + regular_suppliers :]

    # 2. Log-normal distribution for PO amounts
    amounts = np.random.lognormal(mean=10, sigma=1.5, size=num_pos)
    amounts = np.clip(amounts, 500, 150000)

    # 6. Campaign Linkage (using placeholder IDs)
    campaign_ids = [f"CAMP-{i:03d}" for i in range(1, 31)]
    
    for i in range(num_pos):
        # Select supplier based on distribution
        rand_val = random.random()
        if rand_val < 0.5 and high_volume_pool:
            supplier = random.choice(high_volume_pool)
        elif rand_val < 0.9 and regular_pool:
            supplier = random.choice(regular_pool)
        elif occasional_pool:
            supplier = random.choice(occasional_pool)
        else:
            supplier = random.choice(suppliers)


        # 3. Temporal Patterns for PO dates
        # Q4 spike (2x probability)
        month = random.choices(range(1, 13), weights=[1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2], k=1)[0]
        # Month-end clustering (last 5 days are 3x more likely)
        day_weights = [1]*25 + [3]*6
        day = random.choices(range(1, 32), weights=day_weights, k=1)[0]
        # Weekday bias (95% on weekdays)
        is_weekday = random.random() < 0.95
        
        year = random.choice([2023, 2024, 2025])
        
        try:
            if is_weekday:
                date_issued = fake.date_time_between(start_date=f"-{36-month}m", end_date="now").replace(year=year, month=month, day=day)
                while date_issued.weekday() >= 5:
                    date_issued -= timedelta(days=1)
            else:
                date_issued = fake.date_time_between(start_date=f"-{36-month}m", end_date="now").replace(year=year, month=month, day=day)
                while date_issued.weekday() < 5:
                    date_issued += timedelta(days=1)
        except ValueError:
            # Handle invalid date combinations like Feb 30
            day = min(day, 28)
            date_issued = fake.date_time_between(start_date=f"-{36-month}m", end_date="now").replace(year=year, month=month, day=day)


        # 4. Status Distribution
        if date_issued.year == 2025:
            status = random.choices(['completed', 'approved', 'pending', 'cancelled'], weights=[0.75, 0.15, 0.07, 0.03], k=1)[0]
            if status == 'pending' and (datetime.now() - date_issued).days > 30:
                status = 'approved' # Old pending POs should be approved
        else:
            status = 'completed' # POs from previous years are completed

        # 5. Delivery Date Distribution
        if date_issued.year == 2024:
            delivery_date = date_issued + timedelta(days=random.randint(30, 365))
            if delivery_date.year == 2024:
                delivery_date = delivery_date.replace(year=2025)
        else:
            delivery_date = date_issued + timedelta(days=random.randint(7, 60))

        # Campaign Linkage
        campaign_id = None
        if random.random() < 0.3:
            campaign_id = random.choice(campaign_ids)
            
        product = random.choice(products)

        purchase_orders.append({
            'orderNumber': f"PO-{str(uuid.uuid4().hex)[:10]}",
            'supplierVendorCode': supplier['vendorCode'],
            'orderTotalValue': round(amounts[i], 2),
            'dateIssued': date_issued,
            'orderStatus': status,
            'category': product['category_L4'],
            'campaign_id': campaign_id,
            'description': product['description'],
            'deliveryDate': delivery_date,
            'productSku': product['sku'],
            'quantity': 1, # Simplified to one line item per PO
            'unitPrice': round(amounts[i], 2),
            'item': 1,
            'dateChanged': date_issued + timedelta(days=random.randint(1, 30)),
            'approvedBy': fake.name(),
            'still_to_be_delivered_qty': 0,
            'still_to_be_delivered_value': 0,
            'still_to_be_invoiced_qty': 0,
            'still_to_be_invoiced_value': 0,
            'contractReference': f"CTR-{str(uuid.uuid4().hex)[:10]}" if random.random() < 0.3 else None,
            'paymentTerms': supplier['paymentTerms'],
            'requisitioner': fake.name(),
            'costCenter': f"CC-{random.randint(100, 180)}",
        })
        
    return purchase_orders

def generate_invoices(purchase_orders):
    """
    Generates a list of synthetic invoices with realistic status and amount logic.
    """
    fake = Faker()
    invoices = []
    po_groups = pd.DataFrame(purchase_orders).groupby('orderNumber')

    for po_number, po_items in po_groups:
        po_total_value = po_items['orderTotalValue'].sum()
        first_po_item = po_items.iloc[0]

        if first_po_item['orderStatus'] in ['completed', 'approved'] and random.random() < 0.9:
            num_invoices = random.randint(1, 3)
            invoice_amounts = [po_total_value / num_invoices] * num_invoices
            invoice_amounts = [max(0, amt + random.uniform(-amt*0.1, amt*0.1)) for amt in invoice_amounts]
            amount_diff = po_total_value - sum(invoice_amounts)
            if invoice_amounts:
                invoice_amounts[-1] += amount_diff

            for amount in invoice_amounts:
                payment_terms_days = int(first_po_item['paymentTerms'].split(' ')[1])
                issue_date = first_po_item['dateIssued'] + timedelta(days=random.randint(1, 5))
                due_date = issue_date + timedelta(days=payment_terms_days)
                
                paid_date = None
                is_late = False
                
                # Payment Status Realism: 80% on time, 15% paid late, 5% overdue
                rand_status = random.random()
                if rand_status < 0.8: # 80% paid on time
                    status = 'paid'
                    paid_date = due_date - timedelta(days=random.randint(1, 15))
                elif rand_status < 0.95: # 15% paid late
                    status = 'paid'
                    is_late = True
                    paid_date = due_date + timedelta(days=random.randint(1, 30))
                else: # 5% overdue
                    if datetime.now() > due_date:
                        status = 'overdue'
                    else:
                        status = 'pending' # If due date is in the future, it's pending

                invoices.append({
                    'invoiceNumber': f"INV-{str(uuid.uuid4().hex)[:8]}",
                    'po_id': po_number,
                    'amount': round(amount, 2),
                    'issue_date': issue_date.isoformat(),
                    'due_date': due_date.isoformat(),
                    'paid_date': paid_date.isoformat() if paid_date else None,
                    'status': status,
                    'late_payment_flag': is_late,
                    'supplierReference': fake.ean(length=13),
                    'glAccount': f"GL-{random.randint(1000, 1200)}",
                    'costCenter': first_po_item['costCenter'],
                    'invoiceText': f"Invoice for PO {po_number}",
                    'postingDate': issue_date + timedelta(days=random.randint(1, 10)),
                })
    return invoices

def generate_single_po_item(po_number, supplier, order_date, cost_center, product):
    """
    Generates a single purchase order item.
    """
    fake = Faker()
    quantity = random.randint(1, 100)
    unit_price = round(random.uniform(10, 1000), 2)
    delivery_date = order_date + timedelta(days=random.randint(7, 60))
    
    status = random.choices(['Draft', 'Pending Approval', 'Approved', 'Rejected', 'Issued', 'Partially Received', 'Delivered', 'Closed', 'Cancelled'], weights=[0.05, 0.05, 0.1, 0.05, 0.1, 0.1, 0.1, 0.4, 0.05], k=1)[0]
    if status in ['Draft', 'Pending Approval', 'Approved', 'Rejected', 'Cancelled']:
        still_to_be_delivered_qty = quantity
        still_to_be_invoiced_qty = quantity
    elif status in ['Issued', 'Partially Received']:
        still_to_be_delivered_qty = random.randint(0, quantity)
        still_to_be_invoiced_qty = random.randint(still_to_be_delivered_qty, quantity)
    else: # Delivered, Closed
        still_to_be_delivered_qty = 0
        still_to_be_invoiced_qty = random.randint(0, quantity)

    return {
        'orderNumber': po_number,
        'item': 1, # Assuming one item per new PO for simplicity
        'dateIssued': order_date,
        'dateChanged': order_date + timedelta(days=random.randint(1, 30)),
        'orderStatus': status,
        'orderTotalValue': quantity * unit_price,
        'approvedBy': fake.name(),
        'supplierVendorCode': supplier['vendorCode'],
        'productSku': product['sku'],
        'quantity': quantity,
        'unitPrice': unit_price,
        'deliveryDate': delivery_date,
        'still_to_be_delivered_qty': still_to_be_delivered_qty,
        'still_to_be_delivered_value': still_to_be_delivered_qty * unit_price,
        'still_to_be_invoiced_qty': still_to_be_invoiced_qty,
        'still_to_be_invoiced_value': still_to_be_invoiced_qty * unit_price,
        'contractReference': f"CTR-{str(uuid.uuid4().hex)[:10]}" if random.random() < 0.3 else None,
        'paymentTerms': random.choice(['Net 30', 'Net 60', 'Net 90']),
        'requisitioner': fake.name(),
        'costCenter': cost_center,
    }

def balance_spend_distribution(purchase_orders, products, suppliers, max_iterations=10):
    """
    Balances the spend distribution across main categories by adding or removing purchase orders.
    """
    po_df = pd.DataFrame(purchase_orders)
    products_df = pd.DataFrame(products)
    
    for i in range(max_iterations):
        merged_df = pd.merge(po_df, products_df, left_on='productSku', right_on='sku')
        total_spend = merged_df['orderTotalValue'].sum()
        if total_spend == 0:
            return po_df.to_dict('records')
            
        category_spend = merged_df.groupby('category_L1')['orderTotalValue'].sum()
        spend_distribution = (category_spend / total_spend) * 100
        
        print(f"\n--- Iteration {i+1}: Spend Distribution Check ---")
        print(spend_distribution)
        
        under_represented = spend_distribution[spend_distribution < UNDER_REP_PERCENT]
        over_represented = spend_distribution[spend_distribution > OVER_REP_PERCENT]
        
        if under_represented.empty and over_represented.empty:
            print("Spend distribution is within the desired range.")
            return po_df.to_dict('records')

        # Add POs for under-represented categories
        for category, percentage in under_represented.items():
            spend_needed = ((UNDER_REP_PERCENT/100) * total_spend) - category_spend.get(category, 0)
            products_in_cat = products_df[products_df['category_L1'] == category]
            if products_in_cat.empty:
                continue
            
            added_spend = 0
            while added_spend < spend_needed:
                product = products_in_cat.sample(1).iloc[0]
                supplier = random.choice(suppliers)
                fake = Faker()
                order_date = fake.date_time_between(start_date='-2y', end_date='now')
                po_number = f"PO-ADJ-{str(uuid.uuid4().hex)[:8]}"
                cost_center = f"CC-{random.randint(100, 180)}"
                
                new_po_item = generate_single_po_item(po_number, supplier, order_date, cost_center, product)
                
                po_df = pd.concat([po_df, pd.DataFrame([new_po_item])], ignore_index=True)
                added_spend += new_po_item['orderTotalValue']

        # Remove POs from over-represented categories
        for category, percentage in over_represented.items():
            spend_to_remove = category_spend[category] - ((OVER_REP_PERCENT/100) * total_spend)
            
            merged_df_for_removal = pd.merge(po_df, products_df, left_on='productSku', right_on='sku')
            pos_in_cat = merged_df_for_removal[merged_df_for_removal['category_L1'] == category]
            
            pos_to_remove = pos_in_cat.sort_values('orderTotalValue', ascending=True)
            
            removed_spend = 0
            for idx, po_to_remove in pos_to_remove.iterrows():
                if removed_spend >= spend_to_remove:
                    break
                
                order_number_to_remove = po_to_remove['orderNumber']
                
                po_spend = po_df[po_df['orderNumber'] == order_number_to_remove]['orderTotalValue'].sum()

                po_df = po_df[po_df['orderNumber'] != order_number_to_remove]
                removed_spend += po_spend

    print("Could not balance spend distribution within max iterations.")
    return po_df.to_dict('records')

if __name__ == '__main__':
    script_dir = os.path.dirname(os.path.abspath(__file__))
    ontology_path = os.path.join(script_dir, '../../ontologies/procurement_v0.9.md')
    country_locales, _locale_report = sanitize_country_locales(country_locales)

    suppliers_data = []
    products_data = []
    po_data = []
    invoice_data = []
    risks_data = []

    if APPEND_MODE:
        print("\n--- APPEND MODE ON: Loading existing data ---\n")
        try:
            suppliers_data = pd.read_csv(os.path.join(script_dir, 'suppliers.csv')).to_dict('records')
            print(f"Loaded {len(suppliers_data)} existing suppliers.")
        except FileNotFoundError:
            print("No existing suppliers.csv found.")
            pass
        try:
            products_data = pd.read_csv(os.path.join(script_dir, 'products.csv')).to_dict('records')
            print(f"Loaded {len(products_data)} existing products.")
        except FileNotFoundError:
            print("No existing products.csv found.")
            pass
        try:
            po_data = pd.read_csv(os.path.join(script_dir, 'purchase_orders.csv')).to_dict('records')
            print(f"Loaded {len(po_data)} existing purchase orders.")
        except FileNotFoundError:
            print("No existing purchase_orders.csv found.")
            pass
        try:
            invoice_data = pd.read_csv(os.path.join(script_dir, 'invoices.csv')).to_dict('records')
            print(f"Loaded {len(invoice_data)} existing invoices.")
        except FileNotFoundError:
            print("No existing invoices.csv found.")
            pass

    # 1. Parse Categories
    categories = parse_categories(ontology_path)

    # 2. Generate Products
    print("\n--- Generating Products ---")
    new_products_data = generate_products_with_ollama(categories, NUM_PRODUCTS)
    products_data.extend(new_products_data)

    # 3. Generate Suppliers
    print("--- Generating Suppliers ---")
    new_suppliers_data = generate_suppliers_with_ollama(NUM_SUPPLIERS)
    suppliers_data.extend(new_suppliers_data)

    # 4. Generate Purchase Orders
    print("\n--- Generating Purchase Orders ---")
    new_po_data = generate_purchase_orders(suppliers_data, products_data, NUM_PURCHASES)
    po_data.extend(new_po_data)

    # Calculate last annual revenue from POs
    print("\n--- Calculating Last Annual Revenue for Suppliers ---")
    po_df_for_revenue = pd.DataFrame(po_data)
    current_year = datetime.now().year
    previous_year = current_year - 1
    
    # Ensure 'dateIssued' is in datetime format
    po_df_for_revenue['dateIssued'] = pd.to_datetime(po_df_for_revenue['dateIssued'])
    
    previous_year_pos = po_df_for_revenue[po_df_for_revenue['dateIssued'].dt.year == previous_year]
    
    supplier_spend = previous_year_pos.groupby('supplierVendorCode')['orderTotalValue'].sum().to_dict()

    for supplier in suppliers_data:
        supplier['lastAnnualRevenue'] = supplier_spend.get(supplier['vendorCode'], 0)

    # 5. Balance Spend Distribution
    print("\n--- Balancing Spend Distribution ---")
    po_data = balance_spend_distribution(po_data, products_data, suppliers_data)

    # 6. Generate Invoices
    print("\n--- Generating Invoices ---")
    invoice_data.extend(generate_invoices(po_data))

    # 7. Calculate Risk Score
    print("\n--- Calculating Risk Scores ---")
    country_risk_map = {}
    # default by region
    for c in europe:
        country_risk_map[c] = 'Low Risk'  # many EU/EEA countries -> Low
    for c in americas:
        # treat US/Canada as Low, some LATAM as Medium
        if c in ('United States', 'Canada'):
            country_risk_map[c] = 'Low Risk'
        else:
            country_risk_map[c] = 'Medium Risk'
    for c in asia_oceania:
        # mix: China/India/Indonesia/Pakistan/Bangladesh -> High; others Medium/Low
        if c in ('China', 'India', 'Indonesia', 'Pakistan', 'Bangladesh'):
            country_risk_map[c] = 'High Risk'
        elif c in ('Japan','South Korea','Singapore','Australia','New Zealand'):
            country_risk_map[c] = 'Low Risk'
        else:
            country_risk_map[c] = 'Medium Risk'
    for c in mena_africa:
        # assign Medium or High for many; South Africa Medium, Gulf Low/Medium depending
        if c in ('United Arab Emirates','Israel','Turkey'):
            country_risk_map[c] = 'Medium Risk'
        elif c in ('South Africa','Morocco'):
            country_risk_map[c] = 'Medium Risk'
        else:
            country_risk_map[c] = 'High Risk'

    # Ensure every key in country_locales has an entry in country_risk_map (add missing as Medium Risk)
    for country in country_locales:
        if country not in country_risk_map:
            country_risk_map[country] = 'Medium Risk'

    risk_calculator = RiskCalculator(country_risk_map, company_total_spend=sum(po['orderTotalValue'] for po in po_data))

    # Calculate total spend per critical item
    po_df = pd.DataFrame(po_data)
    products_df = pd.DataFrame(products_data)
    suppliers_df = pd.DataFrame(suppliers_data)

    critical_products = products_df[products_df['isCritical']]
    merged_df = pd.merge(po_df, critical_products, left_on='productSku', right_on='sku')
    total_item_spend = merged_df.groupby('productSku')['orderTotalValue'].sum().to_dict()

    for i, supplier in suppliers_df.iterrows():
        supplier_pos = po_df[po_df['supplierVendorCode'] == supplier['vendorCode']]
        supplier_critical_items = pd.merge(supplier_pos, critical_products, left_on='productSku', right_on='sku')
        
        critical_items_for_risk_calc = []
        if not supplier_critical_items.empty:
            for sku, group in supplier_critical_items.groupby('productSku'):
                supplier_spend_for_item = group['orderTotalValue'].sum()
                total_spend_for_item = total_item_spend.get(sku, 0)
                critical_items_for_risk_calc.append({
                    'supplier_spend': supplier_spend_for_item,
                    'total_item_spend': total_spend_for_item
                })

        supplier_risk_data = {
            'country': supplier['country'],
            'financial_health_status': supplier['financialHealth'],
            'total_spend': supplier_pos['orderTotalValue'].sum(),
            'critical_items': critical_items_for_risk_calc
        }
        risk_scores = risk_calculator.calculate_supplier_risk(supplier_risk_data)
        suppliers_df.at[i, 'riskScore'] = risk_scores['total_risk']
        
        for risk_type, risk_value in risk_scores.items():
            if risk_type != 'total_risk':
                mitigation_plan = generate_mitigation_plan(risk_type, risk_value)
                risks_data.append({
                    'riskId': f"RISK-{str(uuid.uuid4().hex)[:8]}",
                    'supplierVendorCode': supplier['vendorCode'],
                    'riskType': risk_type.replace('_', ' ').title(),
                    'riskScore': risk_value,
                    'riskDescription': f'{risk_type.replace("_", " ").title()} for supplier {supplier['vendorCode']} is {risk_value}.',
                    'mitigationPlan': mitigation_plan,
                    'riskStatus': 'Active'
                })

    # 8. Save DataFrames
    if not suppliers_df.empty:
        suppliers_df.to_csv(os.path.join(script_dir, 'suppliers.csv'), index=False)
        print(f"Successfully generated and saved {len(suppliers_df)} suppliers.")
    if not products_df.empty:
        products_df.to_csv(os.path.join(script_dir, 'products.csv'), index=False)
        print(f"Successfully generated and saved {len(products_df)} products.")
    if not po_df.empty:
        po_df.to_csv(os.path.join(script_dir, 'purchase_orders.csv'), index=False)
        print(f"Successfully generated and saved {len(po_df)} purchase orders.")
    if invoice_data:
        invoice_df = pd.DataFrame(invoice_data)
        invoice_df.to_csv(os.path.join(script_dir, 'invoices.csv'), index=False)
        print(f"Successfully generated and saved {len(invoice_data)} invoices.")
    if risks_data:
        risks_df = pd.DataFrame(risks_data)
        risks_df.to_csv(os.path.join(script_dir, 'risks.csv'), index=False)
        print(f"Successfully generated and saved {len(risks_df)} risks.")

print("\n--- Running Data Integrity Check ---")

procurement_data_integrity_checker.check_data_integrity()

print("\nData generation complete.")
