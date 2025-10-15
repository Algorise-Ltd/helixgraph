// Neo4j Schema Setup for HR Data
// This script creates constraints and indexes for the HR knowledge graph

// ============================================================
// CONSTRAINTS - Ensure data integrity and uniqueness
// ============================================================

// Employee constraints
CREATE CONSTRAINT employee_id_unique IF NOT EXISTS
FOR (e:Employee) REQUIRE e.employee_id IS UNIQUE;

// Department constraints
CREATE CONSTRAINT department_name_unique IF NOT EXISTS
FOR (d:Department) REQUIRE d.name IS UNIQUE;

// Location constraints
CREATE CONSTRAINT location_name_unique IF NOT EXISTS
FOR (l:Location) REQUIRE l.name IS UNIQUE;

// Skill constraints
CREATE CONSTRAINT skill_id_unique IF NOT EXISTS
FOR (s:Skill) REQUIRE s.skill_id IS UNIQUE;


// ============================================================
// INDEXES - Optimize query performance
// ============================================================

// Employee indexes
CREATE INDEX employee_email IF NOT EXISTS
FOR (e:Employee) ON (e.email);

CREATE INDEX employee_name IF NOT EXISTS
FOR (e:Employee) ON (e.last_name, e.first_name);

CREATE INDEX employee_job_title IF NOT EXISTS
FOR (e:Employee) ON (e.job_title);

CREATE INDEX employee_hire_date IF NOT EXISTS
FOR (e:Employee) ON (e.hire_date);

// Skill indexes
CREATE INDEX skill_name IF NOT EXISTS
FOR (s:Skill) ON (s.name);

CREATE INDEX skill_category IF NOT EXISTS
FOR (s:Skill) ON (s.category);


// ============================================================
// VERIFICATION
// ============================================================

// List all constraints
SHOW CONSTRAINTS;

// List all indexes
SHOW INDEXES;

RETURN "Schema setup complete! Constraints and indexes created." AS message;
