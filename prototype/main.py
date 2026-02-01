import json
import datetime
from enum import Enum
from typing import Dict, List, Optional

class AgentType(Enum):
    VALIDATION_AGENT = "validation_agent"
    MATCHING_AGENT = "matching_agent"
    PAYMENT_AGENT = "payment_agent"
    EXCEPTION_AGENT = "exception_agent"
    APPROVAL_AGENT = "approval_agent"
    COMMUNICATION_AGENT = "communication_agent"

class InvoiceStatus(Enum):
    RECEIVED = "received"
    VALIDATED = "validated"
    DUPLICATE_DETECTED = "duplicate_detected"
    MISSING_PO = "missing_po"
    MATCH_FAILED = "match_failed"
    APPROVAL_PENDING = "approval_pending"
    APPROVED = "approved"
    PROCESSED = "processed"
    ESCALATED = "escalated"
    REJECTED = "rejected"

class Invoice:
    def __init__(self, invoice_data: Dict):
        self.invoice_id = invoice_data["invoice_id"]
        self.vendor_name = invoice_data["vendor_name"]
        self.invoice_date = invoice_data["invoice_date"]
        self.amount = invoice_data["amount"]
        self.currency = invoice_data["currency"]
        self.po_number = invoice_data.get("po_number")
        self.vat_amount = invoice_data.get("vat_amount", 0.0)
        self.due_date = invoice_data["due_date"]
        self.line_items = invoice_data.get("line_items", [])
        self.vendor_details = invoice_data.get("vendor_details", {})
        self.status = InvoiceStatus.RECEIVED
        self.processing_log: List[Dict] = []
        self.approved_by = None
        self.approval_notes = ""
        
    def log_action(self, agent: AgentType, action: str, reason: str, outcome: str):
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "agent": agent.value,
            "action": action,
            "reason": reason,
            "outcome": outcome,
            "status_before": self.status.name,
            "status_after": None
        }
        self.processing_log.append(log_entry)
        print(f"[LOG] {log_entry['timestamp']} - {agent.value}: {action} -> {outcome}")
        
    def update_status(self, new_status: InvoiceStatus):
        old_status = self.status
        self.status = new_status
        # Update the last log entry with status change
        if self.processing_log:
            self.processing_log[-1]["status_after"] = new_status.name
        print(f"   Status: {old_status.name} -> {new_status.name}")

class AIAgent:
    def __init__(self, agent_type: AgentType):
        self.agent_type = agent_type
        
    def process_invoice(self, invoice: Invoice) -> bool:
        raise NotImplementedError("Subclasses must implement process_invoice")

class ValidationAgent(AIAgent):
    def __init__(self):
        super().__init__(AgentType.VALIDATION_AGENT)
    
    def process_invoice(self, invoice: Invoice) -> bool:
        invoice.log_action(
            self.agent_type,
            "validate_invoice",
            "Checking invoice authenticity and compliance",
            "valid"
        )
        
        # Simulate validation checks
        if invoice.amount <= 0:
            invoice.log_action(
                self.agent_type,
                "validate_invoice",
                "Invalid amount detected",
                "invalid"
            )
            return False
            
        if not invoice.vendor_name.strip():
            invoice.log_action(
                self.agent_type,
                "validate_invoice",
                "Missing vendor name",
                "invalid"
            )
            return False
        
        # VAT validation
        if invoice.vat_amount > invoice.amount * 0.25:  # Assuming max 25% VAT
            invoice.log_action(
                self.agent_type,
                "validate_vat",
                "VAT amount exceeds reasonable threshold",
                "vat_validation_failed"
            )
            return False
            
        invoice.update_status(InvoiceStatus.VALIDATED)
        return True

class MatchingAgent(AIAgent):
    def __init__(self):
        super().__init__(AgentType.MATCHING_AGENT)
        # Simulated existing invoices for duplicate detection
        self.existing_invoices = set()
        self.purchase_orders = {
            "PO-001": {"vendor": "Acme Corp", "amount": 1500.00, "expected_delivery_date": "2026-01-20"},
            "PO-002": {"vendor": "Globex Inc", "amount": 2300.00, "expected_delivery_date": "2026-01-25"}
        }
        # Simulated goods receipts
        self.goods_receipts = {
            "PO-001": {"received_quantity": 1, "delivered_date": "2026-01-18"},
            "PO-002": {"received_quantity": 1, "delivered_date": "2026-01-22"}
        }
    
    def process_invoice(self, invoice: Invoice) -> bool:
        # Check for duplicates
        invoice_key = f"{invoice.vendor_name}_{invoice.amount}"
        if invoice_key in self.existing_invoices:
            invoice.log_action(
                self.agent_type,
                "check_duplicates",
                "Duplicate invoice detected",
                "duplicate_found"
            )
            invoice.update_status(InvoiceStatus.DUPLICATE_DETECTED)
            return False
        
        # Add to existing invoices to prevent future duplicates
        self.existing_invoices.add(invoice_key)
        
        # Check for purchase order
        if not invoice.po_number:
            invoice.log_action(
                self.agent_type,
                "check_po_match",
                "No purchase order found",
                "missing_po"
            )
            invoice.update_status(InvoiceStatus.MISSING_PO)
            return False
        
        # Check if PO exists and matches
        if invoice.po_number in self.purchase_orders:
            po_info = self.purchase_orders[invoice.po_number]
            if po_info["vendor"].lower() != invoice.vendor_name.lower():
                invoice.log_action(
                    self.agent_type,
                    "check_po_match",
                    "Vendor mismatch with PO",
                    "match_failed"
                )
                invoice.update_status(InvoiceStatus.MATCH_FAILED)
                return False
            elif abs(po_info["amount"] - invoice.amount) > 0.01:
                invoice.log_action(
                    self.agent_type,
                    "check_po_match",
                    "Amount mismatch with PO",
                    "match_failed"
                )
                invoice.update_status(InvoiceStatus.MATCH_FAILED)
                return False
        else:
            invoice.log_action(
                self.agent_type,
                "check_po_match",
                "Purchase order not found",
                "match_failed"
            )
            invoice.update_status(InvoiceStatus.MATCH_FAILED)
            return False
        
        # Check goods receipt (for 3-way matching)
        if invoice.po_number in self.goods_receipts:
            gr_info = self.goods_receipts[invoice.po_number]
            # Simulate quantity matching
            if len(invoice.line_items) > 0:
                total_quantity = sum(item.get('quantity', 0) for item in invoice.line_items)
                if total_quantity != gr_info['received_quantity']:
                    invoice.log_action(
                        self.agent_type,
                        "check_gr_match",
                        "Quantity mismatch with goods receipt",
                        "match_failed"
                    )
                    invoice.update_status(InvoiceStatus.MATCH_FAILED)
                    return False
        else:
            invoice.log_action(
                self.agent_type,
                "check_gr_match",
                "Goods receipt not found for 3-way match",
                "match_failed"
            )
            invoice.update_status(InvoiceStatus.MATCH_FAILED)
            return False
        
        # VAT validation
        if invoice.vat_amount > invoice.amount * 0.25:  # Assuming max 25% VAT
            invoice.log_action(
                self.agent_type,
                "validate_vat",
                "VAT amount exceeds reasonable threshold",
                "vat_validation_failed"
            )
            invoice.update_status(InvoiceStatus.MATCH_FAILED)
            return False
        
        invoice.log_action(
            self.agent_type,
            "3_way_match",
            "Successfully matched PO, Invoice, and Receipt",
            "matched"
        )
        return True

class PaymentAgent(AIAgent):
    def __init__(self):
        super().__init__(AgentType.PAYMENT_AGENT)
    
    def process_invoice(self, invoice: Invoice) -> bool:
        # Simulate payment processing
        invoice.log_action(
            self.agent_type,
            "process_payment",
            f"Processing payment of {invoice.amount} {invoice.currency}",
            "payment_initiated"
        )
        
        # Simulate bank transfer
        invoice.log_action(
            self.agent_type,
            "bank_transfer",
            "Transfer initiated to vendor bank account",
            "transfer_completed"
        )
        
        # Update ERP system
        invoice.log_action(
            self.agent_type,
            "update_erp",
            "ERP system updated with payment information",
            "erp_updated"
        )
        
        invoice.update_status(InvoiceStatus.PROCESSED)
        return True

class ExceptionAgent(AIAgent):
    def __init__(self):
        super().__init__(AgentType.EXCEPTION_AGENT)
    
    def process_invoice(self, invoice: Invoice) -> bool:
        # Handle different exception types
        if invoice.status == InvoiceStatus.MISSING_PO:
            invoice.log_action(
                self.agent_type,
                "handle_missing_po",
                "Routing to procurement for PO verification",
                "escalated_to_procurement"
            )
            # Draft communication to procurement
            print("   📧 Drafting email to procurement: Please create PO for invoice {invoice.invoice_id}")
        elif invoice.status == InvoiceStatus.MATCH_FAILED:
            invoice.log_action(
                self.agent_type,
                "handle_match_failure",
                "Routing to AP manager for manual review",
                "escalated_to_manager"
            )
            # Draft communication to manager
            print("   📧 Drafting email to AP manager: 3-way match failed for invoice {invoice.invoice_id}")
        elif invoice.status == InvoiceStatus.DUPLICATE_DETECTED:
            invoice.log_action(
                self.agent_type,
                "handle_duplicate",
                "Flagging duplicate and notifying AP team",
                "duplicate_flagged"
            )
            # Draft communication about duplicate
            print("   📧 Drafting notification: Duplicate invoice detected for {invoice.invoice_id}")
        elif invoice.status == InvoiceStatus.REJECTED:
            invoice.log_action(
                self.agent_type,
                "handle_rejection",
                "Processing rejected invoice",
                "rejection_handled"
            )
        
        invoice.update_status(InvoiceStatus.ESCALATED)
        return True

class ApprovalAgent(AIAgent):
    def __init__(self):
        super().__init__(AgentType.APPROVAL_AGENT)
        # Simulated approval rules based on amount
        self.approval_thresholds = {
            "manager": 1000,
            "director": 5000,
            "cfo": 10000
        }
    
    def process_invoice(self, invoice: Invoice) -> bool:
        # Determine approval level based on amount
        if invoice.amount >= self.approval_thresholds["cfo"]:
            required_approval = "CFO"
        elif invoice.amount >= self.approval_thresholds["director"]:
            required_approval = "Director"
        elif invoice.amount >= self.approval_thresholds["manager"]:
            required_approval = "Manager"
        else:
            # Small amounts auto-approved
            invoice.log_action(
                self.agent_type,
                "auto_approve",
                f"Invoice under manager threshold ({self.approval_thresholds['manager']})",
                "auto_approved"
            )
            invoice.update_status(InvoiceStatus.APPROVED)
            return True
        
        invoice.log_action(
            self.agent_type,
            "request_approval",
            f"Requesting {required_approval} approval for amount {invoice.amount}",
            "approval_requested"
        )
        
        # Simulate approval process
        # In a real system, this would wait for actual approval
        invoice.update_status(InvoiceStatus.APPROVAL_PENDING)
        
        # For demo purposes, simulate approval
        invoice.log_action(
            self.agent_type,
            "simulate_approval",
            f"{required_approval} approved invoice",
            "approved"
        )
        invoice.approved_by = required_approval
        invoice.update_status(InvoiceStatus.APPROVED)
        return True

class CommunicationAgent(AIAgent):
    def __init__(self):
        super().__init__(AgentType.COMMUNICATION_AGENT)
    
    def process_invoice(self, invoice: Invoice) -> bool:
        # Draft appropriate communication based on status
        if invoice.status == InvoiceStatus.APPROVED:
            invoice.log_action(
                self.agent_type,
                "send_payment_confirmation",
                "Sending payment confirmation to vendor",
                "confirmation_sent"
            )
            print(f"   📧 Email drafted to {invoice.vendor_details.get('primary_contact_email', 'vendor')}: Payment scheduled for {invoice.due_date}")
        elif invoice.status == InvoiceStatus.ESCALATED:
            invoice.log_action(
                self.agent_type,
                "send_exception_notification",
                "Sending exception notification to relevant parties",
                "notification_sent"
            )
            print(f"   📧 Email drafted to AP team: Exception raised for invoice {invoice.invoice_id}")
        
        return True

class AIAPOrchestrator:
    def __init__(self):
        self.validation_agent = ValidationAgent()
        self.matching_agent = MatchingAgent()
        self.payment_agent = PaymentAgent()
        self.exception_agent = ExceptionAgent()
        self.approval_agent = ApprovalAgent()
        self.communication_agent = CommunicationAgent()
    
    def process_invoice(self, invoice_data: Dict) -> Invoice:
        invoice = Invoice(invoice_data)
        
        print(f"\n🤖 Starting AI AP Employee processing for invoice {invoice.invoice_id}")
        print(f"   Vendor: {invoice.vendor_name}")
        print(f"   Amount: {invoice.amount} {invoice.currency}")
        print(f"   Due Date: {invoice.due_date}")
        
        # Plan Phase: Determine processing steps
        invoice.log_action(
            AgentType.VALIDATION_AGENT,
            "planning",
            "Initializing invoice processing workflow",
            "workflow_started"
        )
        
        # Main Processing Loop - Plan → Act → Observe → Validate → Recover → Complete
        processing_complete = False
        retry_count = 0
        max_retries = 3
        
        while not processing_complete and retry_count < max_retries:
            try:
                # Act Phase: Execute validation
                if self.validation_agent.process_invoice(invoice):
                    # Validation passed, proceed to matching
                    if self.matching_agent.process_invoice(invoice):
                        # Matching succeeded, proceed to approval
                        if self.approval_agent.process_invoice(invoice):
                            # Approved, proceed to payment
                            if self.payment_agent.process_invoice(invoice):
                                # Payment processed successfully
                                processing_complete = True
                                
                                # Send communication
                                self.communication_agent.process_invoice(invoice)
                            else:
                                # Payment failed
                                invoice.log_action(
                                    AgentType.PAYMENT_AGENT,
                                    "payment_failed",
                                    "Payment processing failed",
                                    "retry_needed"
                                )
                                retry_count += 1
                        else:
                            # Approval failed
                            invoice.log_action(
                                AgentType.APPROVAL_AGENT,
                                "approval_failed",
                                "Approval process failed",
                                "escalation_needed"
                            )
                            processing_complete = True
                            self.exception_agent.process_invoice(invoice)
                    else:
                        # Matching failed, handle exception
                        if invoice.status in [InvoiceStatus.MISSING_PO, InvoiceStatus.MATCH_FAILED, InvoiceStatus.DUPLICATE_DETECTED]:
                            processing_complete = True
                            self.exception_agent.process_invoice(invoice)
                else:
                    # Validation failed, handle exception
                    processing_complete = True
                    self.exception_agent.process_invoice(invoice)
                    
            except Exception as e:
                # Recover Phase: Handle unexpected errors
                invoice.log_action(
                    AgentType.VALIDATION_AGENT,
                    "error_recovery",
                    f"Unexpected error: {str(e)}",
                    "recovery_attempted"
                )
                
                if retry_count < max_retries:
                    retry_count += 1
                    invoice.log_action(
                        AgentType.VALIDATION_AGENT,
                        "retry_processing",
                        f"Retrying processing (attempt {retry_count}/{max_retries})",
                        "retry_initiated"
                    )
                else:
                    invoice.log_action(
                        AgentType.VALIDATION_AGENT,
                        "max_retries_exceeded",
                        "Max retries exceeded, escalating to human",
                        "escalated_to_human"
                    )
                    invoice.update_status(InvoiceStatus.ESCALATED)
                    processing_complete = True
        
        # Complete Phase: Finalize processing
        invoice.log_action(
            AgentType.VALIDATION_AGENT,
            "completion",
            "Invoice processing completed",
            f"final_status_{invoice.status.value}"
        )
        
        return invoice

def main():
    # Load sample invoice data
    with open("../data/sample_invoice.json", "r") as f:
        sample_invoice_data = json.load(f)
    
    # Initialize orchestrator
    orchestrator = AIAPOrchestrator()
    
    print("🤖 AI AP EMPLOYEE v1.0")
    print("="*30)
    
    # Process the invoice
    print("📦 Processing normal invoice...")
    processed_invoice = orchestrator.process_invoice(sample_invoice_data)
    
    # Create a scenario for missing PO
    print("🔍 Testing missing PO scenario...")
    missing_po_invoice = sample_invoice_data.copy()
    missing_po_invoice["invoice_id"] = "INV-2026-002"
    missing_po_invoice["po_number"] = None  # No PO
    missing_po_invoice["description"] = "Invoice without purchase order"
    
    processed_missing_po = orchestrator.process_invoice(missing_po_invoice)
    
    # Create a scenario for duplicate invoice
    print("🔄 Testing duplicate detection...")
    duplicate_invoice = sample_invoice_data.copy()
    duplicate_invoice["invoice_id"] = "INV-2026-003"
    duplicate_invoice["description"] = "Potential duplicate invoice"
    
    # Process the same invoice again to trigger duplicate detection
    processed_duplicate = orchestrator.process_invoice(sample_invoice_data)
    
    # Save processing logs
    all_logs = processed_invoice.processing_log + processed_missing_po.processing_log + processed_duplicate.processing_log
    with open("sample_logs.json", "w") as f:
        json.dump(all_logs, f, indent=2)
    
    # Summary output
    print(f"\n✅ DONE! Processed 3 invoices")
    print(f"📊 Status: Normal={processed_invoice.status.value}, MissingPO={processed_missing_po.status.value}, Dup={processed_duplicate.status.value}")

if __name__ == "__main__":
    main()