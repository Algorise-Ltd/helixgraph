# Procurement Ontology v0.9

## Entities & minimal fields
**Supplier**
- vendorCode ([Text], Internal identifier - Primary Key)
- legalName ([Text])
- taxID ([Text], VAT Number)
- address ([Text])
- country ([Text])
- contactPerson ([Text])
- isActive ([Boolean])
- financialHealth([Text], High, Medium, Low)
- riskScore ([Number], 0-100 score)

**PO (Purchase Order)**
- orderNumber ([Text]), Internal identifier - Primary Key)
- dateIssued ([Date])
- dateChanged ([Date])
- orderStatus ([Text], e.g., Draft, Pending Approval, Approved, Rejected, Issued, Partially Received, Delivered, Closed, Cancelled)
- orderTotalValue ([Monetary Amount])
- approvedBy ([Text], can be turned into edge if Person entity is created)

**Invoice**
- invoiceNumber ([Text], Internal identifier - Primary Key)
- supplierReference ([Text], supplier invoice reference)
- dateCreated ([Date])
- paymentDueDate ([Date])
- totalPaymentDue ([Monetary Amount])
- paymentStatus ([Text], e.g., Received, Approved, Rejected, Scheduled for Payment, Paid, Overdue)
- late_payment_flag ([Boolean])

**Contract**
- id ([Text], Internal identifier - Primary Key)
- contractName ([Text], title)
- startDate ([Date])
- endDate ([Date])
- contractedAmount ([Monetary Amount])
- contractType ([Text], e.g., MSA, SOW)
- isAutoRenewing ([Boolean])
- hasAmendments ([Boolean])

**Risk**
- riskId ([Text], Internal identifier - Primary Key)
- riskType ([Text], e.g., FinancialRisk)
- riskDescription ([Text])
- mitigationPlan ([Text])
- riskStatus ([Text], e.g., Active, Mitigated)
- riskScore ([Number], score for the specific Risk Type)

**PR (Purchase Requisition)**
- requisitionID ([Text], Internal identifier - Primary Key)
- dateRequested ([Date])
- dateConverted ([Date])
- requestedBy ([Text], can be turned into edge if Person entity is created)
- status ([Text], e.g., Draft, Pending Approval, Approved, Turned to PO, Rejected)

**Product_Service**
- name ([Text])
- sku ([Text], Internal identifier - Primary Key)
- description ([Text])
- unitOfMeasure ([Text], eg., Piece, KG)
- isCritical ([Boolean])

**Line_Item**
- quantity ([Number])
- unitPrice ([Monetary Amount])
- lineTotal ([Monetary Amount], total)

**Category**
- L4CategoryName ([Text], Primary Key)
- level_1 ([Text])
- level_2 ([Text])
- level_3 ([Text])


## Relationships (graph edges we expect later)
- PO --(ISSUED_TO)--> Supplier
- PO --(REFERENCES)--> Contract
- PO --(CONTAINS)--> LineItem
- PO --(BASED_ON)--> Requisition
- Requisition --(REQUESTS)--> Product_Service
- Requisition --(CONTAINS)--> LineItem
- Invoice --(ISSUED_BY)--> Supplier
- Invoice --(REFERENCES)--> PO
- Invoice --(CONTAINS)--> LineItem
- Contract --(SIGNED_WITH)--> Supplier
- Contract --(AMENDS)--> Contract
- Supplier --(HAS_RISK)--> Risk
- LineItem --(IS_FOR)--> Product_Service
- LineItem --(BILLED_BY)--> Invoice
- Product_Service --(SUPPLIED_BY)--> Supplier
- Product_Service --(BELONGS_TO)--> Category

---

## Supplier Category Taxonomy
This taxonomy categorizes suppliers into a hierarchical structure.

### L1: Direct Materials
-   **L2: Raw Materials**
    -   **L3: Metals & Minerals**
        -   L4: Ferrous Metals (Steel, Iron)
        -   L4: Non-Ferrous Metals (Aluminum, Copper, Lithium)
        -   L4: Precious Metals (Gold, Silver)
    -   **L3: Chemicals**
        -   L4: Solvents & Adhesives
        -   L4: Coatings, Pigments & Dyes
        -   L4: Bulk & Specialty Chemicals
    -   **L3: Plastics & Polymers**
        -   L4: Resins (PET, HDPE)
        -   L4: Injection Molded Plastics
        -   L4: Films & Sheeting
    -   **L3: Agricultural Products**
        -   L4: Grains & Cereals
        -   L4: Oils & Fats
        -   L4: Fibers (Cotton, Wool)
-   **L2: Components & Sub-Assemblies**
    -   **L3: Electronic Components**
        -   L4: Semiconductors & Integrated Circuits
        -   L4: Passive Components (Resistors, Capacitors)
        -   L4: Printed Circuit Boards (PCBs)
    -   **L3: Mechanical Components**
        -   L4: Fasteners (Nuts, Bolts, Screws)
        -   L4: Bearings & Gears
        -   L4: Motors & Pumps
    -   **L3: Fabricated Parts**
        -   L4: Machined Parts
        -   L4: Stamped Metal Parts
        -   L4: Castings & Forgings
-   **L2: Packaging Materials**
    -   **L3: Primary Packaging**
        -   L4: Bottles, Jars & Cans
        -   L4: Bags, Pouches & Wrappers
    -   **L3: Secondary Packaging**
        -   L4: Corrugated Boxes & Cartons
        -   L4: Trays & Dividers
    -   **L3: Tertiary Packaging & Shipping Supplies**
        -   L4: Pallets & Crates
        -   L4: Stretch & Shrink Wrap
        -   L4: Labels & Inserts

### L1: Technical Materials
-   **L2: Manufacturing Equipment**
    -   **L3: Production Machinery**
        -   L4: CNC Machines & Lathes
        -   L4: Assembly Line Automation & Robotics
        -   L4: Processing Equipment
    -   **L3: Tooling & Molds**
        -   L4: Dies, Jigs & Fixtures
        -   L4: Molds & Patterns
    -   **L3: Material Handling Equipment**
        -   L4: Forklifts & Pallet Jacks
        -   L4: Conveyor Systems
-   **L2: MRO (Maintenance, Repair & Operations)**
    -   **L3: Spare Parts**
        -   L4: Equipment-Specific Spare Parts
        -   L4: General Industrial Spares (Valves, Belts)
    -   **L3: Industrial Consumables**
        -   L4: Lubricants, Oils & Greases
        -   L4: Abrasives & Welding Supplies
        -   L4: Cleaning Agents & Janitorial Supplies
    -   **L3: Safety & PPE (Personal Protective Equipment)**
        -   L4: Safety Gloves, Goggles & Hard Hats
        -   L4: Fall Protection & Respiratory Gear
-   **L2: R&D and Laboratory**
    -   **L3: Lab Equipment**
        -   L4: Measurement & Testing Instruments
        -   L4: Analytical Equipment (Spectrometers, Microscopes)
    -   **L3: Lab Supplies**
        -   L4: Chemicals & Reagents
        -   L4: Glassware & Plasticware
    -   **L3: Prototyping Services & Materials**
        -   L4: 3D Printing Services
        -   L4: Rapid Prototyping Materials

### L1: Indirect Services and Materials
-   **L2: IT & Technology**
    -   **L3: Hardware**
        -   L4: Data Center (Servers, Storage)
        -   L4: Networking (Routers, Switches, Firewalls)
        -   L4: End-User Computing (Laptops, Desktops, Monitors)
        -   L4: Mobile Devices (Tablets, Smartphones, Accessories)
        -   L4: Peripherals & Accessories (Printers, Keyboards)
        -   L4: Audio/Visual Equipment (Projectors, Conferencing Systems)
    -   **L3: Software**
        -   L4: Enterprise Applications (ERP, CRM, SCM)
        -   L4: Productivity & Collaboration Suites (Office, Email)
        -   L4: Engineering & Design (CAD, PLM)
        -   L4: Security & Compliance Software
        -   L4: Business Intelligence & Analytics (BI, Data Visualization)
    -   **L3: IT Services & Telecom**
        -   L4: Cloud & Hosting (IaaS, PaaS, SaaS)
        -   L4: IT Consulting & Implementation
        -   L4: Managed Services (Helpdesk, Network Management)
        -   L4: Telecommunications (Mobile, Fixed Line, Internet)
        -   L4: Cybersecurity Services (Pen Testing, Monitoring, SOC)
-   **L2: Corporate & Professional Services**
    -   **L3: Financial Services**
        -   L4: Banking & Treasury Services
        -   L4: Audit, Tax & Advisory Services
        -   L4: Insurance (Property, Liability, Health, Travel)
        -   L4: Payment Processing
    -   **L3: Human Resources Services**
        -   L4: Recruitment & Staffing (Permanent, Temporary)
        -   L4: Payroll & Benefits Administration
        -   L4: Training & Development
        -   L4: HR Consulting & Technology
        -   L4: Employee Welfare & Assistance Programs
    -   **L3: Legal Services**
        -   L4: Corporate & Commercial Law
        -   L4: Intellectual Property & Patents
        -   L4: Litigation & Dispute Resolution
    -   **L3: Consulting**
        -   L4: Management & Strategy Consulting
        -   L4: Operations & Process Improvement
        -   L4: Environmental & Sustainability Consulting
-   **L2: Marketing & Sales**
    -   **L3: Marketing & Advertising**
        -   L4: Digital Marketing & SEO/SEM
        -   L4: Creative, Content & Branding Agencies
        -   L4: Public Relations (PR) Firms
        -   L4: Media Buying (Print, Broadcast, Digital)
        -   L4: Influencer & Social Media Marketing
        -   L4: Sponsorships & Partnerships
    -   **L3: Sales Support**
        -   L4: Sales Training
        -   L4: Lead Generation Services
        -   L4: Merchandising Services
        -   L4: Customer Relationship Management (CRM) Tools
        -   L4: Sales Incentive & Reward Programs
    -   **L3: Events & Promotions**
        -   L4: Event Management & Production
        -   L4: Trade Show & Exhibition Services
        -   L4: Promotional Goods & Branded Merchandise
    -   **L3: Market Research**
        -   L4: Data, Surveys & Analysis
        -   L4: Competitor Intelligence Services
        -   L4: Brand Tracking & Analytics
-   **L2: Facility Services**
    -   **L3: Real Estate & Utilities**
        -   L4: Property Leases & Rent
        -   L4: Utilities (Gas, Electricity, Water)
        -   L4: Waste Management & Recycling
        -   L4: Energy Management & Sustainability Services
    -   **L3: Facility Management**
        -   L4: Janitorial & Cleaning Services
        -   L4: Building Maintenance & HVAC
        -   L4: Landscaping & Groundskeeping
    -   **L3: Office Supplies & Services**
        -   L4: Stationery & Consumables
        -   L4: Office Furniture & Fixtures
        -   L4: Catering & Vending Services
        -   L4: Mail & Document Management
        -   L4: Print & Copy Services
    -   **L3: Security Services**
        -   L4: Manned Guarding
        -   L4: Alarm Systems & Monitoring
        -   L4: Access Control Systems
        -   L4: Security Consulting & Risk Assessment
-   **L2: Logistics**
    -   **L3: Transportation & Freight**
        -   L4: Road Freight (FTL, LTL)
        -   L4: Air & Ocean Freight
        -   L4: Parcel & Courier Services
        -   L4: Freight Forwarding & Customs Brokerage
    -   **L3: Warehousing & Distribution**
        -   L4: 3rd Party Logistics (3PL) Services
        -   L4: Warehouse Rental & Storage
        -   L4: Order Fulfillment & Value-Added Services
        -   L4: Inventory Management Systems
    -   **L3: Fleet Management**
        -   L4: Vehicle Leasing & Purchase
        -   L4: Fuel, Fuel Cards & Management
        -   L4: Vehicle Maintenance & Repair
        -   L4: Telematics & Fleet Tracking
-   **L2: Corporate Travel**
    -   **L3: Transportation**
        -   L4: Airlines
        -   L4: Rail Services
        -   L4: Car Rentals
        -   L4: Taxi & Ride-Sharing Services
    -   **L3: Accommodation**
        -   L4: Hotels & Chains
        -   L4: Serviced Apartments
    -   **L3: Travel Management Services**
        -   L4: Travel Management Companies (TMCs)
        -   L4: Online Booking Tools (OBTs)
        -   L4: Expense Management Software
        -   L4: Visa & Immigration Support
