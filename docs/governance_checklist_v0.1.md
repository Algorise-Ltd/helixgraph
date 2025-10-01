# Governance Checklist v0.1 (Sprint 0)

## Data classes

- Public Open Data (OK): Publicly available supplier information, open government contracting data. Slight modification are allowed to make Open Data connect with other data sources.

- Synthetic Data (OK): Anonymized or generated data for development and testing and development purposes.

- Customer Samples (NOT in S0; NDA + anonymization if ever used): If customer data is ever needed for analytics, it must be governed by a Non-Disclosure Agreements and fully anonymized before ingestion. This is out of scope for Sprint 0.

## PII & secrets

- No Direct PII in Graph: The graph will not store sensitive Personally Identifiable Information (PII) like home addresses, personal phone numbers, or social security numbers. Business contact information (e.g., schema:name, schema:email for a schema:Person) is acceptable but must be handled as sensitive. 

- Secrets Management: API keys, database credentials, and other secrets for accessing source systems (like an ERP) must be stored in a dedicated secrets manager and NOT in configuration files or code.

- Redaction Policy: All free-text fields (like notes or descriptions) must not have PII or commercial secrets. In case of Customer data usage, all open-text fields should be scanned for and have PII or commercial secrets redacted before being loaded into the graph. 

- Commercially Sensitive Data: Some data fields like (contractedAmount, unitPrice, endDate etc.) are considered commercially sensitive and must be protected with access controls. Mentioned Access Controls are only required for Customer data.

## Data Quality (DQ) gates (to implement later in ETL)

- Completeness:
  - A PO must have an orderNumber, dateIssued, a single Supplier, and at least one Line_Item.
  - A Supplier must have a legalName and vendorCode.
  - An Invoice must have all its field filled.
  - A Contract must have all its field filled.

- Uniqueness: vendorCode, orderNumber, taxID and invoiceNumber must be unique across all entities of their type.

- Validity:
  - paymentDueDate on an Invoice must occur after the dateCreated. endDate on a Contract must be after the startDate.
  - orderTotalValue of a PO must be equal to sum of all Line_Item's quantity times unitPrice.

- Referential Integrity: 
  - A PO cannot reference a vendorCode that does not exist as a Supplier.
  - An Invoice must reference an existing PO.

- Format Consistency: All date fields must conform to ISO 8601 format (YYYY-MM-DD). All monetary values must be in a consistent currency or have a currency field attached.

- Logical Consistency:
  - The sum of all lineTotal values on a PO should equal the orderTotalValue.

## Retention & access

- Retention Policy: Active procurement documents from Customer Data (Contracts, POs, Invoices) will be retained for 5 years after the closing date (e.g., final payment date or contract end date) to meet financial audit requirements. After 5 years, data will be archived.

- Access Control: Access will be role-based.

- Read-Only Analyst: Can query all data but cannot modify it. Cannot export raw data containing commercially sensitive information.

- Data Engineer / Database Admin: Full administrative access to the graph structure to all data and data ingestion pipelines.

- Default Access: Deny all by default. Access must be explicitly granted.

## Approvals

- Schema Changes: Any changes to the ontology (new entities, properties, or relationships) must be reviewed and approved by the Data Governance Board (or a designated lead architect).

- Data Access Requests: All requests for access must be submitted through a formal ticketing system, stating the business justification. Requests must be approved by the data owner (e.g., Project Manager).

- Bulk Data Export: Any request to export more than 1,000 records must be approved by the data owner. The purpose and destination of the data must be logged for audit purposes.

- New Data Source Onboarding: Before a new data source (e.g., a new ERP, a new supplier portal) is integrated, it must be reviewed by the Data Governance Board to ensure it meets the quality and security standards outlined in this checklist.