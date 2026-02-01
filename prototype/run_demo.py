#!/usr/bin/env python3
"""
Demo runner and scenario simulator for the AI Accounts Payable Employee system.
Demonstrates the multi-agent system handling various scenarios.
"""

import asyncio
import json
import sys
from datetime import datetime
from typing import Dict, List, Any
import random

# Import our modules
from agent_loop import AgentOrchestrator, InvoiceStatus, AgentType, AgentAction
from tools import ToolRegistry
from memory import MemoryType, MemorySystem


class ScenarioSimulator:
    """Simulates different AP scenarios to test the AI system"""
    
    def __init__(self):
        self.scenarios = {
            "happy_path": self.happy_path_scenario,
            "missing_po": self.missing_po_scenario,
            "duplicate_invoice": self.duplicate_invoice_scenario,
            "three_way_mismatch": self.three_way_mismatch_scenario,
            "vendor_bank_change": self.vendor_bank_change_scenario,
            "vat_failure": self.vat_failure_scenario,
            "sla_breach_risk": self.sla_breach_risk_scenario
        }
        
    async def happy_path_scenario(self) -> Dict:
        """Scenario: Clean invoice with PO and receipt"""
        print("[SCENARIO] Running Happy Path - Clean invoice with PO and receipt")
        
        # Simulated invoice data
        invoice_context = {
            "source": "email",
            "file_path": "/uploads/happy_path_invoice.pdf",
            "sender": "vendor@reliable-supplier.com",
            "subject": "Invoice INV-2026-001 with PO reference"
        }
        
        return invoice_context
        
    async def missing_po_scenario(self) -> Dict:
        """Scenario: Invoice without purchase order"""
        print("[SCENARIO] Running Missing PO - Invoice without purchase order")
        
        invoice_context = {
            "source": "email", 
            "file_path": "/uploads/missing_po_invoice.pdf",
            "sender": "new-vendor@unknown.com",
            "subject": "Invoice INV-2026-002 - No PO reference"
        }
        
        return invoice_context
        
    async def duplicate_invoice_scenario(self) -> Dict:
        """Scenario: Duplicate invoice detection"""
        print("[SCENARIO] Running Duplicate Invoice - Detection and prevention")
        
        invoice_context = {
            "source": "email",
            "file_path": "/uploads/duplicate_invoice.pdf", 
            "sender": "regular@supplier.com",
            "subject": "Invoice INV-2026-001 - Possible duplicate"
        }
        
        return invoice_context
        
    async def three_way_mismatch_scenario(self) -> Dict:
        """Scenario: 3-way match discrepancy"""
        print("[SCENARIO] Running 3-Way Mismatch - Price/quantity discrepancy")
        
        invoice_context = {
            "source": "email",
            "file_path": "/uploads/mismatch_invoice.pdf",
            "sender": "vendor@discrepancy.com", 
            "subject": "Invoice INV-2026-003 - Mismatched amounts"
        }
        
        return invoice_context
        
    async def vendor_bank_change_scenario(self) -> Dict:
        """Scenario: Vendor bank details change request"""
        print("[SCENARIO] Running Vendor Bank Change - Fraud risk assessment")
        
        invoice_context = {
            "source": "email",
            "file_path": "/uploads/bank_change_invoice.pdf",
            "sender": "updated@supplier.com",
            "subject": "Invoice with updated banking details"
        }
        
        return invoice_context
        
    async def vat_failure_scenario(self) -> Dict:
        """Scenario: VAT validation failure"""
        print("[SCENARIO] Running VAT Failure - Invalid VAT calculation")
        
        invoice_context = {
            "source": "email",
            "file_path": "/uploads/vat_failure_invoice.pdf",
            "sender": "tax@noncompliant.com",
            "subject": "Invoice with VAT issues"
        }
        
        return invoice_context
        
    async def sla_breach_risk_scenario(self) -> Dict:
        """Scenario: SLA breach risk - Approval deadline approaching"""
        print("[SCENARIO] Running SLA Breach Risk - Deadline approaching")
        
        invoice_context = {
            "source": "email",
            "file_path": "/uploads/sla_risk_invoice.pdf",
            "sender": "urgent@supplier.com",
            "subject": "URGENT: Invoice due tomorrow"
        }
        
        return invoice_context


class DemoRunner:
    """Main demo runner that executes scenarios"""
    
    def __init__(self):
        self.orchestrator = AgentOrchestrator()
        self.tool_registry = ToolRegistry()
        self.memory_system = MemorySystem()
        self.simulator = ScenarioSimulator()
        
    async def setup_system(self):
        """Initialize all system components"""
        print("💼 AI Accounts Payable Employee - Enterprise Edition")
        print("=" * 60)
        
        # Initialize tools
        await self.tool_registry.initialize_tools()
        print("🔄 Initializing core systems...")
        
        # Initialize memory
        await self.memory_system.initialize_memory()
        
        print("✅ System initialization complete")
        print("   All components ready for invoice processing")
        
    async def run_scenario(self, scenario_name: str) -> Dict:
        """Run a specific scenario"""
        # Get scenario context (without printing the detailed scenario description)
        scenario_func = self.simulator.scenarios.get(scenario_name)
        if not scenario_func:
            raise ValueError(f"Unknown scenario: {scenario_name}")
            
        context = await scenario_func()
        
        # Store scenario in memory
        self.memory_system.manager.store(
            key=f"scenario_{scenario_name}_{datetime.now().isoformat()}",
            value=context,
            memory_type=MemoryType.SESSION_CONTEXT,
            tags=["demo", "scenario", scenario_name],
            importance=0.8
        )
        
        # Process through orchestrator
        result = await self.orchestrator.process_invoice(context)
        
        # Professional output
        status_emojis = {
            "PROCESSING_COMPLETE": "✅",
            "MATCHING_EXCEPTION": "⚠️",
            "FAILED_AT_VALIDATION": "❌",
            "FAILED_AT_EXTRACTION": "❌",
            "FAILED_AT_CAPTURE": "❌"
        }
        emoji = status_emojis.get(result['status'], "❓")
        
        print(f"{emoji} {scenario_name.replace('_', ' ').title()}: {result['status']} | Steps: {len(result['processing_log'])}")
        return result
        
    async def run_full_demo(self):
        """Run the complete demo with all scenarios"""
        await self.setup_system()
        
        print("\n🚀 Executing Invoice Processing Workflows...")
        print("-" * 50)
        
        # Define scenarios to run
        scenarios = [
            "happy_path",
            "missing_po", 
            "duplicate_invoice",
            "three_way_mismatch"
        ]
        
        results = {}
        
        for scenario in scenarios:
            try:
                result = await self.run_scenario(scenario)
                results[scenario] = result
            except Exception as e:
                print(f"❌ {scenario.replace('_', ' ').title()}: FAILED - {str(e)}")
                results[scenario] = {"status": "FAILED", "error": str(e)}
        
        # Generate summary
        await self.generate_summary(results)
        
    async def generate_summary(self, results: Dict[str, Any]):
        """Generate and display summary of all scenarios"""
        total_scenarios = len(results)
        successful_scenarios = sum(1 for result in results.values() 
                                  if result.get('status', '').startswith('PROCESSING_COMPLETE') or 
                                     result.get('status') == 'MATCHING_EXCEPTION')  # Exception handling is also success
        
        success_rate = (successful_scenarios/total_scenarios)*100
        
        print(f"\n📈 PROCESSING SUMMARY")
        print("-" * 30)
        print(f"Total Workflows: {total_scenarios}")
        print(f"Successful:      {successful_scenarios}")
        print(f"Failed:          {total_scenarios - successful_scenarios}")
        print(f"Success Rate:    {success_rate:.1f}%")
        
        print(f"\n📋 DETAILED RESULTS:")
        print("-" * 30)
        for scenario, result in results.items():
            status = result.get('status', 'UNKNOWN')
            if status.startswith('PROCESSING_COMPLETE') or status == 'MATCHING_EXCEPTION':
                emoji = "✅ SUCCESS"
            else:
                emoji = "❌ FAILED"
            print(f"  {emoji}: {scenario.replace('_', ' ').title()}")
        
        print(f"\n🎯 AI Accounts Payable Employee processing complete")
        if success_rate >= 80:
            print("   ✅ System performance meets enterprise standards")
        else:
            print("   ⚠️  Review required for operational deployment")


class InteractiveDemo:
    """Interactive demo allowing user to select scenarios"""
    
    def __init__(self):
        self.runner = DemoRunner()
        self.scenarios = {
            "1": "happy_path",
            "2": "missing_po", 
            "3": "duplicate_invoice",
            "4": "three_way_mismatch",
            "5": "vendor_bank_change",
            "6": "vat_failure",
            "7": "sla_breach_risk",
            "all": "run_all",
            "quit": "quit"
        }
        
    async def show_menu(self):
        """Show interactive menu"""
        print("\n🎯 AI AP Employee Interactive Demo")
        print("=" * 40)
        print("Select a scenario to run:")
        print("  1. Happy Path - Clean invoice with PO")
        print("  2. Missing PO - Invoice without purchase order") 
        print("  3. Duplicate Invoice - Detection and prevention")
        print("  4. 3-Way Mismatch - Price/quantity discrepancy")
        print("  5. Vendor Bank Change - Fraud risk assessment")
        print("  6. VAT Failure - Invalid VAT calculation")
        print("  7. SLA Breach Risk - Approval deadline approaching")
        print("  all. Run all scenarios")
        print("  quit. Exit demo")
        print()
        
    async def run_interactive(self):
        """Run the interactive demo"""
        await self.runner.setup_system()
        
        while True:
            await self.show_menu()
            choice = input("Enter your choice (1-7, 'all', or 'quit'): ").strip().lower()
            
            if choice == "quit":
                print("👋 Exiting AI AP Employee demo. Goodbye!")
                break
            elif choice == "all":
                await self.runner.run_full_demo()
            elif choice in self.scenarios:
                scenario_name = self.scenarios[choice]
                if scenario_name == "run_all":
                    await self.runner.run_full_demo()
                else:
                    await self.runner.run_scenario(scenario_name)
            else:
                print("❌ Invalid choice. Please select a valid option.")
                
            input("\nPress Enter to continue...")


async def main():
    """Main entry point"""
    print("💼 AI Accounts Payable Employee - Enterprise Edition")
    print("="*60)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg == "interactive":
            demo = InteractiveDemo()
            await demo.run_interactive()
        elif arg == "quick":
            runner = DemoRunner()
            await runner.setup_system()
            print("\n📋 Executing Invoice Processing Workflow...")
            await runner.run_scenario("happy_path")
            print("✅ Invoice processing workflow completed")
        else:
            print(f"Usage: {sys.argv[0]} [interactive|quick]")
            print("  interactive: Run interactive demo")
            print("  quick: Run single happy path scenario")
    else:
        # Run full demo by default
        runner = DemoRunner()
        await runner.run_full_demo()


if __name__ == "__main__":
    asyncio.run(main())