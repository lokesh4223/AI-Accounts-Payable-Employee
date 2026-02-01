#!/usr/bin/env python3
"""
Live Agent Performance Demo
Demonstrates real-time monitoring of agent activities
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from performance_monitor import monitor, MonitoredAgentMixin
from agent_dashboard import dashboard

class LiveInvoiceProcessor(MonitoredAgentMixin):
    """Invoice processor with live monitoring"""
    
    def __init__(self, agent_type: str):
        super().__init__(f"{agent_type}Agent")
        dashboard.register_agent(self.agent_name)
        
    async def process_invoice_step(self, step_name: str, duration: float = 1.0):
        """Process a step in the invoice workflow"""
        
        async def step_task():
            # Simulate actual work
            await asyncio.sleep(duration)
            # Simulate occasional errors (10% chance)
            import random
            if random.random() < 0.1:
                raise Exception(f"Processing error in {step_name}")
            return f"Completed {step_name}"
            
        # Use both monitoring systems
        result, success = await self.monitored_execute(step_name, step_task())
        
        # Also log to dashboard
        start_time = asyncio.get_event_loop().time()
        dashboard.log_agent_start(self.agent_name, step_name)
        await asyncio.sleep(duration)
        dashboard.log_agent_complete(self.agent_name, success, duration)
        
        return result, success

async def run_live_demo():
    """Run the live demonstration"""
    
    print("🤖 AI AP EMPLOYEE - LIVE AGENT PERFORMANCE DEMO")
    print("=" * 50)
    print("Starting real-time monitoring of agent activities...")
    print("This simulates a complete invoice processing workflow")
    print("\nPress Ctrl+C to stop\n")
    
    # Start both monitoring systems
    monitor.start_monitoring()
    dashboard.start_monitoring()
    
    # Create agents
    agents = {
        'capture': LiveInvoiceProcessor('InvoiceCapture'),
        'extract': LiveInvoiceProcessor('DataExtraction'),
        'validate': LiveInvoiceProcessor('Validation'),
        'match': LiveInvoiceProcessor('Matching'),
        'approve': LiveInvoiceProcessor('Approval'),
        'pay': LiveInvoiceProcessor('Payment')
    }
    
    # Invoice processing workflow steps
    workflow = [
        ('capture', 'Receiving invoice from email', 1.2),
        ('extract', 'Extracting data with OCR', 2.0),
        ('validate', 'Validating vendor information', 0.8),
        ('validate', 'Checking for duplicates', 0.5),
        ('match', 'Performing 3-way matching', 2.5),
        ('approve', 'Routing for approval', 1.0),
        ('approve', 'Checking approval status', 1.5),
        ('pay', 'Generating payment instruction', 1.8),
        ('pay', 'Executing bank transfer', 2.2)
    ]
    
    invoice_count = 0
    
    try:
        while True:
            invoice_count += 1
            print(f"\n📄 Processing Invoice #{invoice_count}")
            print("-" * 30)
            
            # Process each step in the workflow
            for agent_key, step_name, duration in workflow:
                agent = agents[agent_key]
                
                print(f"⏳ {agent.agent_name}: {step_name}")
                result, success = await agent.process_invoice_step(step_name, duration)
                
                if success:
                    print(f"✅ {result}")
                else:
                    print(f"❌ Failed: {result}")
                    
                # Small delay between steps
                await asyncio.sleep(0.3)
                
            print(f"🎉 Invoice #{invoice_count} processing complete!")
            
            # Random delay before next invoice
            import random
            await asyncio.sleep(random.uniform(2, 4))
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping live demonstration...")
        monitor.stop_monitoring()
        dashboard.stop_monitoring()
        print("✅ Demonstration stopped. Final statistics:")
        
        # Show final performance summary
        perf = monitor.tracker.get_system_performance()
        print(f"\n📊 FINAL PERFORMANCE SUMMARY:")
        print(f"   Total Invoices Processed: {invoice_count}")
        print(f"   System Success Rate: {perf['success_rate']:.1f}%")
        print(f"   Average Processing Time: {perf['avg_processing_time']:.2f}s")
        print(f"   Active Agents: {perf['active_agents']}/{perf['total_agents']}")

def show_monitoring_options():
    """Show available monitoring demonstrations"""
    print("🤖 AI AP EMPLOYEE - MONITORING OPTIONS")
    print("=" * 40)
    print("1. Live Performance Dashboard (Detailed)")
    print("2. Simple Agent Status View")
    print("3. Performance Statistics Only")
    print("4. Exit")
    print()
    
    while True:
        choice = input("Select monitoring mode (1-4): ").strip()
        
        if choice == '1':
            asyncio.run(run_live_demo())
            break
        elif choice == '2':
            print("Simple status view - coming soon!")
            break
        elif choice == '3':
            print("Performance statistics - coming soon!")
            break
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1-4.")

if __name__ == "__main__":
    show_monitoring_options()