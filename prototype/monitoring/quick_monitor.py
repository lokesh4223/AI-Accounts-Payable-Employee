#!/usr/bin/env python3
"""
Direct Live Monitoring Demo
Run this to see real-time agent performance monitoring
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(__file__))

from performance_monitor import monitor, MonitoredAgentMixin

class SimpleAgent(MonitoredAgentMixin):
    """Simple agent for demonstration"""
    
    def __init__(self, name: str):
        super().__init__(name)
        
    async def work(self, task_name: str, duration: float):
        """Perform work with monitoring"""
        async def task():
            await asyncio.sleep(duration)
            import random
            if random.random() < 0.15:  # 15% error rate for demo
                raise Exception("Simulated processing error")
            return f"Finished {task_name}"
            
        return await self.monitored_execute(task_name, task())

async def demo():
    """Run the demonstration"""
    print("🤖 LIVE AGENT PERFORMANCE MONITOR")
    print("=" * 40)
    print("Starting real-time monitoring...")
    print("Press Ctrl+C to stop\n")
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Create agents
    agents = [
        SimpleAgent("InvoiceCapture"),
        SimpleAgent("DataExtraction"), 
        SimpleAgent("Validation"),
        SimpleAgent("Matching"),
        SimpleAgent("Approval")
    ]
    
    tasks = [
        "Processing invoice document",
        "Extracting data fields",
        "Validating information",
        "Checking 3-way match",
        "Routing for approval",
        "Updating records"
    ]
    
    try:
        task_counter = 0
        while True:
            import random
            
            # Pick random agent and task
            agent = random.choice(agents)
            task = random.choice(tasks)
            duration = random.uniform(0.5, 3.0)
            
            task_counter += 1
            print(f"[{task_counter}] {agent.agent_name} → {task}")
            
            # Process the task
            result, success = await agent.work(task, duration)
            
            if not success:
                print(f"   ❌ Failed: {result}")
            
            # Brief pause
            await asyncio.sleep(random.uniform(0.2, 1.0))
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping monitor...")
        monitor.stop_monitoring()
        print("✅ Monitoring completed!")

if __name__ == "__main__":
    asyncio.run(demo())