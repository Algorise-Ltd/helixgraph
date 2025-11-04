import json
import ollama
from faker import Faker
import random
import pandas as pd
from math import floor
import os
import uuid
import re
from datetime import datetime, timedelta
from etl.procurement.risk_calculator import RiskCalculator

OLLAMA_MODEL = 'granite4:micro'
NUM_PRODUCTS = 100
NUM_PURCHASES = 400
NUM_SUPPLIERS = 200
APPEND_MODE = True
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
    with open(markdown_file, 'r') as f:
        content = f.read()

    categories = []
    current_l1 = None
    current_l2 = None
    current_l3 = None

    for line in content.split('\n'):
        l1_match = re.match(r'### L1: (.*)', line)
        l2_match = re.match(r'-   \*\*L2: (.*)\*\*', line)
        l3_match = re.match(r'    -   \*\*L3: (.*)\*\*', line)
        l4_match = re.match(r'        -   L4: (.*)', line)

        if l1_match:
            current_l1 = l1_match.group(1).strip()
        elif l2_match:
            current_l2 = l2_match.group(1).strip()
        elif l3_match:
            current_l3 = l3_match.group(1).strip()
        elif l4_match:
            l4_category = l4_match.group(1).strip()
            categories.append({
                'L1CategoryName': current_l1,
                'L2CategoryName': current_l2,
                'L3CategoryName': current_l3,
                'L4CategoryName': l4_category,
            })

    return categories

def generate_with_ollama(prompt):
    """
    Sends a prompt to the Ollama API and gets a response.
    """
    try:
        response = ollama.generate(model=OLLAMA_MODEL, prompt=prompt, stream=False)
        response_str = response.get('response', '')

        json_start = response_str.find('{')
        json_end = response_str.rfind('}') + 1

        if json_start != -1 and json_end != 0:
            json_str = response_str[json_start:json_end]
            return json.loads(json_str)
        else:
            return None

    except Exception as e:
        print(f"Error interacting with Ollama: {e}")
        return None

def generate_mitigation_plan(risk_type, risk_score):
    """
    Generates a realistic mitigation plan using Ollama based on risk type and score.
    """
    prompt = f"Generate a brief, one-sentence mitigation plan for a supplier risk of type '{risk_type}' with a score of {risk_score}. The plan should be actionable and concise. Output the result in JSON format with a single key: 'mitigation_plan'."
    
    mitigation_data = generate_with_ollama(prompt)
    
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

    for i in range(num_suppliers):
        country = country_list[i]
        locale = country_locales.get(country, 'en_US')
        fake = Faker(locale)
        raw_address = fake.address()
        # normalize multi-line addresses to a single-line string
        address = " ".join(line.strip() for line in raw_address.splitlines() if line.strip())
        print(f"Generating supplier {i+1}/{num_suppliers} for country: {country}...")

        prompt = f"Generate a realistic and unique supplier name and a contact person's full name for a company located at this address in {country}: {address}. Output the result in JSON format with keys: 'name', 'contact_person'."

        supplier_data = generate_with_ollama(prompt)

        if supplier_data:
            name = supplier_data.get('name') if isinstance(supplier_data.get('name'), str) else 'N/A'
            contact_person = supplier_data.get('contact_person') if isinstance(supplier_data.get('contact_person'), str) else 'N/A'

            suppliers.append({
                'vendorCode': f"SUP-{str(uuid.uuid4().hex)[:8]}",
                'legalName': name,
                'address': address,
                'country': country,
                'contactPerson': contact_person,
                'isActive': random.choices([True, False], weights=[0.9, 0.1], k=1)[0],
                'financialHealth': random.choices(['High', 'Medium', 'Low'], weights=[0.1, 0.3, 0.6], k=1)[0],
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
        
        product_data = generate_with_ollama(prompt)
        
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

def generate_purchase_orders(suppliers, products, num_pos=400):
    """
    Generates a list of synthetic purchase orders with multiple line items and cost centers.
    """
    fake = Faker()
    purchase_orders = []
    
    direct_products = [p for p in products if p['category_L1'] == 'Direct Materials']
    indirect_products = [p for p in products if p['category_L1'] == 'Indirect Services and Materials']
    technical_products = [p for p in products if p['category_L1'] == 'Technical Materials']

    for _ in range(num_pos):
        po_number = f"PO-{str(uuid.uuid4().hex)[:10]}"
        supplier = random.choice(suppliers)
        order_date = fake.date_time_between(start_date='-2y', end_date='now')
        num_items = random.randint(1, 5)
        cost_center = f"CC-{random.randint(100, 180)}"
        
        for item_num in range(1, num_items + 1):
            if random.random() < 0.7 and (direct_products or technical_products):
                product = random.choice(direct_products + technical_products)
            elif indirect_products:
                product = random.choice(indirect_products)
            else:
                product = random.choice(products) # Fallback

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

            purchase_orders.append({
                'orderNumber': po_number,
                'item': item_num,
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

        if first_po_item['orderStatus'] in ['Issued', 'Partially Received', 'Delivered', 'Closed']:
            num_invoices = random.randint(1, 3)
            invoice_amounts = [po_total_value / num_invoices] * num_invoices
            invoice_amounts = [max(0, amt + random.uniform(-amt*0.1, amt*0.1)) for amt in invoice_amounts]
            amount_diff = po_total_value - sum(invoice_amounts)
            invoice_amounts[-1] += amount_diff

            for amount in invoice_amounts:
                payment_terms_days = int(first_po_item['paymentTerms'].split(' ')[1])
                due_date = first_po_item['dateIssued'] + timedelta(days=payment_terms_days)
                
                # Realistic Status Logic
                status_flow = ['Received', 'Approved', 'Scheduled for Payment', 'Paid']
                is_rejected = random.random() < 0.05
                if is_rejected:
                    status = 'Rejected'
                else:
                    status = random.choice(status_flow)

                is_late = False
                if status == 'Paid':
                    if random.random() < 0.15:
                        is_late = True
                        payment_date = due_date + timedelta(days=random.randint(1, 45))
                    else:
                        payment_date = due_date - timedelta(days=random.randint(1, 15))
                elif status == 'Scheduled for Payment' and due_date < datetime.now():
                    status = 'Overdue'

                invoices.append({
                    'invoiceNumber': f"INV-{str(uuid.uuid4().hex)[:8]}",
                    'supplierReference': fake.ean(length=13),
                    'dateCreated': first_po_item['dateIssued'] + timedelta(days=random.randint(1, 5)),
                    'paymentDueDate': due_date,
                    'totalPaymentDue': round(amount, 2),
                    'paymentStatus': status,
                    'late_payment_flag': is_late,
                    'poOrderNumber': po_number,
                    'glAccount': f"GL-{random.randint(1000, 1200)}",
                    'costCenter': first_po_item['costCenter'],
                    'invoiceText': f"Invoice for PO {po_number}",
                    'postingDate': first_po_item['dateIssued'] + timedelta(days=random.randint(1, 10)),
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

    # 5. Balance Spend Distribution
    print("\n--- Balancing Spend Distribution ---")
    po_data = balance_spend_distribution(po_data, products_data, suppliers_data)

    # 6. Generate Invoices
    print("\n--- Generating Invoices ---")
    new_invoice_data = generate_invoices(new_po_data)
    invoice_data.extend(new_invoice_data)

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
from etl.procurement.procurement_data_integrity_checker import check_integrity
check_integrity()

print("\nData generation complete.")
