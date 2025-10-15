"""
Preview generated HR data
"""
import json

print("="*70)
print("HR Data Preview")
print("="*70)

# Load data
with open('data/hr/hr_employees.json', 'r') as f:
    employees = json.load(f)

with open('data/hr/hr_skills.json', 'r') as f:
    skills = json.load(f)

with open('data/hr/hr_employee_skills.json', 'r') as f:
    emp_skills = json.load(f)

print(f"\n📊 Dataset Summary:")
print(f"  Employees:     {len(employees)}")
print(f"  Skills:        {len(skills)}")
print(f"  Departments:   {len(set(e['department'] for e in employees))}")
print(f"  Locations:     {len(set(e['location'] for e in employees))}")
print(f"  Relationships: {len(emp_skills)}")

print("\n📋 Sample Employee (EMP0010):")
sample_emp = employees[9]
print(json.dumps(sample_emp, indent=2))

print("\n🎯 Sample Skills (first 10):")
for skill in skills[:10]:
    print(f"  {skill['skill_id']}: {skill['name']:20} ({skill['category']})")

print("\n🔗 Sample Employee-Skill Relationships (first 5):")
for es in emp_skills[:5]:
    print(f"  {es['employee_id']} → {es['skill_id']}: {es['proficiency_level']:12} ({es['years_of_experience']} years)")

print("\n" + "="*70)

