#!/usr/bin/env python3
"""
Real-time Agent Performance Dashboard
Shows live agent activities and performance metrics
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import threading
import queue

class AgentMetrics:
    """Tracks performance metrics for each agent"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.tasks_completed = 0
        self.tasks_failed = 0
        self.current_status = "idle"
        self.last_activity = None
        self.processing_time = []
        self.active_task = None
        
    def start_task(self, task_description: str):
        """Record task start"""
        self.current_status = "processing"
        self.active_task = task_description
        self.last_activity = datetime.now()
        
    def complete_task(self, success: bool, duration: float):
        """Record task completion"""
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
        self.processing_time.append(duration)
        self.current_status = "idle"
        self.active_task = None
        self.last_activity = datetime.now()
        
    def get_success_rate(self) -> float:
        """Calculate success rate percentage"""
        total = self.tasks_completed + self.tasks_failed
        if total == 0:
            return 0.0
        return (self.tasks_completed / total) * 100
        
    def get_avg_processing_time(self) -> float:
        """Get average processing time"""
        if not self.processing_time:
            return 0.0
        return sum(self.processing_time) / len(self.processing_time)

class AgentDashboard:
    """Live dashboard for monitoring agent performance"""
    
    def __init__(self):
        self.agents: Dict[str, AgentMetrics] = {}
        self.event_queue = queue.Queue()
        self.running = False
        self.display_thread = None
        
    def register_agent(self, agent_name: str):
        """Register a new agent for monitoring"""
        if agent_name not in self.agents:
            self.agents[agent_name] = AgentMetrics(agent_name)
            
    def log_agent_start(self, agent_name: str, task_description: str):
        """Log when an agent starts a task"""
        if agent_name in self.agents:
            self.agents[agent_name].start_task(task_description)
            self.event_queue.put({
                'timestamp': datetime.now(),
                'agent': agent_name,
                'event': 'start',
                'task': task_description
            })
            
    def log_agent_complete(self, agent_name: str, success: bool, duration: float):
        """Log when an agent completes a task"""
        if agent_name in self.agents:
            self.agents[agent_name].complete_task(success, duration)
            self.event_queue.put({
                'timestamp': datetime.now(),
                'agent': agent_name,
                'event': 'complete',
                'success': success,
                'duration': duration
            })
            
    def start_monitoring(self):
        """Start the live dashboard display"""
        self.running = True
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
        
    def stop_monitoring(self):
        """Stop the live dashboard"""
        self.running = False
        if self.display_thread:
            self.display_thread.join(timeout=2)
            
    def _display_loop(self):
        """Main display loop running in separate thread"""
        while self.running:
            self._clear_screen()
            self._display_header()
            self._display_agents()
            self._display_recent_events()
            time.sleep(1)  # Update every second
            
    def _clear_screen(self):
        """Clear terminal screen"""
        print("\033[2J\033[H", end="")
        
    def _display_header(self):
        """Display dashboard header"""
        print("=" * 80)
        print("🤖 AI ACCOUNTS PAYABLE - AGENT PERFORMANCE DASHBOARD")
        print(f"🕒 Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        print()
        
    def _display_agents(self):
        """Display current agent status"""
        print("📊 AGENT STATUS OVERVIEW")
        print("-" * 50)
        
        if not self.agents:
            print("No agents registered yet.")
            return
            
        # Header
        print(f"{'Agent Name':<20} {'Status':<12} {'Tasks':<8} {'Success':<8} {'Avg Time':<10} {'Active Task'}")
        print("-" * 80)
        
        for agent_name, metrics in self.agents.items():
            status_icon = self._get_status_icon(metrics.current_status)
            success_rate = f"{metrics.get_success_rate():.1f}%"
            avg_time = f"{metrics.get_avg_processing_time():.2f}s"
            
            active_task = metrics.active_task or "None"
            if len(active_task) > 25:
                active_task = active_task[:22] + "..."
                
            print(f"{agent_name:<20} {status_icon:<12} {metrics.tasks_completed:<8} {success_rate:<8} {avg_time:<10} {active_task}")
            
        print()
        
    def _get_status_icon(self, status: str) -> str:
        """Get status icon for display"""
        icons = {
            "idle": "🟢 Idle",
            "processing": "🔵 Active",
            "error": "🔴 Error"
        }
        return icons.get(status, status)
        
    def _display_recent_events(self):
        """Display recent agent events"""
        print("📈 RECENT ACTIVITIES")
        print("-" * 50)
        
        recent_events = []
        while not self.event_queue.empty() and len(recent_events) < 10:
            try:
                event = self.event_queue.get_nowait()
                recent_events.append(event)
            except queue.Empty:
                break
                
        if not recent_events:
            print("No recent activities.")
            return
            
        # Display most recent first
        for event in reversed(recent_events[-10:]):
            timestamp = event['timestamp'].strftime('%H:%M:%S')
            agent = event['agent']
            
            if event['event'] == 'start':
                print(f"[{timestamp}] 🚀 {agent} started: {event['task']}")
            elif event['event'] == 'complete':
                status = "✅ SUCCESS" if event['success'] else "❌ FAILED"
                duration = f"{event['duration']:.2f}s"
                print(f"[{timestamp}] {status} {agent} completed ({duration})")

# Global dashboard instance
dashboard = AgentDashboard()

class MonitoredAgent:
    """Base class for agents with built-in monitoring"""
    
    def __init__(self, name: str):
        self.name = name
        dashboard.register_agent(name)
        
    async def execute_with_monitoring(self, task_description: str, task_func, *args, **kwargs):
        """Execute a task with performance monitoring"""
        start_time = time.time()
        
        # Log task start
        dashboard.log_agent_start(self.name, task_description)
        
        try:
            # Execute the actual task
            result = await task_func(*args, **kwargs)
            success = True
        except Exception as e:
            print(f"❌ {self.name} encountered error: {e}")
            result = None
            success = False
        finally:
            # Log task completion
            duration = time.time() - start_time
            dashboard.log_agent_complete(self.name, success, duration)
            
        return result, success

# Example usage and demo
async def demo_agent_activities():
    """Demonstrate live agent monitoring"""
    
    # Create sample agents
    capture_agent = MonitoredAgent("InvoiceCapture")
    extraction_agent = MonitoredAgent("DataExtraction")
    validation_agent = MonitoredAgent("Validation")
    matching_agent = MonitoredAgent("Matching")
    approval_agent = MonitoredAgent("Approval")
    
    print("🚀 Starting live agent performance dashboard...")
    print("Press Ctrl+C to stop monitoring")
    print()
    
    # Start the dashboard
    dashboard.start_monitoring()
    
    try:
        # Simulate various agent activities
        tasks = [
            ("Processing PDF invoice from email", 2.5),
            ("Extracting data fields using OCR", 1.8),
            ("Validating vendor information", 0.9),
            ("Performing 3-way matching", 3.2),
            ("Routing for approval", 1.1),
            ("Checking approval status", 0.7),
            ("Generating payment instruction", 1.4),
        ]
        
        agents = [capture_agent, extraction_agent, validation_agent, matching_agent, approval_agent]
        
        # Run continuous simulation
        task_index = 0
        while True:
            # Randomly select an agent and task
            import random
            agent = random.choice(agents)
            task_desc, duration = random.choice(tasks)
            
            # Simulate task execution
            async def simulate_task():
                await asyncio.sleep(duration)
                # Simulate occasional failures
                if random.random() < 0.1:  # 10% failure rate
                    raise Exception("Simulated processing error")
                return f"Completed: {task_desc}"
            
            await agent.execute_with_monitoring(task_desc, simulate_task)
            task_index += 1
            
            # Add some delay between tasks
            await asyncio.sleep(random.uniform(0.5, 2.0))
            
    except KeyboardInterrupt:
        print("\n🛑 Stopping dashboard...")
        dashboard.stop_monitoring()
        print("✅ Dashboard stopped.")

if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo_agent_activities())