# Procurement Ontology v0.1 (Sprint 0)

## Entities & minimal fields
**Supplier**

- legalName ([Text])
- vendorCode ([Text], Internal identifier)
- taxID ([Text], VAT Number)
- address ([Text])
- contactPerson ([Text])
- riskScore ([Number], 0-100 score)
- supplierTier ([Text], e.g., Tier 1, Strategic)
- isSingleSource ([Boolean])

**PO (Purchase Order)**

- orderNumber ([Text])
- dateIssued ([Date])
- dateChanged ([Date])
- orderStatus ([Text], e.g., Processing, Delivered)
- orderTotalValue ([Monetary Amount])
- orderValueCategory ([Text], High/Medium/Low)
- approvedBy ([Text], can be turned into edge if Person entity is created)

**Invoice**

- invoiceNumber ([Text])
- dateCreated ([Date])
- paymentDueDate ([Date])
- totalPaymentDue ([Monetary Amount])
- paymentStatus ([Text], e.g., Paid, Overdue)

**Contract**

- contractName ([Text], Contract ID or title)
- startDate ([Date])
- endDate ([Date])
- contractedAmount ([Monetary Amount])
- contractType ([Text], e.g., MSA, SOW)
- isAutoRenewing ([Boolean])
- hasAmendments ([Boolean])

**Risk (attached to Supplier)**

- riskType ([Text], e.g., FinancialRisk)
- riskDescription ([Text])
- mitigationPlan ([Text])
- riskStatus ([Text], e.g., Active, Mitigated)

**PR (Purchase Requisition)**

- requisitionID ([Text])
- dateRequested ([Date])
- dateConverted ([Date])
- requestedBy ([Text], can be turned into edge if Person entity is created)
- status ([Text], e.g., Approved, Pending)

**Product_Service**

- name ([Text])
- sku ([Text], Internal product code)
- description ([Text])
- unitOfMeasure ([Text], eg., Piece, KG)
- category ([Text], Goods or Service Category)
- isCritical ([Boolean])

**Line_Item**

- quantity ([Number])
- unitPrice ([Monetary Amount])
- lineTotal ([Monetary Amount], total)

## Relationships (graph edges we expect later)

- PO --(ORDERED_FROM)--> Supplier
- PO --(REFERENCES)--> Contract
- PO --(CONTAINS)--> LineItem
- PO --(BASED_ON)--> Requisition
- Requisition --(REQUESTS)--> Product_Service
- Invoice --(ISSUED_BY)--> Supplier
- Invoice --(REFERENCES)--> PO
- Invoice --(CONTAINS)--> LineItem
- Contract --(SIGNED_WITH)--> Supplier
- Contract --(AMENDS)--> Contract
- Supplier --(HAS_RISK)--> Risk
- LineItem --(IS_FOR)--> Product_Service
- Product_Service --(SUPPLIED_BY)--> Supplier
- Supplier --(PARENTS)--> Supplier