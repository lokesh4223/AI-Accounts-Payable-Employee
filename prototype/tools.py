"""
Mock tools and utilities for the AI system
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class EmailMessage:
    """Represents an email message"""
    sender: str
    subject: str
    body: str
    attachments: List[Dict[str, str]]
    received_at: datetime
    message_id: str


class MockEmailClient:
    """Mock email client for processing incoming invoice emails"""
    
    def __init__(self):
        self.inbox = []
        self.connected = False
    
    async def connect(self):
        """Connect to the email server"""
        print("[MOCK] Connected to email server")
        self.connected = True
        return True
    
    async def disconnect(self):
        """Disconnect from the email server"""
        self.connected = False
        print("[MOCK] Disconnected from email server")
        return True
    
    async def get_unread_messages(self, folder: str = "INBOX") -> List[EmailMessage]:
        """Get unread email messages from the specified folder"""
        if not self.connected:
            raise Exception("Email client not connected")
        
        # Simulate fetching unread messages
        mock_messages = [
            EmailMessage(
                sender="accounts@acme-corp.com",
                subject="Invoice ACME-2026-001 for Software Services",
                body="Please find attached invoice for services rendered.",
                attachments=[{"filename": "ACME-INV-2026-001.pdf", "size": "2.3MB"}],
                received_at=datetime.now(),
                message_id="msg_001"
            ),
            EmailMessage(
                sender="billing@global-tech.com",
                subject="Invoice GTECH-2026-002 - Monthly Subscription",
                body="Monthly subscription invoice attached.",
                attachments=[{"filename": "GTECH-INV-2026-002.pdf", "size": "1.8MB"}],
                received_at=datetime.now(),
                message_id="msg_002"
            )
        ]
        
        return mock_messages[:2]  # Return first 2 messages
    
    async def mark_as_read(self, message_ids: List[str]):
        """Mark messages as read"""
        print(f"[MOCK] Marked {len(message_ids)} messages as read")
        return True


class MockOCRProcessor:
    """Mock OCR processor for extracting text from documents"""
    
    def __init__(self):
        self.processed_documents = 0
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document and extract text/content"""
        # Simulate OCR processing
        await asyncio.sleep(0.1)  # Simulate processing time
        
        self.processed_documents += 1
        
        # Mock extracted data based on filename
        if "ACME" in file_path:
            return {
                "text_content": "ACME CORPORATION LTD\nInvoice Number: ACME-2026-001\nDate: 2026-01-15\nAmount: $1,250.75\nPO Number: PO-2026-001",
                "confidence_score": 0.92,
                "metadata": {
                    "page_count": 1,
                    "language": "en",
                    "format": "PDF"
                },
                "extracted_fields": {
                    "vendor_name": "Acme Corporation Ltd",
                    "invoice_number": "ACME-2026-001",
                    "invoice_date": "2026-01-15",
                    "amount": 1250.75,
                    "currency": "USD",
                    "po_number": "PO-2026-001"
                }
            }
        elif "GTECH" in file_path:
            return {
                "text_content": "GLOBAL TECH SOLUTIONS\nInvoice Number: GTECH-2026-002\nDate: 2026-01-16\nAmount: $895.00\nPO Number: PO-2026-002",
                "confidence_score": 0.89,
                "metadata": {
                    "page_count": 1,
                    "language": "en",
                    "format": "PDF"
                },
                "extracted_fields": {
                    "vendor_name": "Global Tech Solutions",
                    "invoice_number": "GTECH-2026-002",
                    "invoice_date": "2026-01-16",
                    "amount": 895.00,
                    "currency": "USD",
                    "po_number": "PO-2026-002"
                }
            }
        else:
            return {
                "text_content": "SAMPLE INVOICE DATA",
                "confidence_score": 0.95,
                "metadata": {
                    "page_count": 1,
                    "language": "en",
                    "format": "PDF"
                },
                "extracted_fields": {
                    "vendor_name": "Sample Vendor Inc",
                    "invoice_number": "SAMPLE-001",
                    "invoice_date": "2026-01-15",
                    "amount": 1000.00,
                    "currency": "USD",
                    "po_number": "SAMPLE-PO-001"
                }
            }
    
    async def get_processing_stats(self) -> Dict[str, int]:
        """Get OCR processing statistics"""
        return {
            "documents_processed": self.processed_documents,
            "average_confidence": 0.92,
            "last_processed": datetime.now().isoformat()
        }


class MockERPSync:
    """Mock ERP synchronization for interfacing with accounting systems"""
    
    def __init__(self):
        self.sync_operations = 0
        self.invoices_synced = []
    
    async def connect(self):
        """Connect to ERP system"""
        print("[MOCK] Connected to ERP system")
        return True
    
    async def sync_invoice(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Sync invoice data to ERP system"""
        await asyncio.sleep(0.05)  # Simulate network delay
        self.sync_operations += 1
        
        # Simulate ERP response
        erp_response = {
            "erp_invoice_id": f"ERP-{invoice_data.get('invoice_number', 'UNKNOWN')}",
            "sync_status": "SUCCESS",
            "sync_timestamp": datetime.now().isoformat(),
            "gl_codes_assigned": True,
            "purchase_order_linked": invoice_data.get("po_number") is not None
        }
        
        self.invoices_synced.append(erp_response)
        
        return erp_response
    
    async def get_vendor_info(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """Get vendor information from ERP"""
        await asyncio.sleep(0.02)  # Simulate network delay
        
        # Mock vendor data
        mock_vendors = {
            "ACME-001": {
                "vendor_name": "Acme Corporation Ltd",
                "status": "ACTIVE",
                "payment_terms": "NET30",
                "tax_id": "GB123456789",
                "risk_level": "LOW"
            },
            "GTECH-002": {
                "vendor_name": "Global Tech Solutions",
                "status": "ACTIVE",
                "payment_terms": "NET45",
                "tax_id": "US987654321",
                "risk_level": "MEDIUM"
            }
        }
        
        return mock_vendors.get(vendor_id)
    
    async def create_purchase_order(self, po_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a purchase order in ERP"""
        await asyncio.sleep(0.05)
        
        po_response = {
            "po_number": f"ERP-PO-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "status": "CREATED",
            "created_at": datetime.now().isoformat()
        }
        
        return po_response


class MockBankingInterface:
    """Mock banking interface for payment preparation"""
    
    def __init__(self):
        self.payment_preparations = 0
        self.bank_connections = []
    
    async def connect(self):
        """Connect to banking system"""
        print("[MOCK] Connected to banking system")
        connection_id = f"BANK_CONN_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.bank_connections.append(connection_id)
        return {"connection_id": connection_id, "status": "CONNECTED"}
    
    async def prepare_payment_file(self, payment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare payment file for transmission to bank"""
        await asyncio.sleep(0.1)  # Simulate processing
        self.payment_preparations += 1
        
        # Generate mock payment file
        payment_file = {
            "payment_reference": f"PMT-{payment_data.get('invoice_id', 'UNKNOWN')}-{datetime.now().strftime('%Y%m%d')}",
            "file_name": f"payment_{payment_data.get('invoice_id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xml",
            "file_size_kb": 15,
            "payment_amount": payment_data.get("amount"),
            "currency": payment_data.get("currency", "USD"),
            "beneficiary_details": payment_data.get("vendor_bank_details", {}),
            "creation_timestamp": datetime.now().isoformat(),
            "checksum": "A1B2C3D4E5F6"
        }
        
        return payment_file
    
    async def validate_bank_details(self, bank_details: Dict[str, str]) -> Dict[str, Any]:
        """Validate bank account details"""
        await asyncio.sleep(0.05)
        
        # Simple validation mock
        validation_result = {
            "account_valid": len(bank_details.get("account_number", "")) >= 6,
            "sort_code_valid": len(bank_details.get("sort_code", "")) >= 5,
            "iban_valid": bank_details.get("iban", "").startswith("GB") if bank_details.get("iban") else True,
            "validation_timestamp": datetime.now().isoformat(),
            "risk_assessment": "LOW"  # For demo purposes
        }
        
        return validation_result


class MockVendorDatabase:
    """Mock vendor database for vendor information lookup"""
    
    def __init__(self):
        self.vendors = {
            "VEND-ACME-001": {
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
                "created_at": "2024-01-15",
                "categories": ["software", "consulting"],
                "preferred_payment_method": "BACS"
            },
            "VEND-GTECH-002": {
                "vendor_id": "VEND-GTECH-002",
                "vendor_name": "Global Tech Solutions",
                "legal_name": "Global Tech Solutions Inc",
                "tax_id": "US987654321",
                "vat_number": "US987654321",
                "status": "ACTIVE",
                "risk_level": "MEDIUM",
                "bank_details": {
                    "account_number": "98765432",
                    "sort_code": "04-05-06",
                    "account_name": "Global Tech Solutions Inc",
                    "iban": "US30BOFA28073100223456",
                    "bic": "BOFAUS6S"
                },
                "contact_info": {
                    "primary_contact": "Jane Doe",
                    "email": "billing@global-tech.com",
                    "phone": "+1 212 555 1234"
                },
                "payment_terms": "NET45",
                "created_at": "2024-02-20",
                "categories": ["technology", "support"],
                "preferred_payment_method": "WIRE"
            }
        }
    
    async def get_vendor_by_id(self, vendor_id: str) -> Optional[Dict[str, Any]]:
        """Get vendor information by ID"""
        await asyncio.sleep(0.01)  # Simulate DB lookup
        return self.vendors.get(vendor_id)
    
    async def get_vendor_by_name(self, vendor_name: str) -> Optional[Dict[str, Any]]:
        """Get vendor information by name"""
        await asyncio.sleep(0.01)  # Simulate DB lookup
        for vendor in self.vendors.values():
            if vendor["vendor_name"].lower() == vendor_name.lower():
                return vendor
        return None
    
    async def search_vendors(self, search_term: str) -> List[Dict[str, Any]]:
        """Search vendors by term"""
        await asyncio.sleep(0.02)  # Simulate DB search
        results = []
        for vendor in self.vendors.values():
            if search_term.lower() in vendor["vendor_name"].lower():
                results.append(vendor)
        return results
    
    async def update_vendor_risk_level(self, vendor_id: str, new_risk_level: str) -> bool:
        """Update vendor risk level"""
        if vendor_id in self.vendors:
            self.vendors[vendor_id]["risk_level"] = new_risk_level
            return True
        return False
    
    async def get_vendor_history(self, vendor_id: str) -> List[Dict[str, Any]]:
        """Get vendor payment history"""
        await asyncio.sleep(0.02)  # Simulate DB lookup
        # Mock history data
        return [
            {"date": "2025-12-15", "amount": 1100.00, "status": "PAID"},
            {"date": "2026-01-15", "amount": 1250.75, "status": "PAID"},
            {"date": "2026-02-15", "amount": 950.00, "status": "SCHEDULED"}
        ]


class MockComplianceChecker:
    """Mock compliance checker for business rule validation"""
    
    def __init__(self):
        self.check_count = 0
        self.policies = {
            "duplicate_detection_window_days": 30,
            "max_single_invoice_amount": 10000,
            "requires_po_for_amount_over": 500,
            "mandatory_fields": ["vendor_name", "invoice_number", "amount", "invoice_date"],
            "approval_thresholds": {
                "department_manager": 1000,
                "finance_manager": 5000,
                "cfo": 25000
            }
        }
    
    async def check_compliance(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check invoice compliance against policies"""
        await asyncio.sleep(0.02)  # Simulate processing
        self.check_count += 1
        
        # Perform various compliance checks
        results = {
            "duplicate_check": await self._check_duplicates(invoice_data),
            "amount_validation": await self._validate_amount(invoice_data),
            "required_fields": await self._check_required_fields(invoice_data),
            "po_requirement": await self._check_po_requirement(invoice_data),
            "tax_validation": await self._validate_tax(invoice_data),
            "overall_compliance": True  # Assume compliant for demo
        }
        
        # Overall compliance is true only if all checks pass
        results["overall_compliance"] = all([
            results["duplicate_check"]["no_duplicate"],
            results["amount_validation"]["within_limit"],
            results["required_fields"]["all_present"],
            results["po_requirement"]["compliant"]
        ])
        
        return results
    
    async def _check_duplicates(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check for duplicate invoices"""
        # Mock duplicate detection - assume no duplicates for demo
        return {
            "no_duplicate": True,
            "similar_invoices": [],
            "window_checked_days": self.policies["duplicate_detection_window_days"]
        }
    
    async def _validate_amount(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate invoice amount against policy limits"""
        amount = invoice_data.get("amount", 0)
        return {
            "within_limit": amount <= self.policies["max_single_invoice_amount"],
            "amount": amount,
            "limit": self.policies["max_single_invoice_amount"]
        }
    
    async def _check_required_fields(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check that all required fields are present"""
        missing_fields = []
        for field in self.policies["mandatory_fields"]:
            if not invoice_data.get(field):
                missing_fields.append(field)
        
        return {
            "all_present": len(missing_fields) == 0,
            "missing_fields": missing_fields,
            "required_fields": self.policies["mandatory_fields"]
        }
    
    async def _check_po_requirement(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check if PO is required and present based on amount"""
        amount = invoice_data.get("amount", 0)
        has_po = bool(invoice_data.get("po_number"))
        
        requires_po = amount > self.policies["requires_po_for_amount_over"]
        compliant = not requires_po or has_po
        
        return {
            "compliant": compliant,
            "requires_po": requires_po,
            "has_po": has_po,
            "amount": amount,
            "threshold": self.policies["requires_po_for_amount_over"]
        }
    
    async def _validate_tax(self, invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate tax/VAT compliance"""
        # Mock tax validation
        return {
            "tax_compliant": True,
            "vat_validated": True,
            "tax_id_present": bool(invoice_data.get("vendor_tax_id"))
        }
    
    async def get_policy(self, policy_name: str) -> Any:
        """Get a specific policy value"""
        return self.policies.get(policy_name)


class MockAuditLogger:
    """Mock audit logger for compliance and tracking"""
    
    def __init__(self):
        self.log_entries = []
        self.exported_reports = []
    
    async def log_action(self, action_type: str, entity_type: str, entity_id: str, 
                        user_id: str, details: Dict[str, Any], timestamp: datetime = None):
        """Log an action for audit purposes"""
        if timestamp is None:
            timestamp = datetime.now()
        
        log_entry = {
            "log_id": f"AUDIT-{timestamp.strftime('%Y%m%d_%H%M%S_%f')}",
            "action_type": action_type,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "user_id": user_id,
            "timestamp": timestamp.isoformat(),
            "details": details,
            "ip_address": "127.0.0.1",  # Mock IP
            "user_agent": "AI-AP-Employee/1.0"  # Mock user agent
        }
        
        self.log_entries.append(log_entry)
        return log_entry["log_id"]
    
    async def get_logs(self, entity_type: str = None, entity_id: str = None, 
                      days_back: int = 30) -> List[Dict[str, Any]]:
        """Retrieve audit logs"""
        cutoff_date = datetime.now().timestamp() - (days_back * 24 * 60 * 60)
        
        filtered_logs = [
            log for log in self.log_entries
            if log["timestamp"] >= datetime.fromtimestamp(cutoff_date).isoformat()
            and (not entity_type or log["entity_type"] == entity_type)
            and (not entity_id or log["entity_id"] == entity_id)
        ]
        
        return filtered_logs
    
    async def export_report(self, report_type: str, filters: Dict[str, Any] = None) -> str:
        """Export audit report"""
        report_id = f"REPORT-{report_type}-{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_data = {
            "report_id": report_id,
            "report_type": report_type,
            "generated_at": datetime.now().isoformat(),
            "filters_applied": filters or {},
            "entry_count": len(self.log_entries),
            "logs": self.log_entries[-100:]  # Last 100 entries for demo
        }
        
        self.exported_reports.append(report_data)
        return report_id


class ToolRegistry:
    """Registry to coordinate access to different tools"""
    
    def __init__(self):
        self.email_client = MockEmailClient()
        self.ocr_processor = MockOCRProcessor()
        self.erp_sync = MockERPSync()
        self.banking_interface = MockBankingInterface()
        self.vendor_database = MockVendorDatabase()
        self.compliance_checker = MockComplianceChecker()
        self.audit_logger = MockAuditLogger()
        self.initialized = False
    
    async def initialize_tools(self):
        """Initialize all tools"""
        print("[TOOLS] All mock tools initialized")
        self.initialized = True
        return True
    
    def get_tool(self, tool_name: str):
        """Get a specific tool by name"""
        tools = {
            'email_client': self.email_client,
            'ocr_processor': self.ocr_processor,
            'erp_sync': self.erp_sync,
            'banking_interface': self.banking_interface,
            'vendor_database': self.vendor_database,
            'compliance_checker': self.compliance_checker,
            'audit_logger': self.audit_logger
        }
        return tools.get(tool_name)
    
    async def get_all_tools_status(self) -> Dict[str, bool]:
        """Get status of all tools"""
        return {
            'email_client_connected': self.email_client.connected,
            'erp_connected': True,  # Always true for mock
            'banking_connected': len(self.banking_interface.bank_connections) > 0,
            'initialized': self.initialized
        }