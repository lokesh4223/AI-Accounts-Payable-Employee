# AI Accounts Payable Employee - Data Models

## Overview

This document describes the data models used in the AI Accounts Payable Employee system. The data models support the core functionality of invoice processing, vendor management, approval workflows, and audit trails.

## Database Schema

### Core Entities

#### 1. Vendors Table
Stores vendor information and related details.

```sql
CREATE TABLE vendors (
    vendor_id VARCHAR(50) PRIMARY KEY,
    vendor_name VARCHAR(255) NOT NULL,
    legal_name VARCHAR(255),
    tax_id VARCHAR(50),
    vat_number VARCHAR(50),
    status ENUM('ACTIVE', 'BLOCKED', 'INACTIVE') DEFAULT 'ACTIVE',
    risk_level ENUM('LOW', 'MEDIUM', 'HIGH') DEFAULT 'LOW',
    bank_details JSON, -- Stores account number, sort code, IBAN, etc.
    contact_info JSON, -- Stores primary contact, email, phone
    payment_terms VARCHAR(50), -- e.g., NET30, NET60
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    categories JSON, -- Array of vendor categories
    preferred_payment_method VARCHAR(20) -- e.g., BACS, CHAPS, WIRE
);
```

**Sample Data:**
```json
{
  "vendor_id": "VEND-ACME-001",
  "vendor_name": "Acme Corporation Ltd",
  "legal_name": "Acme Corporation Limited",
  "tax_id": "GB123456789",
  "vat_number": "GB123456789",
  "status": "ACTIVE",
  "risk_level": "LOW",
  "bank_details": {
    "account_number": "12345678",
    "sort_code": "01-02-03",
    "account_name": "Acme Corporation Ltd",
    "iban": "GB29NWBK60161331926819",
    "bic": "NWBKGB2L"
  },
  "contact_info": {
    "primary_contact": "John Smith",
    "email": "accounts@acme-corp.com",
    "phone": "+44 20 1234 5678"
  },
  "payment_terms": "NET30",
  "categories": ["software", "consulting"],
  "preferred_payment_method": "BACS"
}
```

#### 2. Invoices Table
Stores invoice details and processing status.

```sql
CREATE TABLE invoices (
    invoice_id VARCHAR(50) PRIMARY KEY,
    vendor_id VARCHAR(50) NOT NULL,
    invoice_number VARCHAR(100) NOT NULL,
    invoice_date DATE NOT NULL,
    due_date DATE,
    amount DECIMAL(15,2) NOT NULL,
    currency CHAR(3) DEFAULT 'USD',
    po_number VARCHAR(50), -- Reference to purchase order
    gr_number VARCHAR(50), -- Reference to goods receipt
    status ENUM('RECEIVED', 'EXTRACTED', 'VALIDATED', 'MATCHED', 'APPROVED', 'PAID', 'REJECTED', 'DUPLICATE') DEFAULT 'RECEIVED',
    file_path VARCHAR(500), -- Path to original invoice file
    extracted_data JSON, -- Structured data from OCR
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    processed_at TIMESTAMP NULL,
    approved_at TIMESTAMP NULL,
    paid_at TIMESTAMP NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);
```

**Sample Data:**
```json
{
  "invoice_id": "INV-2026-001",
  "vendor_id": "VEND-ACME-001",
  "invoice_number": "ACME-INV-001",
  "invoice_date": "2026-01-15",
  "due_date": "2026-02-14",
  "amount": 1250.75,
  "currency": "USD",
  "po_number": "PO-2026-001",
  "gr_number": "GR-2026-001",
  "status": "APPROVED",
  "file_path": "/invoices/2026/01/acme-inv-001.pdf",
  "extracted_data": {
    "vendor_name": "Acme Corporation Ltd",
    "invoice_number": "ACME-INV-001",
    "invoice_date": "2026-01-15",
    "due_date": "2026-02-14",
    "amount": 1250.75,
    "currency": "USD",
    "line_items": [
      {
        "description": "Software License",
        "quantity": 1,
        "unit_price": 1000.00,
        "total": 1000.00
      },
      {
        "description": "Setup Fee",
        "quantity": 1,
        "unit_price": 250.75,
        "total": 250.75
      }
    ]
  }
}
```

#### 3. Purchase Orders Table
Stores purchase order information for matching purposes.

```sql
CREATE TABLE purchase_orders (
    po_id VARCHAR(50) PRIMARY KEY,
    po_number VARCHAR(100) NOT NULL,
    vendor_id VARCHAR(50) NOT NULL,
    po_date DATE NOT NULL,
    po_amount DECIMAL(15,2) NOT NULL,
    currency CHAR(3) DEFAULT 'USD',
    status ENUM('OPEN', 'PARTIAL', 'CLOSED', 'CANCELLED') DEFAULT 'OPEN',
    line_items JSON, -- Detailed line item information
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    closed_at TIMESTAMP NULL,
    FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
);
```

**Sample Data:**
```json
{
  "po_id": "PO-2026-001",
  "po_number": "PO-2026-001",
  "vendor_id": "VEND-ACME-001",
  "po_date": "2025-12-15",
  "po_amount": 1250.00,
  "currency": "USD",
  "status": "CLOSED",
  "line_items": [
    {
      "item_code": "SW-001",
      "description": "Software License",
      "quantity_ordered": 1,
      "unit_price": 1000.00,
      "total_amount": 1000.00
    },
    {
      "item_code": "SETUP-001",
      "description": "Setup Fee",
      "quantity_ordered": 1,
      "unit_price": 250.00,
      "total_amount": 250.00
    }
  ]
}
```

#### 4. Goods Receipts Table
Stores goods receipt information for 3-way matching.

```sql
CREATE TABLE goods_receipts (
    gr_id VARCHAR(50) PRIMARY KEY,
    gr_number VARCHAR(100) NOT NULL,
    po_id VARCHAR(50) NOT NULL,
    gr_date DATE NOT NULL,
    status ENUM('CONFIRMED', 'DISCREPANCIES', 'PENDING') DEFAULT 'PENDING',
    received_items JSON, -- Items received with quantities
    discrepancies JSON, -- Any discrepancies found
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (po_id) REFERENCES purchase_orders(po_id)
);
```

**Sample Data:**
```json
{
  "gr_id": "GR-2026-001",
  "gr_number": "GR-2026-001",
  "po_id": "PO-2026-001",
  "gr_date": "2026-01-10",
  "status": "CONFIRMED",
  "received_items": [
    {
      "item_code": "SW-001",
      "description": "Software License",
      "quantity_received": 1,
      "received_date": "2026-01-10"
    },
    {
      "item_code": "SETUP-001",
      "description": "Setup Fee",
      "quantity_received": 1,
      "received_date": "2026-01-10"
    }
  ],
  "discrepancies": null
}
```

#### 5. Approval Workflows Table
Manages approval processes and routing.

```sql
CREATE TABLE approval_workflows (
    approval_id VARCHAR(50) PRIMARY KEY,
    invoice_id VARCHAR(50) NOT NULL,
    approval_sequence INT NOT NULL,
    approver_user_id VARCHAR(50) NOT NULL,
    approval_status ENUM('PENDING', 'APPROVED', 'REJECTED', 'SKIPPED') DEFAULT 'PENDING',
    approval_required_amount DECIMAL(15,2), -- Threshold that triggered this approval
    comments TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices(invoice_id)
);
```

**Sample Data:**
```json
{
  "approval_id": "APP-2026-001-01",
  "invoice_id": "INV-2026-001",
  "approval_sequence": 1,
  "approver_user_id": "USER-001",
  "approval_status": "APPROVED",
  "approval_required_amount": 1000.00,
  "comments": "Approved per department budget allocation",
  "approved_at": "2026-01-16 10:30:00"
}
```

#### 6. Audit Logs Table
Maintains comprehensive audit trails.

```sql
CREATE TABLE audit_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    entity_type ENUM('INVOICE', 'VENDOR', 'APPROVAL', 'PAYMENT', 'USER', 'SYSTEM') NOT NULL,
    entity_id VARCHAR(50) NOT NULL,
    action_type ENUM('CREATE', 'UPDATE', 'DELETE', 'APPROVE', 'REJECT', 'VIEW', 'EXPORT', 'IMPORT') NOT NULL,
    user_id VARCHAR(50), -- NULL for system actions
    ip_address VARCHAR(45), -- Supports IPv6
    user_agent TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    details JSON, -- Additional context for the action
    session_id VARCHAR(100)
);
```

**Sample Data:**
```json
{
  "entity_type": "INVOICE",
  "entity_id": "INV-2026-001",
  "action_type": "APPROVE",
  "user_id": "USER-001",
  "ip_address": "192.168.1.100",
  "timestamp": "2026-01-16 10:30:00",
  "details": {
    "previous_status": "VALIDATED",
    "new_status": "APPROVED",
    "reason": "Amount below threshold, auto-approved",
    "approver_role": "department_manager"
  }
}
```

#### 7. Memory Entries Table
Stores structured memory for the AI system.

```sql
CREATE TABLE memory_entries (
    memory_id VARCHAR(50) PRIMARY KEY,
    key_name VARCHAR(255) NOT NULL,
    value JSON NOT NULL,
    memory_type ENUM('SESSION_CONTEXT', 'LONG_TERM', 'EPISODIC', 'SEMANTIC', 'POLICY', 'PATTERN') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    tags JSON, -- Array of tags for categorization
    importance FLOAT DEFAULT 0.5, -- 0.0 to 1.0 scale
    last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

**Sample Data:**
```json
{
  "memory_id": "MEM-2026-001",
  "key_name": "vendor_payment_pattern_ACME",
  "value": {
    "vendor_id": "VEND-ACME-001",
    "avg_payment_time_days": 25,
    "preferred_payment_method": "BACS",
    "payment_history": [
      {"date": "2025-12-20", "amount": 1100.00},
      {"date": "2026-01-20", "amount": 1250.75}
    ]
  },
  "memory_type": "PATTERN",
  "expires_at": "2027-01-01 00:00:00",
  "tags": ["vendor", "payment", "pattern"],
  "importance": 0.8
}
```

## Indexes for Performance

```sql
-- Indexes for fast lookups
CREATE INDEX idx_invoices_status ON invoices(status);
CREATE INDEX idx_invoices_vendor ON invoices(vendor_id);
CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_po_number ON invoices(po_number);

CREATE INDEX idx_vendors_status ON vendors(status);
CREATE INDEX idx_vendors_name ON vendors(vendor_name);

CREATE INDEX idx_approvals_invoice ON approval_workflows(invoice_id);
CREATE INDEX idx_approvals_status ON approval_workflows(approval_status);

CREATE INDEX idx_audit_entity ON audit_logs(entity_id, entity_type);
CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp);

CREATE INDEX idx_memory_type ON memory_entries(memory_type);
CREATE INDEX idx_memory_expires ON memory_entries(expires_at);
```

## Relationships

```
[VEN0ORS] 1---* [INVOICES]
[INVOICES] 1---* [APPROVAL_WORKFLOWS]
[INVOICES] --- [PURCHASE_ORDERS] (via po_number)
[INVOICES] --- [GOODS_RECEIPTS] (via gr_number)
[PURCHASE_ORDERS] 1---* [GOODS_RECEIPTS]

[AUDIT_LOGS] links to all entities
[MEMORY_ENTRIES] stores AI system memory
```

## Data Integrity Constraints

1. **Referential Integrity**: Foreign key constraints maintain relationship consistency
2. **Domain Constraints**: Enumerated values for status fields ensure data validity
3. **Check Constraints**: Amounts must be positive, dates must be valid
4. **Unique Constraints**: Invoice numbers per vendor, PO numbers, GR numbers
5. **Temporal Constraints**: Invoice date before due date, approval after creation

## Privacy & Security Considerations

1. **PII Protection**: Sensitive data in JSON fields encrypted at rest
2. **Access Logging**: All data access logged for audit purposes
3. **Retention Policies**: Automatic cleanup of temporary data
4. **GDPR Compliance**: Right to deletion and data portability support
5. **Masking**: Sensitive fields masked in application layer