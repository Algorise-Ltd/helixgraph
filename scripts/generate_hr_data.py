"""
Generate sample HR data using Faker
Includes employees, skills, and employee-skill relationships
"""
import json
import csv
import random
from faker import Faker
from datetime import datetime

fake = Faker()


def generate_skills():
    """Generate comprehensive skills list (40+ skills)"""
    skills = [
        # Technical/Programming (12)
        {"skill_id": "SKILL001", "name": "Python", "category": "Technical"},
        {"skill_id": "SKILL002", "name": "Java", "category": "Technical"},
        {"skill_id": "SKILL003", "name": "JavaScript", "category": "Technical"},
        {"skill_id": "SKILL004", "name": "TypeScript", "category": "Technical"},
        {"skill_id": "SKILL005", "name": "C++", "category": "Technical"},
        {"skill_id": "SKILL006", "name": "Go", "category": "Technical"},
        {"skill_id": "SKILL007", "name": "SQL", "category": "Technical"},
        {"skill_id": "SKILL008", "name": "React", "category": "Technical"},
        {"skill_id": "SKILL009", "name": "Node.js", "category": "Technical"},
        {"skill_id": "SKILL010", "name": "Machine Learning", "category": "Technical"},
        {"skill_id": "SKILL011", "name": "Data Analysis", "category": "Technical"},
        {"skill_id": "SKILL012", "name": "API Design", "category": "Technical"},
        
        # Tools (10)
        {"skill_id": "SKILL013", "name": "Docker", "category": "Tool"},
        {"skill_id": "SKILL014", "name": "Kubernetes", "category": "Tool"},
        {"skill_id": "SKILL015", "name": "Git", "category": "Tool"},
        {"skill_id": "SKILL016", "name": "AWS", "category": "Tool"},
        {"skill_id": "SKILL017", "name": "Azure", "category": "Tool"},
        {"skill_id": "SKILL018", "name": "Salesforce", "category": "Tool"},
        {"skill_id": "SKILL019", "name": "Tableau", "category": "Tool"},
        {"skill_id": "SKILL020", "name": "Excel", "category": "Tool"},
        {"skill_id": "SKILL021", "name": "Jira", "category": "Tool"},
        {"skill_id": "SKILL022", "name": "Figma", "category": "Tool"},
        
        # Soft Skills (10)
        {"skill_id": "SKILL023", "name": "Leadership", "category": "Soft Skill"},
        {"skill_id": "SKILL024", "name": "Communication", "category": "Soft Skill"},
        {"skill_id": "SKILL025", "name": "Problem Solving", "category": "Soft Skill"},
        {"skill_id": "SKILL026", "name": "Team Collaboration", "category": "Soft Skill"},
        {"skill_id": "SKILL027", "name": "Project Management", "category": "Soft Skill"},
        {"skill_id": "SKILL028", "name": "Negotiation", "category": "Soft Skill"},
        {"skill_id": "SKILL029", "name": "Public Speaking", "category": "Soft Skill"},
        {"skill_id": "SKILL030", "name": "Critical Thinking", "category": "Soft Skill"},
        {"skill_id": "SKILL031", "name": "Time Management", "category": "Soft Skill"},
        {"skill_id": "SKILL032", "name": "Mentoring", "category": "Soft Skill"},
        
        # Domain Specific (12)
        {"skill_id": "SKILL033", "name": "Digital Marketing", "category": "Domain"},
        {"skill_id": "SKILL034", "name": "SEO/SEM", "category": "Domain"},
        {"skill_id": "SKILL035", "name": "Content Strategy", "category": "Domain"},
        {"skill_id": "SKILL036", "name": "Financial Modeling", "category": "Domain"},
        {"skill_id": "SKILL037", "name": "Accounting", "category": "Domain"},
        {"skill_id": "SKILL038", "name": "Sales Strategy", "category": "Domain"},
        {"skill_id": "SKILL039", "name": "Customer Success", "category": "Domain"},
        {"skill_id": "SKILL040", "name": "Recruitment", "category": "Domain"},
        {"skill_id": "SKILL041", "name": "HR Policies", "category": "Domain"},
        {"skill_id": "SKILL042", "name": "Supply Chain", "category": "Domain"},
        {"skill_id": "SKILL043", "name": "Agile/Scrum", "category": "Domain"},
        {"skill_id": "SKILL044", "name": "DevOps", "category": "Domain"},
        
        # Languages (6)
        {"skill_id": "SKILL045", "name": "English", "category": "Language"},
        {"skill_id": "SKILL046", "name": "Spanish", "category": "Language"},
        {"skill_id": "SKILL047", "name": "Mandarin", "category": "Language"},
        {"skill_id": "SKILL048", "name": "French", "category": "Language"},
        {"skill_id": "SKILL049", "name": "German", "category": "Language"},
        {"skill_id": "SKILL050", "name": "Japanese", "category": "Language"},
    ]
    return skills


def get_relevant_skills_for_role(job_title, department):
    """Return relevant skill IDs based on job title and department"""
    
    # Define skill mappings
    base_skills = {
        'Engineering': ['SKILL001', 'SKILL003', 'SKILL007', 'SKILL010', 'SKILL011', 'SKILL015', 'SKILL021', 'SKILL025', 'SKILL026', 'SKILL043'],
        'Marketing': ['SKILL020', 'SKILL024', 'SKILL029', 'SKILL031', 'SKILL033', 'SKILL034', 'SKILL035'],
        'Sales': ['SKILL018', 'SKILL020', 'SKILL024', 'SKILL028', 'SKILL029', 'SKILL038', 'SKILL039'],
        'HR': ['SKILL020', 'SKILL024', 'SKILL027', 'SKILL031', 'SKILL040', 'SKILL041'],
        'Finance': ['SKILL007', 'SKILL011', 'SKILL020', 'SKILL019', 'SKILL025', 'SKILL036', 'SKILL037'],
        'Operations': ['SKILL020', 'SKILL021', 'SKILL025', 'SKILL027', 'SKILL031', 'SKILL042', 'SKILL043']
    }
    
    # Additional skills based on seniority
    leadership_skills = ['SKILL023', 'SKILL027', 'SKILL032']
    tech_advanced = ['SKILL002', 'SKILL004', 'SKILL006', 'SKILL008', 'SKILL009', 'SKILL012', 'SKILL013', 'SKILL014', 'SKILL016', 'SKILL017', 'SKILL044']
    
    relevant_skills = base_skills.get(department, ['SKILL024', 'SKILL025', 'SKILL026', 'SKILL031']).copy()
    
    # Add role-specific skills
    if 'Manager' in job_title or 'Lead' in job_title or 'VP' in job_title or 'Chief' in job_title or 'CFO' in job_title or 'COO' in job_title:
        relevant_skills.extend(leadership_skills)
    
    if department == 'Engineering':
        # Add more technical skills for engineers
        relevant_skills.extend(random.sample(tech_advanced, k=min(5, len(tech_advanced))))
    
    # Add language skills (everyone has English, random chance of others)
    relevant_skills.append('SKILL045')  # English
    if random.random() > 0.6:
        relevant_skills.append(random.choice(['SKILL046', 'SKILL047', 'SKILL048', 'SKILL049', 'SKILL050']))
    
    # Remove duplicates and return random subset
    relevant_skills = list(set(relevant_skills))
    num_skills = random.randint(5, min(12, len(relevant_skills)))
    return random.sample(relevant_skills, k=num_skills)


def generate_proficiency_level(years_experience):
    """Generate realistic proficiency level based on experience"""
    if years_experience < 1:
        return random.choices(['Beginner', 'Intermediate'], weights=[0.7, 0.3])[0]
    elif years_experience < 3:
        return random.choices(['Beginner', 'Intermediate', 'Advanced'], weights=[0.2, 0.6, 0.2])[0]
    elif years_experience < 6:
        return random.choices(['Intermediate', 'Advanced', 'Expert'], weights=[0.2, 0.6, 0.2])[0]
    else:
        return random.choices(['Advanced', 'Expert'], weights=[0.4, 0.6])[0]


def generate_employee_skills(employee_id, job_title, department, hire_date_str):
    """Generate skills for an employee with realistic proficiency levels"""
    
    # Calculate years of experience based on hire date
    hire_date = datetime.fromisoformat(hire_date_str)
    years_since_hire = (datetime.now() - hire_date).days / 365.25
    
    relevant_skill_ids = get_relevant_skills_for_role(job_title, department)
    
    employee_skills = []
    for skill_id in relevant_skill_ids:
        # Generate years of experience for this specific skill
        skill_years = round(random.uniform(0.5, min(years_since_hire + 3, 15)), 1)
        proficiency = generate_proficiency_level(skill_years)
        
        employee_skills.append({
            'employee_id': employee_id,
            'skill_id': skill_id,
            'proficiency_level': proficiency,
            'years_of_experience': skill_years
        })
    
    return employee_skills


def generate_hr_data(num_employees=200):
    """Generate sample HR employee data with skills"""
    
    # Simplified to 3 core departments (aligned with business domains)
    departments = ['Engineering', 'Marketing', 'Sales']
    locations = ['San Francisco', 'London', 'Tokyo']
    
    job_titles = {
        'Engineering': ['Software Engineer', 'Senior Engineer', 'Tech Lead', 'Engineering Manager', 'Staff Engineer', 'DevOps Engineer', 'Data Engineer', 'QA Engineer'],
        'Marketing': ['Marketing Manager', 'Content Writer', 'SEO Specialist', 'Brand Manager', 'Marketing Coordinator', 'Digital Marketing Specialist', 'Product Marketing Manager', 'Growth Manager'],
        'Sales': ['Sales Rep', 'Account Executive', 'Sales Manager', 'VP of Sales', 'Sales Development Rep', 'Account Manager', 'Business Development Manager', 'Sales Engineer']
    }
    
    salary_ranges = {
        # Engineering roles
        'Software Engineer': (70000, 120000),
        'Senior Engineer': (100000, 160000),
        'Staff Engineer': (140000, 190000),
        'Tech Lead': (130000, 180000),
        'Engineering Manager': (140000, 200000),
        'DevOps Engineer': (80000, 140000),
        'Data Engineer': (85000, 145000),
        'QA Engineer': (65000, 110000),
        # Marketing roles
        'Marketing Manager': (80000, 130000),
        'Content Writer': (50000, 80000),
        'Marketing Coordinator': (45000, 65000),
        'SEO Specialist': (60000, 90000),
        'Brand Manager': (90000, 140000),
        'Digital Marketing Specialist': (55000, 95000),
        'Product Marketing Manager': (80000, 135000),
        'Growth Manager': (75000, 130000),
        # Sales roles
        'Sales Rep': (50000, 90000),
        'Sales Development Rep': (45000, 75000),
        'Account Executive': (70000, 120000),
        'Sales Manager': (90000, 150000),
        'VP of Sales': (150000, 250000),
        'Account Manager': (60000, 105000),
        'Business Development Manager': (75000, 130000),
        'Sales Engineer': (70000, 125000)
    }
    
    employees = []
    
    for i in range(num_employees):
        employee_id = f"EMP{i+1:04d}"
        department = random.choice(departments)
        job_title = random.choice(job_titles[department])
        salary_range = salary_ranges[job_title]
        
        # Better manager assignment logic
        manager_id = None
        if i > 10:  # First 10 are senior leaders
            manager_id = f"EMP{random.randint(1, max(1, min(i-1, 30))):04d}"
        
        employee = {
            'employee_id': employee_id,
            'first_name': fake.first_name(),
            'last_name': fake.last_name(),
            'email': fake.email(),
            'phone': fake.phone_number(),
            'hire_date': fake.date_between(start_date='-8y', end_date='today').isoformat(),
            'job_title': job_title,
            'department': department,
            'manager_id': manager_id,
            'salary': round(random.uniform(*salary_range), 2),
            'location': random.choice(locations)
        }
        
        employees.append(employee)
    
    return employees


if __name__ == "__main__":
    print("=" * 60)
    print("Generating HR Data with Skills")
    print("=" * 60)
    
    # Generate skills
    print("\n[1/5] Generating skills taxonomy...")
    skills = generate_skills()
    print(f"✓ Generated {len(skills)} unique skills")
    
    # Generate employees
    print("\n[2/5] Generating employee profiles...")
    employees = generate_hr_data(num_employees=200)
    print(f"✓ Generated {len(employees)} employees")
    
    # Generate employee-skill relationships
    print("\n[3/5] Generating employee-skill relationships...")
    all_employee_skills = []
    for emp in employees:
        emp_skills = generate_employee_skills(
            emp['employee_id'], 
            emp['job_title'], 
            emp['department'],
            emp['hire_date']
        )
        all_employee_skills.extend(emp_skills)
    print(f"✓ Generated {len(all_employee_skills)} skill assignments")
    
    # Save employees
    print("\n[4/5] Saving data files...")
    with open('data/hr/hr_employees.json', 'w') as f:
        json.dump(employees, f, indent=2)
    print(f"✓ Saved employees -> data/hr/hr_employees.json")
    
    with open('data/hr/hr_employees.csv', 'w', newline='') as f:
        if employees:
            writer = csv.DictWriter(f, fieldnames=employees[0].keys())
            writer.writeheader()
            writer.writerows(employees)
    print(f"✓ Saved employees -> data/hr/hr_employees.csv")
    
    # Save skills
    with open('data/hr/hr_skills.json', 'w') as f:
        json.dump(skills, f, indent=2)
    print(f"✓ Saved skills -> data/hr/hr_skills.json")
    
    with open('data/hr/hr_skills.csv', 'w', newline='') as f:
        if skills:
            writer = csv.DictWriter(f, fieldnames=skills[0].keys())
            writer.writeheader()
            writer.writerows(skills)
    print(f"✓ Saved skills -> data/hr/hr_skills.csv")
    
    # Save employee-skill relationships
    with open('data/hr/hr_employee_skills.json', 'w') as f:
        json.dump(all_employee_skills, f, indent=2)
    print(f"✓ Saved employee-skills -> data/hr/hr_employee_skills.json")
    
    with open('data/hr/hr_employee_skills.csv', 'w', newline='') as f:
        if all_employee_skills:
            writer = csv.DictWriter(f, fieldnames=all_employee_skills[0].keys())
            writer.writeheader()
            writer.writerows(all_employee_skills)
    print(f"✓ Saved employee-skills -> data/hr/hr_employee_skills.csv")
    
    # Save teams
    with open('data/hr/hr_teams.json', 'w') as f:
        json.dump(teams, f, indent=2)
    print(f"✓ Saved teams -> data/hr/hr_teams.json")
    
    with open('data/hr/hr_teams.csv', 'w', newline='') as f:
        if teams:
            writer = csv.DictWriter(f, fieldnames=teams[0].keys())
            writer.writeheader()
            writer.writerows(teams)
    print(f"✓ Saved teams -> data/hr/hr_teams.csv")
    
    # Save employee-team relationships
    with open('data/hr/hr_employee_teams.json', 'w') as f:
        json.dump(employee_teams, f, indent=2)
    print(f"✓ Saved employee-teams -> data/hr/hr_employee_teams.json")
    
    with open('data/hr/hr_employee_teams.csv', 'w', newline='') as f:
        if employee_teams:
            writer = csv.DictWriter(f, fieldnames=employee_teams[0].keys())
            writer.writeheader()
            writer.writerows(employee_teams)
    print(f"✓ Saved employee-teams -> data/hr/hr_employee_teams.csv")
    
    # Statistics
    print("\n[7/7] Data Generation Summary")
    print("=" * 60)
    print(f"Total Employees:        {len(employees)}")
    print(f"Total Skills:           {len(skills)}")
    print(f"Total Skill Relations:  {len(all_employee_skills)}")
    print(f"Avg Skills/Employee:    {len(all_employee_skills)/len(employees):.1f}")
    
    # Breakdown by category
    skill_categories = {}
    for skill in skills:
        cat = skill['category']
        skill_categories[cat] = skill_categories.get(cat, 0) + 1
    
    print(f"\nSkills by Category:")
    for cat, count in sorted(skill_categories.items()):
        print(f"  {cat:15} {count:2} skills")
    
    # Department breakdown
    dept_counts = {}
    for emp in employees:
        dept = emp['department']
        dept_counts[dept] = dept_counts.get(dept, 0) + 1
    
    print(f"\nEmployees by Department:")
    for dept, count in sorted(dept_counts.items()):
        print(f"  {dept:15} {count:3} employees")
    
    print("\n" + "=" * 60)
    print("✓ All data generated successfully!")
    print("=" * 60)
    
    # Sample data
    print("\n📋 Sample Employee:")
    print(json.dumps(employees[0], indent=2))
    
    print("\n📋 Sample Skill:")
    print(json.dumps(skills[0], indent=2))
    
    print("\n📋 Sample Employee-Skill Relationship:")
    print(json.dumps(all_employee_skills[0], indent=2))
