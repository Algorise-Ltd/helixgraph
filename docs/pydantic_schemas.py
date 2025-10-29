from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Q001: Top 10 high-value customers
class Q1Schema(BaseModel):
    customer_id: int
    total_revenue: float
    order_count: int

# Q002: Marketing campaigns with highest conversion rate
class Q2Schema(BaseModel):
    campaign_id: int
    campaign_name: str
    conversion_rate: float

# Q003: Average order frequency per customer by region
class Q3Schema(BaseModel):
    region: str
    average_orders: float

# Q004: Suppliers ranked by on-time delivery
class Q4Schema(BaseModel):
    supplier_id: int
    supplier_name: str
    on_time_delivery_rate: float

# Q005: Products below safety stock level
class Q5Schema(BaseModel):
    product_id: int
    product_name: str
    current_stock: int
    safety_stock: int

# Q006: Average order processing time
class Q6Schema(BaseModel):
    employee_id: int
    employee_name: str
    average_processing_days: float

# Q007: Employee attrition rate by department
class Q7Schema(BaseModel):
    department_id: int
    department_name: str
    attrition_rate: float

# Q008: New employees completing onboarding
class Q8Schema(BaseModel):
    employee_id: int
    employee_name: str
    completed_onboarding: bool

# Q009: Employee performance vs project completion
class Q9Schema(BaseModel):
    employee_id: int
    employee_name: str
    team_id: int
    projects_completed: int
    performance_score: float

# Q010: High-value customers affected by supply chain delays
class Q10Schema(BaseModel):
    customer_id: int
    customer_name: str
    total_revenue: float
    average_order_delay_days: float

# Q011: ROI of marketing campaigns relative to inventory
class Q11Schema(BaseModel):
    campaign_id: int
    campaign_name: str
    roi: float
    stock_change: int

# Q012: Sales team performance vs customer satisfaction
class Q12Schema(BaseModel):
    team_id: int
    team_name: str
    team_sales_total: float
    average_customer_feedback_score: float
