"""
Core agent execution logic implementing the Plan → Act → Observe → Recover → Complete loop
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InvoiceStatus(Enum):
    """Processing status of an invoice"""
    RECEIVED = "received"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    MATCHED = "matched"
    APPROVED = "approved"
    PAID = "paid"
    REJECTED = "rejected"


class AgentType(Enum):
    """Types of agents in the system"""
    INVOICE_CAPTURE = "invoice_capture_agent"
    EXTRACTION = "extraction_agent"
    VALIDATION = "validation_agent"
    MATCHING = "matching_agent"
    APPROVAL = "approval_agent"
    PAYMENT = "payment_agent"


class AgentAction(Enum):
    """Actions performed by agents"""
    CAPTURE_INVOICE = "capture_invoice"
    EXTRACT_DATA = "extract_data"
    VALIDATE_DATA = "validate_data"
    PERFORM_MATCHING = "perform_matching"
    REQUEST_APPROVAL = "request_approval"
    PREPARE_PAYMENT = "prepare_payment"


@dataclass
class ProcessingResult:
    """Result of agent processing"""
    success: bool
    message: str
    data: Optional[Dict] = None
    error: Optional[str] = None
    metadata: Optional[Dict] = None


@dataclass
class ProcessingLog:
    """Log entry for processing actions"""
    timestamp: datetime
    agent_type: AgentType
    action: AgentAction
    outcome: str  # success, failure, exception
    status_before: InvoiceStatus
    status_after: InvoiceStatus
    details: Optional[Dict] = None


class BaseAgent(ABC):
    """Base class for all agents implementing the core loop"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def plan(self, context: Dict) -> Dict:
        """Plan the actions to be taken based on context"""
        pass
    
    @abstractmethod
    async def act(self, plan: Dict) -> ProcessingResult:
        """Execute the planned actions"""
        pass
    
    @abstractmethod
    async def observe(self, result: ProcessingResult) -> Dict:
        """Observe and analyze the results of actions"""
        pass
    
    @abstractmethod
    async def complete(self, context: Dict) -> ProcessingResult:
        """Complete the processing and update state"""
        pass
    
    async def execute_loop(self, context: Dict) -> ProcessingResult:
        """Execute the full Plan → Act → Observe → Recover → Complete loop"""
        try:
            # Plan Phase
            plan = await self.plan(context)
            
            # Act Phase
            action_result = await self.act(plan)
            
            if not action_result.success:
                return action_result  # Return the failed result directly
            
            # Observe Phase
            observed_data = await self.observe(action_result)
            
            # Complete Phase
            completion_result = await self.complete(context)
            
            # For data transformation agents, the result of the act phase
            # is usually what we want to pass forward
            if action_result.success and action_result.data is not None:
                return action_result
            else:
                return completion_result
            
        except Exception as e:
            self.logger.error(f"Error in agent loop: {str(e)}")
            return ProcessingResult(
                success=False,
                message=f"Agent loop error: {str(e)}",
                error=str(e)
            )


class InvoiceCaptureAgent(BaseAgent):
    """Agent responsible for capturing invoices from various sources"""
    
    def __init__(self):
        super().__init__("InvoiceCaptureAgent")
    
    async def plan(self, context: Dict) -> Dict:
        """Plan the invoice capture based on source"""
        return {
            "source": context.get("source", "email"),
            "file_path": context.get("file_path"),
            "sender": context.get("sender"),
            "subject": context.get("subject")
        }
    
    async def act(self, plan: Dict) -> ProcessingResult:
        """Capture the invoice from the specified source"""
        try:
            # Simulate invoice capture
            invoice_id = f"INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            
            result_data = {
                "invoice_id": invoice_id,
                "source": plan["source"],
                "file_path": plan["file_path"],
                "received_at": datetime.now().isoformat(),
                "status": InvoiceStatus.RECEIVED.value
            }
            
            return ProcessingResult(
                success=True,
                message="Invoice captured successfully",
                data=result_data
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message="Failed to capture invoice",
                error=str(e)
            )
    
    async def observe(self, result: ProcessingResult) -> Dict:
        """Observe the captured invoice"""
        if result.success:
            return {
                "captured_invoice": result.data,
                "observation_time": datetime.now().isoformat()
            }
        return {"error": result.error}
    
    async def complete(self, context: Dict) -> ProcessingResult:
        """Complete the capture process"""
        return ProcessingResult(
            success=True,
            message="Invoice capture completed",
            data={"next_action": "extraction"}
        )


class ExtractionAgent(BaseAgent):
    """Agent responsible for extracting data from invoices"""
    
    def __init__(self):
        super().__init__("ExtractionAgent")
    
    async def plan(self, context: Dict) -> Dict:
        """Plan the data extraction"""
        return {
            "invoice_id": context.get("invoice_id"),
            "file_path": context.get("file_path"),
            "source": context.get("source", "email")
        }
    
    async def act(self, plan: Dict) -> ProcessingResult:
        """Extract structured data from the invoice"""
        try:
            # Simulate data extraction from invoice
            extracted_data = {
                "vendor_name": "Acme Corporation Ltd",
                "invoice_number": f"ACME-{plan['invoice_id'].split('-')[-1]}",
                "invoice_date": "2026-01-15",
                "amount": 1250.75,
                "currency": "USD",
                "total_amount": 1250.75,
                "vat_amount": 0.00,
                "line_items": [
                    {"description": "Software License", "quantity": 1, "amount": 1000.00},
                    {"description": "Setup Fee", "quantity": 1, "amount": 250.75}
                ],
                "po_number": "PO-2026-001",
                "delivery_note": "DN-2026-001"
            }
            
            result_data = {
                "invoice_id": plan["invoice_id"],
                "extracted_data": extracted_data,
                "confidence_score": 0.95,
                "extraction_time": datetime.now().isoformat()
            }
            
            return ProcessingResult(
                success=True,
                message="Data extracted successfully",
                data=result_data
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message="Failed to extract data",
                error=str(e)
            )
    
    async def observe(self, result: ProcessingResult) -> Dict:
        """Observe the extracted data"""
        if result.success:
            return {
                "extracted_data": result.data,
                "quality_metrics": {
                    "confidence": result.data.get("confidence_score", 0.0),
                    "field_completeness": 0.95
                }
            }
        return {"error": result.error}
    
    async def complete(self, context: Dict) -> ProcessingResult:
        """Complete the extraction process"""
        return ProcessingResult(
            success=True,
            message="Data extraction completed",
            data={"next_action": "validation"}
        )


class ValidationAgent(BaseAgent):
    """Agent responsible for validating extracted data"""
    
    def __init__(self):
        super().__init__("ValidationAgent")
    
    async def plan(self, context: Dict) -> Dict:
        """Plan the validation process"""
        return {
            "extracted_data": context.get("extracted_data"),
            "invoice_id": context.get("invoice_id")
        }
    
    async def act(self, plan: Dict) -> ProcessingResult:
        """Validate the extracted data against business rules"""
        try:
            extracted_data = plan["extracted_data"]
            
            # Perform validation checks
            validation_checks = {
                "required_fields_valid": all([
                    extracted_data.get("vendor_name"),
                    extracted_data.get("invoice_number"),
                    extracted_data.get("invoice_date"),
                    extracted_data.get("amount") is not None
                ]),
                "amount_format_valid": isinstance(extracted_data.get("amount"), (int, float)),
                "date_logic_valid": True,  # Simplified
            }
            
            # Check if any validation failed
            all_passed = all(validation_checks.values())
            
            # Check for negative conditions (these should be False for success)
            has_issues = {
                "duplicate_detected": False  # Expecting False (no duplicate)
            }
            
            # Overall success: all positive checks passed AND no negative conditions triggered
            all_valid = all_passed and all(not value for value in has_issues.values())
            
            result_data = {
                "validation_results": validation_checks,
                "is_valid": all_valid,
                "validation_time": datetime.now().isoformat()
            }
            
            return ProcessingResult(
                success=all_valid,
                message="Validation completed",
                data=result_data
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message="Validation failed",
                error=str(e)
            )
    
    async def observe(self, result: ProcessingResult) -> Dict:
        """Observe the validation results"""
        if result.success:
            return {
                "validation_outcome": "passed",
                "results": result.data.get("validation_results", {})
            }
        return {
            "validation_outcome": "failed",
            "error": result.error
        }
    
    async def complete(self, context: Dict) -> ProcessingResult:
        """Complete the validation process"""
        return ProcessingResult(
            success=True,
            message="Data validation completed",
            data={"next_action": "matching"}
        )


class MatchingAgent(BaseAgent):
    """Agent responsible for 3-way matching"""
    
    def __init__(self):
        super().__init__("MatchingAgent")
    
    async def plan(self, context: Dict) -> Dict:
        """Plan the matching process"""
        return {
            "extracted_data": context.get("extracted_data"),
            "invoice_id": context.get("invoice_id")
        }
    
    async def act(self, plan: Dict) -> ProcessingResult:
        """Perform 3-way matching (PO, Invoice, Goods Receipt)"""
        try:
            extracted_data = plan["extracted_data"]
            
            # Simulate matching process
            po_exists = extracted_data.get("po_number") is not None
            match_percentage = 100.0  # Perfect match for demo
            
            # For this demo, we'll simulate a common exception scenario
            # where there's a small mismatch that gets treated as an exception
            if po_exists:
                match_status = "MATCHED_WITH_EXCEPTION"  # Simulate minor mismatch
                exception_reason = "Minor amount variance detected"
            else:
                match_status = "NO_PO_FOUND"
                exception_reason = "Purchase order not found"
            
            result_data = {
                "match_status": match_status,
                "match_percentage": match_percentage,
                "exception_reason": exception_reason,
                "matching_time": datetime.now().isoformat()
            }
            
            # For demo purposes, return success but with exception status
            return ProcessingResult(
                success=True,  # Matching completed (even if with exception)
                message=f"Matching completed with exception: {exception_reason}",
                data=result_data
            )
        except Exception as e:
            return ProcessingResult(
                success=False,
                message="Matching failed",
                error=str(e)
            )
    
    async def observe(self, result: ProcessingResult) -> Dict:
        """Observe the matching results"""
        if result.success:
            return {
                "match_outcome": result.data.get("match_status", "unknown"),
                "exception_details": result.data.get("exception_reason", "none")
            }
        return {"error": result.error}
    
    async def complete(self, context: Dict) -> ProcessingResult:
        """Complete the matching process"""
        return ProcessingResult(
            success=True,
            message="3-way matching completed",
            data={"next_action": "approval"}
        )


class AgentOrchestrator:
    """Coordinates agent collaboration for end-to-end invoice processing"""
    
    def __init__(self):
        self.agents = {
            AgentType.INVOICE_CAPTURE: InvoiceCaptureAgent(),
            AgentType.EXTRACTION: ExtractionAgent(),
            AgentType.VALIDATION: ValidationAgent(),
            AgentType.MATCHING: MatchingAgent(),
        }
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def process_invoice(self, invoice_context: Dict) -> Dict:
        """Process an invoice through the full agent pipeline"""
        processing_log = []
        current_context = invoice_context.copy()
        current_status = InvoiceStatus.RECEIVED
        
        try:
            # Invoice Capture Phase
            self.logger.info("Starting invoice capture phase")
            capture_result = await self.agents[AgentType.INVOICE_CAPTURE].execute_loop(current_context)
            
            if not capture_result.success:
                return {
                    "status": "FAILED_AT_CAPTURE",
                    "message": f"Capture failed: {capture_result.error}",
                    "processing_log": processing_log
                }
            
            # Update context with capture result
            current_context.update(capture_result.data or {})
            new_status = InvoiceStatus.EXTRACTED
            processing_log.append(ProcessingLog(
                timestamp=datetime.now(),
                agent_type=AgentType.INVOICE_CAPTURE,
                action=AgentAction.CAPTURE_INVOICE,
                outcome="success" if capture_result.success else "failure",
                status_before=current_status,
                status_after=new_status,
                details={"invoice_id": capture_result.data.get("invoice_id")}
            ))
            current_status = new_status
            
            # Data Extraction Phase
            self.logger.info("Starting data extraction phase")
            extraction_context = current_context.copy()
            extraction_result = await self.agents[AgentType.EXTRACTION].execute_loop(extraction_context)
            
            if not extraction_result.success:
                return {
                    "status": "FAILED_AT_EXTRACTION",
                    "message": f"Extraction failed: {extraction_result.error}",
                    "processing_log": processing_log
                }
            
            # Update context with extraction result
            current_context.update(extraction_result.data or {})
            new_status = InvoiceStatus.VALIDATED  # In our flow, extraction leads to validation
            processing_log.append(ProcessingLog(
                timestamp=datetime.now(),
                agent_type=AgentType.EXTRACTION,
                action=AgentAction.EXTRACT_DATA,
                outcome="success" if extraction_result.success else "failure",
                status_before=current_status,
                status_after=new_status,
                details={"confidence": extraction_result.data.get("confidence_score")}
            ))
            current_status = new_status
            
            # Data Validation Phase
            self.logger.info("Starting data validation phase")
            validation_context = current_context.copy()
            validation_result = await self.agents[AgentType.VALIDATION].execute_loop(validation_context)
            
            if not validation_result.success:
                return {
                    "status": "FAILED_AT_VALIDATION",
                    "message": f"Validation failed: {validation_result.error}",
                    "processing_log": processing_log
                }
            
            # Update context with validation result
            current_context.update(validation_result.data or {})
            new_status = InvoiceStatus.MATCHED  # After validation comes matching
            processing_log.append(ProcessingLog(
                timestamp=datetime.now(),
                agent_type=AgentType.VALIDATION,
                action=AgentAction.VALIDATE_DATA,
                outcome="success" if validation_result.success else "failure",
                status_before=current_status,
                status_after=new_status,
                details={"valid": validation_result.data.get("is_valid", False)}
            ))
            current_status = new_status
            
            # 3-Way Matching Phase
            self.logger.info("Starting 3-way matching phase")
            matching_context = current_context.copy()
            matching_result = await self.agents[AgentType.MATCHING].execute_loop(matching_context)
            
            if not matching_result.success:
                return {
                    "status": "FAILED_AT_MATCHING",
                    "message": f"Matching failed: {matching_result.error}",
                    "processing_log": processing_log
                }
            
            # Check matching results for exceptions
            match_status = matching_result.data.get("match_status", "")
            if "EXCEPTION" in match_status or "NO_PO" in match_status:
                processing_log.append(ProcessingLog(
                    timestamp=datetime.now(),
                    agent_type=AgentType.MATCHING,
                    action=AgentAction.PERFORM_MATCHING,
                    outcome="exception",
                    status_before=current_status,
                    status_after=InvoiceStatus.APPROVED,  # Exception handled, move to approval
                    details={"match_status": match_status, "exception": matching_result.data.get("exception_reason")}
                ))
                current_status = InvoiceStatus.APPROVED
                return {
                    "status": "MATCHING_EXCEPTION",
                    "message": f"Invoice processed with matching exception: {matching_result.data.get('exception_reason')}",
                    "processing_log": processing_log
                }
            
            # Successful match
            processing_log.append(ProcessingLog(
                timestamp=datetime.now(),
                agent_type=AgentType.MATCHING,
                action=AgentAction.PERFORM_MATCHING,
                outcome="success",
                status_before=current_status,
                status_after=InvoiceStatus.APPROVED,
                details={"match_percentage": matching_result.data.get("match_percentage")}
            ))
            current_status = InvoiceStatus.APPROVED
            
            # Success case - all phases completed
            return {
                "status": "PROCESSING_COMPLETE",
                "message": "Invoice processed successfully through all phases",
                "processing_log": processing_log
            }
            
        except Exception as e:
            self.logger.error(f"Error in invoice processing: {str(e)}")
            return {
                "status": "PROCESSING_ERROR",
                "message": f"Processing failed with error: {str(e)}",
                "processing_log": processing_log
            }


# Example usage
async def main():
    """Example of how to use the agent orchestrator"""
    orchestrator = AgentOrchestrator()
    
    # Sample invoice context
    invoice_context = {
        "source": "email",
        "file_path": "/uploads/invoice_001.pdf",
        "sender": "vendor@acme-corp.com",
        "subject": "Invoice ACME-001 for software license"
    }
    
    # Process the invoice
    result = await orchestrator.process_invoice(invoice_context)
    
    print(f"Invoice processing result: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Actions performed: {len(result['processing_log'])}")


if __name__ == "__main__":
    asyncio.run(main())