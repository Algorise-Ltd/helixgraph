"""
HR Loader - Domain-specific loader for HR data

Loads HR data into Neo4j:
- Employees
- Skills
- Departments
- Locations
- Employee-Skill relationships with proficiency
"""
import os
from typing import List, Dict, Any, Optional
from pathlib import Path

from etl.base_loader import BaseLoader
from etl.utils import load_json, setup_file_logger, get_project_root
from schemas.hr_schema import Employee, Skill, EmployeeSkill


class HRLoader(BaseLoader):
    """
    HR-specific data loader.
    
    Loads:
    - Employee nodes
    - Skill nodes
    - Department nodes
    - Location nodes
    - WORKS_IN relationships
    - LOCATED_IN relationships
    - REPORTS_TO relationships
    - HAS_SKILL relationships (with proficiency)
    """
    
    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str = "neo4j",
        batch_size: int = 100,
        data_dir: Optional[str] = None,
        log_file: Optional[str] = None
    ):
        """
        Initialize HR Loader.
        
        Args:
            uri: Neo4j URI
            user: Neo4j username
            password: Neo4j password
            database: Neo4j database name
            batch_size: Batch size for loading
            data_dir: Directory containing HR data files (default: data/hr)
            log_file: Log file path (default: logs/hr_load.log)
        """
        # Setup logger before calling parent __init__
        if log_file is None:
            project_root = get_project_root()
            log_file = str(project_root / 'logs' / 'hr_load.log')
        
        logger = setup_file_logger('HRLoader', log_file)
        
        # Initialize parent
        super().__init__(uri, user, password, database, batch_size, logger)
        
        # Set data directory
        if data_dir is None:
            project_root = get_project_root()
            self.data_dir = project_root / 'data' / 'hr'
        else:
            self.data_dir = Path(data_dir)
        
        self.logger.info(f"Data directory: {self.data_dir}")
        
        # Data storage
        self.employees = []
        self.skills = []
        self.employee_skills = []
    
    def load_data_files(self):
        """Load all HR data files from disk"""
        self.logger.info("Loading data files...")
        
        # Load employees
        employees_file = self.data_dir / 'hr_employees.json'
        self.logger.info(f"Loading employees from {employees_file}")
        self.employees = load_json(str(employees_file))
        self.logger.info(f"✓ Loaded {len(self.employees)} employees")
        
        # Load skills
        skills_file = self.data_dir / 'hr_skills.json'
        self.logger.info(f"Loading skills from {skills_file}")
        self.skills = load_json(str(skills_file))
        self.logger.info(f"✓ Loaded {len(self.skills)} skills")
        
        # Load employee-skill relationships
        emp_skills_file = self.data_dir / 'hr_employee_skills.json'
        self.logger.info(f"Loading employee-skills from {emp_skills_file}")
        self.employee_skills = load_json(str(emp_skills_file))
        self.logger.info(f"✓ Loaded {len(self.employee_skills)} employee-skill relationships")
    
    def validate_data_with_schema(self):
        """Validate loaded data using Pydantic schemas"""
        self.logger.info("Validating data with Pydantic schemas...")
        
        # Validate employees
        valid_employees, emp_errors = self.validate_data(self.employees, Employee)
        if emp_errors:
            self.logger.warning(f"Found {len(emp_errors)} invalid employee records")
        self.employees = valid_employees
        
        # Validate skills
        valid_skills, skill_errors = self.validate_data(self.skills, Skill)
        if skill_errors:
            self.logger.warning(f"Found {len(skill_errors)} invalid skill records")
        self.skills = valid_skills
        
        # Validate employee-skill relationships
        valid_emp_skills, emp_skill_errors = self.validate_data(
            self.employee_skills, EmployeeSkill
        )
        if emp_skill_errors:
            self.logger.warning(f"Found {len(emp_skill_errors)} invalid employee-skill records")
        self.employee_skills = valid_emp_skills
        
        self.logger.info("✓ Data validation complete")
    
    def setup_schema(self):
        """Setup Neo4j schema with constraints and indexes"""
        self.logger.info("Setting up Neo4j schema...")
        
        # Constraints
        constraints = [
            """CREATE CONSTRAINT employee_id_unique IF NOT EXISTS
               FOR (e:Employee) REQUIRE e.employee_id IS UNIQUE""",
            
            """CREATE CONSTRAINT department_name_unique IF NOT EXISTS
               FOR (d:Department) REQUIRE d.name IS UNIQUE""",
            
            """CREATE CONSTRAINT location_name_unique IF NOT EXISTS
               FOR (l:Location) REQUIRE l.name IS UNIQUE""",
            
            """CREATE CONSTRAINT skill_id_unique IF NOT EXISTS
               FOR (s:Skill) REQUIRE s.skill_id IS UNIQUE"""
        ]
        
        for constraint in constraints:
            self.create_constraint(constraint)
        
        # Indexes
        indexes = [
            """CREATE INDEX employee_email IF NOT EXISTS
               FOR (e:Employee) ON (e.email)""",
            
            """CREATE INDEX employee_name IF NOT EXISTS
               FOR (e:Employee) ON (e.last_name, e.first_name)""",
            
            """CREATE INDEX employee_job_title IF NOT EXISTS
               FOR (e:Employee) ON (e.job_title)""",
            
            """CREATE INDEX employee_hire_date IF NOT EXISTS
               FOR (e:Employee) ON (e.hire_date)""",
            
            """CREATE INDEX skill_name IF NOT EXISTS
               FOR (s:Skill) ON (s.name)""",
            
            """CREATE INDEX skill_category IF NOT EXISTS
               FOR (s:Skill) ON (s.category)"""
        ]
        
        for index in indexes:
            self.create_index(index)
        
        self.logger.info("✓ Schema setup complete")
    
    def load_departments(self):
        """Load Department nodes"""
        self.logger.info("Loading departments...")
        
        # Extract unique departments
        departments = list(set(emp['department'] for emp in self.employees))
        dept_data = [{'name': dept} for dept in departments]
        
        cypher = """
            UNWIND $batch AS dept
            MERGE (d:Department {name: dept.name})
            SET d.created_at = datetime()
        """
        
        count = self.batch_load(dept_data, cypher, batch_size=50)
        self.stats.add_nodes('Department', count)
        self.logger.info(f"✓ Loaded {count} departments")
    
    def load_locations(self):
        """Load Location nodes"""
        self.logger.info("Loading locations...")
        
        # Extract unique locations
        locations = list(set(emp['location'] for emp in self.employees))
        loc_data = [{'name': loc} for loc in locations]
        
        cypher = """
            UNWIND $batch AS loc
            MERGE (l:Location {name: loc.name})
            SET l.created_at = datetime()
        """
        
        count = self.batch_load(loc_data, cypher, batch_size=50)
        self.stats.add_nodes('Location', count)
        self.logger.info(f"✓ Loaded {count} locations")
    
    def load_skills_nodes(self):
        """Load Skill nodes"""
        self.logger.info("Loading skills...")
        
        cypher = """
            UNWIND $batch AS skill
            MERGE (s:Skill {skill_id: skill.skill_id})
            SET s.name = skill.name,
                s.category = skill.category,
                s.created_at = datetime()
        """
        
        count = self.batch_load(self.skills, cypher, batch_size=50)
        self.stats.add_nodes('Skill', count)
        self.logger.info(f"✓ Loaded {count} skills")
    
    def load_employees_nodes(self):
        """Load Employee nodes with department and location relationships"""
        self.logger.info("Loading employees...")
        
        cypher = """
            UNWIND $batch AS emp
            MERGE (e:Employee {employee_id: emp.employee_id})
            SET e.first_name = emp.first_name,
                e.last_name = emp.last_name,
                e.email = emp.email,
                e.phone = emp.phone,
                e.hire_date = date(emp.hire_date),
                e.job_title = emp.job_title,
                e.salary = emp.salary,
                e.created_at = datetime()
            
            WITH e, emp
            MATCH (d:Department {name: emp.department})
            MERGE (e)-[r1:WORKS_IN]->(d)
            SET r1.created_at = datetime(),
                r1.source = "hr_data"
            
            WITH e, emp
            MATCH (l:Location {name: emp.location})
            MERGE (e)-[r2:LOCATED_IN]->(l)
            SET r2.created_at = datetime(),
                r2.source = "hr_data"
        """
        
        count = self.batch_load(self.employees, cypher)
        self.stats.add_nodes('Employee', count)
        self.stats.add_relationships('WORKS_IN', count)
        self.stats.add_relationships('LOCATED_IN', count)
        self.logger.info(f"✓ Loaded {count} employees with department and location relationships")
    
    def load_manager_relationships(self):
        """Load REPORTS_TO relationships"""
        self.logger.info("Loading manager relationships...")
        
        # Filter employees with managers
        employees_with_managers = [
            emp for emp in self.employees 
            if emp.get('manager_id') and emp['manager_id']
        ]
        
        cypher = """
            UNWIND $batch AS emp
            MATCH (e:Employee {employee_id: emp.employee_id})
            MATCH (m:Employee {employee_id: emp.manager_id})
            MERGE (e)-[r:REPORTS_TO]->(m)
            SET r.created_at = datetime()
        """
        
        count = self.batch_load(employees_with_managers, cypher)
        self.stats.add_relationships('REPORTS_TO', count)
        self.logger.info(f"✓ Loaded {count} manager relationships")
    
    def load_employee_skill_relationships(self):
        """Load HAS_SKILL relationships with proficiency"""
        self.logger.info("Loading employee-skill relationships...")
        
        cypher = """
            UNWIND $batch AS es
            MATCH (e:Employee {employee_id: es.employee_id})
            MATCH (s:Skill {skill_id: es.skill_id})
            MERGE (e)-[r:HAS_SKILL]->(s)
            SET r.proficiency_level = es.proficiency_level,
                r.years_of_experience = es.years_of_experience,
                r.created_at = datetime()
        """
        
        count = self.batch_load(self.employee_skills, cypher, batch_size=500)
        self.stats.add_relationships('HAS_SKILL', count)
        self.logger.info(f"✓ Loaded {count} employee-skill relationships")
    
    def load(self):
        """
        Main loading method - orchestrates the entire ETL process.
        
        Steps:
        1. Load data files
        2. Validate data
        3. Setup schema
        4. Load departments and locations
        5. Load skills
        6. Load employees
        7. Load manager relationships
        8. Load employee-skill relationships
        9. Print statistics
        """
        self.logger.info("=" * 70)
        self.logger.info("Starting HR Data Load")
        self.logger.info("=" * 70)
        
        try:
            # Step 1: Load data files
            self.load_data_files()
            
            # Step 2: Validate data
            self.validate_data_with_schema()
            
            # Step 3: Setup schema
            self.setup_schema()
            
            # Step 4: Load departments and locations (must be first)
            self.load_departments()
            self.load_locations()
            
            # Step 5: Load skills
            self.load_skills_nodes()
            
            # Step 6: Load employees (with dept and location relationships)
            self.load_employees_nodes()
            
            # Step 7: Load manager relationships
            self.load_manager_relationships()
            
            # Step 8: Load employee-skill relationships
            self.load_employee_skill_relationships()
            
            # Print statistics
            self.print_statistics()
            
            # Get graph statistics
            graph_stats = self.get_graph_statistics()
            self.logger.info("\nGraph Statistics:")
            self.logger.info(f"  Total Nodes: {graph_stats['total_nodes']:,}")
            self.logger.info(f"  Total Relationships: {graph_stats['total_relationships']:,}")
            
            self.logger.info("\n✅ HR data load completed successfully!")
            
        except Exception as e:
            self.logger.error(f"❌ Error during load: {e}", exc_info=True)
            raise


def main():
    """Main entry point for HR loader"""
    import sys
    from etl.utils import get_neo4j_config
    
    try:
        # Get Neo4j configuration
        config = get_neo4j_config()
        
        # Create loader
        with HRLoader(
            uri=config['uri'],
            user=config['user'],
            password=config['password'],
            batch_size=100
        ) as loader:
            # Test connection
            if not loader.test_connection():
                print("❌ Failed to connect to Neo4j")
                sys.exit(1)
            
            # Load data
            loader.load()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
