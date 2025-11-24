#!/usr/bin/env python3
"""
Generate additional entities to meet HEL-21 Phase 2 targets.

Targets to fill:
- CAMPAIGN: 31 → 100 (need 69 more)
- ROLE: 24 → 100 (need 76 more)
- SKILL: 50 → 140 (need 90 more)
"""

import json
import random
from pathlib import Path


# Additional campaign templates
CAMPAIGN_TEMPLATES = [
    "{brand} {season} {action}",
    "{product} {event} {year}",
    "{brand} {product} Launch Campaign",
    "{event} {action} with {brand}",
    "{season} {product} Promotion",
    "{brand} {audience} Engagement Drive",
    "{product} {region} Rollout",
    "{brand} {metric} Optimization Campaign",
]

BRANDS = ["Nike", "Adidas", "Apple", "Samsung", "Nestle", "Coca-Cola", "Amazon", "Google", 
          "Microsoft", "Meta", "Tesla", "BMW", "Mercedes", "Toyota", "Honda"]

PRODUCTS = ["Sneakers", "Smartwatch", "Laptop", "Tablet", "Cereal", "Beverage", "Shoes",
            "Headphones", "Gaming Console", "Smart TV", "Fitness Tracker", "Electric Vehicle"]

SEASONS = ["Spring", "Summer", "Fall", "Winter", "Holiday", "Back-to-School", "Q1", "Q2", "Q3", "Q4"]

EVENTS = ["Black Friday", "Cyber Monday", "Prime Day", "Mother's Day", "Father's Day",
          "Valentine's Day", "Christmas", "New Year", "Easter", "Memorial Day"]

ACTIONS = ["Sale", "Launch", "Refresh", "Relaunch", "Revival", "Blitz", "Push", "Drive",
           "Initiative", "Boost", "Expansion", "Upgrade"]

AUDIENCES = ["Millennial", "Gen-Z", "Student", "Professional", "Family", "Senior",
             "Youth", "Premium", "Budget", "Eco-conscious"]

REGIONS = ["EMEA", "APAC", "North America", "Europe", "Asia", "US", "UK", "Germany", "France"]

METRICS = ["ROI", "ROAS", "Conversion", "Engagement", "Awareness", "Retention"]


# Additional role titles
ROLE_TITLES = [
    # Executive
    "Chief Executive Officer", "Chief Technology Officer", "Chief Marketing Officer",
    "Chief Financial Officer", "Chief Operating Officer", "Chief Data Officer",
    "Chief Product Officer", "Chief Revenue Officer", "Vice President of Sales",
    "Vice President of Engineering", "Vice President of Marketing", "Vice President of HR",
    
    # Engineering
    "Senior Software Engineer", "Staff Software Engineer", "Principal Engineer",
    "Engineering Manager", "Director of Engineering", "Solutions Architect",
    "Cloud Engineer", "Data Engineer", "ML Engineer", "Frontend Developer",
    "Backend Developer", "Full Stack Developer", "Mobile Developer", "QA Engineer",
    "Site Reliability Engineer", "Security Engineer", "Platform Engineer",
    
    # Product
    "Product Manager", "Senior Product Manager", "Associate Product Manager",
    "Product Owner", "Product Designer", "UX Designer", "UI Designer",
    "UX Researcher", "Product Marketing Manager", "Technical Product Manager",
    
    # Marketing
    "Digital Marketing Manager", "SEO Specialist", "SEM Specialist",
    "Social Media Manager", "Content Marketing Manager", "Email Marketing Manager",
    "Demand Generation Manager", "Marketing Analyst", "Brand Strategist",
    "Marketing Operations Manager", "Performance Marketing Manager",
    
    # Sales
    "Sales Director", "Regional Sales Manager", "Enterprise Account Executive",
    "Sales Development Representative", "Account Manager", "Customer Success Manager",
    "Business Development Manager", "Inside Sales Representative",
    
    # HR
    "HR Manager", "Talent Acquisition Manager", "Recruiter", "HR Business Partner",
    "Compensation Analyst", "Training Manager", "People Operations Manager",
    "HR Generalist", "Employee Relations Manager",
    
    # Finance
    "Financial Analyst", "Senior Financial Analyst", "Finance Manager",
    "Controller", "Treasury Analyst", "Budget Analyst", "Tax Manager",
    
    # Operations
    "Operations Manager", "Supply Chain Manager", "Logistics Coordinator",
    "Project Manager", "Program Manager", "Business Analyst", "Operations Analyst",
    
    # Data
    "Data Analyst", "Senior Data Analyst", "Business Intelligence Analyst",
    "Data Scientist", "Analytics Manager", "Database Administrator"
]


# Additional skills
ADDITIONAL_SKILLS = [
    # Programming Languages
    "Ruby", "PHP", "Swift", "Kotlin", "Rust", "R", "MATLAB", "Scala", "Perl", "Shell Scripting",
    
    # Frameworks & Libraries
    "Vue.js", "Angular", "Django", "Flask", "Spring Boot", "Express.js", "FastAPI",
    "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy",
    
    # Databases
    "PostgreSQL", "MySQL", "MongoDB", "Redis", "Cassandra", "DynamoDB", "Neo4j",
    "Elasticsearch", "Oracle", "SQL Server",
    
    # Cloud & DevOps
    "GCP", "Jenkins", "GitLab CI/CD", "Terraform", "Ansible", "Chef", "Puppet",
    "Prometheus", "Grafana", "New Relic", "Datadog",
    
    # Business Tools
    "Power BI", "Looker", "SAP", "HubSpot", "Marketo", "Google Analytics",
    "Adobe Creative Suite", "Sketch", "InVision", "Slack", "Microsoft Teams",
    
    # Methodologies
    "Waterfall", "Kanban", "Lean", "Six Sigma", "Design Thinking", "OKRs",
    
    # Soft Skills
    "Strategic Planning", "Stakeholder Management", "Change Management",
    "Conflict Resolution", "Decision Making", "Emotional Intelligence",
    "Cross-functional Collaboration", "Presentation Skills", "Client Relations",
    "Budget Management", "Risk Management", "Process Improvement",
    
    # Domain Skills
    "Product Strategy", "Go-to-Market Strategy", "A/B Testing", "User Research",
    "Competitive Analysis", "Market Research", "Business Development",
    "Contract Negotiation", "Vendor Management", "Compliance", "GDPR",
    "Data Privacy", "Information Security", "Network Security",
    
    # Languages
    "Italian", "Portuguese", "Russian", "Arabic", "Korean", "Dutch",
    "Swedish", "Polish", "Turkish", "Hindi"
]


def generate_campaigns(n=69):
    """Generate n campaign names."""
    campaigns = []
    
    for _ in range(n):
        template = random.choice(CAMPAIGN_TEMPLATES)
        campaign = template.format(
            brand=random.choice(BRANDS),
            product=random.choice(PRODUCTS),
            season=random.choice(SEASONS),
            event=random.choice(EVENTS),
            action=random.choice(ACTIONS),
            audience=random.choice(AUDIENCES),
            region=random.choice(REGIONS),
            metric=random.choice(METRICS),
            year=random.choice(["2024", "2025"])
        )
        campaigns.append(campaign)
    
    return campaigns


def main():
    """Generate additional entities and merge with existing vocabulary."""
    print("="*60)
    print("🚀 Generating Additional Entities")
    print("="*60)
    
    # Load existing vocabulary
    vocab_file = Path(__file__).parent.parent / 'training_data/raw/entity_vocabulary.json'
    print(f"\n📂 Loading existing vocabulary from {vocab_file}")
    
    with open(vocab_file, 'r', encoding='utf-8') as f:
        vocabulary = json.load(f)
    
    print("\n📊 Current counts:")
    print(f"  CAMPAIGN: {len(vocabulary['CAMPAIGN'])}")
    print(f"  ROLE: {len(vocabulary['ROLE'])}")
    print(f"  SKILL: {len(vocabulary['SKILL'])}")
    
    # Generate additional entities
    print("\n1️⃣  Generating 69 additional campaigns...")
    new_campaigns = generate_campaigns(69)
    vocabulary['CAMPAIGN'].extend(new_campaigns)
    print(f"  ✅ Total campaigns: {len(vocabulary['CAMPAIGN'])}")
    
    print("\n2️⃣  Adding 76 additional role titles...")
    vocabulary['ROLE'].extend(ROLE_TITLES[:76])
    vocabulary['ROLE'] = list(set(vocabulary['ROLE']))  # Deduplicate
    print(f"  ✅ Total roles: {len(vocabulary['ROLE'])}")
    
    print("\n3️⃣  Adding 90 additional skills...")
    vocabulary['SKILL'].extend(ADDITIONAL_SKILLS[:90])
    vocabulary['SKILL'] = list(set(vocabulary['SKILL']))  # Deduplicate
    print(f"  ✅ Total skills: {len(vocabulary['SKILL'])}")
    
    # Print final summary
    print("\n" + "="*60)
    print("📊 FINAL ENTITY COUNTS")
    print("="*60)
    total = 0
    for entity_type, entities in vocabulary.items():
        count = len(entities)
        total += count
        status = "✅" if count >= 80 else "⚠️"
        print(f"  {status} {entity_type:12} : {count:4} entities")
    print("-"*60)
    print(f"     {'TOTAL':12} : {total:4} entities")
    print("="*60)
    
    # Save updated vocabulary
    print(f"\n💾 Saving updated vocabulary to {vocab_file}")
    with open(vocab_file, 'w', encoding='utf-8') as f:
        json.dump(vocabulary, f, indent=2, ensure_ascii=False)
    
    print("\n✅ Additional entities generated successfully!")
    print("📊 Ready for training sentence generation")


if __name__ == '__main__':
    main()
