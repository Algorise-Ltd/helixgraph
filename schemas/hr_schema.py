"""
HR Schema - Pydantic models for HR data validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date
from enum import Enum


class ProficiencyLevel(str, Enum):
    """Skill proficiency levels"""
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"
    EXPERT = "Expert"


class SkillCategory(str, Enum):
    """Skill categories"""
    TECHNICAL = "Technical"
    SOFT_SKILL = "Soft Skill"
    DOMAIN = "Domain"
    TOOL = "Tool"
    LANGUAGE = "Language"


class Skill(BaseModel):
    """Skill model"""
    skill_id: str = Field(..., description="Unique skill identifier")
    name: str = Field(..., description="Skill name")
    category: SkillCategory = Field(..., description="Skill category")
    
    class Config:
        json_schema_extra = {
            "example": {
                "skill_id": "SKILL001",
                "name": "Python",
                "category": "Technical"
            }
        }


class EmployeeSkill(BaseModel):
    """Employee-Skill relationship with proficiency"""
    employee_id: str
    skill_id: str
    proficiency_level: ProficiencyLevel
    years_of_experience: Optional[float] = Field(None, ge=0, le=30)
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "skill_id": "SKILL001",
                "proficiency_level": "Advanced",
                "years_of_experience": 5.0
            }
        }


class Employee(BaseModel):
    """Employee model"""
    employee_id: str = Field(..., description="Unique employee identifier")
    first_name: str
    last_name: str
    email: str
    phone: Optional[str] = None
    hire_date: date
    job_title: str
    department: str
    manager_id: Optional[str] = None
    salary: float = Field(..., gt=0)
    location: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "employee_id": "EMP001",
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@company.com",
                "phone": "+1-555-0100",
                "hire_date": "2020-01-15",
                "job_title": "Software Engineer",
                "department": "Engineering",
                "manager_id": "EMP100",
                "salary": 85000.0,
                "location": "New York"
            }
        }
