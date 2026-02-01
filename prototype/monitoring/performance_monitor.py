#!/usr/bin/env python3
"""
Enhanced Agent Performance Monitor
Integrates with existing agent system for real-time performance tracking
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading
import queue
from dataclasses import dataclass, asdict

@dataclass
class AgentActivity:
    """Represents a single agent activity/event"""
    timestamp: datetime
    agent_name: str
    activity_type: str  # 'start', 'complete', 'error', 'retry'
    task_description: str
    duration: Optional[float] = None
    success: Optional[bool] = None
    error_message: Optional[str] = None
    retry_count: int = 0

@dataclass
class PerformanceSnapshot:
    """Snapshot of agent performance at a point in time"""
    timestamp: datetime
    agent_metrics: Dict[str, Dict[str, Any]]
    system_load: float
    pending_tasks: int

class PerformanceTracker:
    """Tracks and analyzes agent performance metrics"""
    
    def __init__(self):
        self.activities: List[AgentActivity] = []
        self.agent_stats: Dict[str, Dict[str, Any]] = {}
        self.max_history = 1000  # Keep last 1000 activities
        
    def record_activity(self, activity: AgentActivity):
        """Record an agent activity"""
        self.activities.append(activity)
        
        # Keep history limited
        if len(self.activities) > self.max_history:
            self.activities.pop(0)
            
        # Update agent statistics
        self._update_agent_stats(activity)
        
    def _update_agent_stats(self, activity: AgentActivity):
        """Update statistics for an agent"""
        agent_name = activity.agent_name
        
        if agent_name not in self.agent_stats:
            self.agent_stats[agent_name] = {
                'total_tasks': 0,
                'successful_tasks': 0,
                'failed_tasks': 0,
                'total_duration': 0.0,
                'avg_duration': 0.0,
                'current_status': 'idle',
                'last_activity': activity.timestamp,
                'error_count': 0,
                'retry_count': 0
            }
        
        stats = self.agent_stats[agent_name]
        
        if activity.activity_type == 'start':
            stats['current_status'] = 'processing'
            stats['last_activity'] = activity.timestamp
            
        elif activity.activity_type == 'complete':
            stats['total_tasks'] += 1
            stats['current_status'] = 'idle'
            stats['last_activity'] = activity.timestamp
            
            if activity.success:
                stats['successful_tasks'] += 1
            else:
                stats['failed_tasks'] += 1
                stats['error_count'] += 1
                
            if activity.duration:
                stats['total_duration'] += activity.duration
                stats['avg_duration'] = stats['total_duration'] / stats['total_tasks']
                
        elif activity.activity_type == 'error':
            stats['error_count'] += 1
            stats['current_status'] = 'error'
            stats['last_activity'] = activity.timestamp
            
        elif activity.activity_type == 'retry':
            stats['retry_count'] += 1
            
    def get_agent_performance(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get performance data for a specific agent"""
        return self.agent_stats.get(agent_name)
        
    def get_system_performance(self) -> Dict[str, Any]:
        """Get overall system performance metrics"""
        total_tasks = sum(stats['total_tasks'] for stats in self.agent_stats.values())
        successful_tasks = sum(stats['successful_tasks'] for stats in self.agent_stats.values())
        failed_tasks = sum(stats['failed_tasks'] for stats in self.agent_stats.values())
        
        success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Calculate average processing time
        total_duration = sum(stats['total_duration'] for stats in self.agent_stats.values())
        avg_processing_time = total_duration / total_tasks if total_tasks > 0 else 0
        
        return {
            'total_agents': len(self.agent_stats),
            'total_tasks': total_tasks,
            'successful_tasks': successful_tasks,
            'failed_tasks': failed_tasks,
            'success_rate': success_rate,
            'avg_processing_time': avg_processing_time,
            'active_agents': sum(1 for stats in self.agent_stats.values() 
                               if stats['current_status'] == 'processing')
        }
        
    def get_recent_activities(self, minutes: int = 5) -> List[AgentActivity]:
        """Get activities from the last N minutes"""
        cutoff_time = datetime.now().timestamp() - (minutes * 60)
        return [activity for activity in self.activities 
                if activity.timestamp.timestamp() >= cutoff_time]

class LiveMonitor:
    """Live monitoring interface for agent performance"""
    
    def __init__(self):
        self.tracker = PerformanceTracker()
        self.is_running = False
        self.display_thread = None
        self.refresh_interval = 1.0  # seconds
        
    def start_monitoring(self):
        """Start live monitoring display"""
        self.is_running = True
        self.display_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.display_thread.start()
        
    def stop_monitoring(self):
        """Stop live monitoring"""
        self.is_running = False
        if self.display_thread:
            self.display_thread.join(timeout=2)
            
    def record_activity(self, activity: AgentActivity):
        """Record an activity for monitoring"""
        self.tracker.record_activity(activity)
        
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            self._clear_display()
            self._show_dashboard()
            time.sleep(self.refresh_interval)
            
    def _clear_display(self):
        """Clear terminal for fresh display"""
        print("\033[2J\033[H", end="")
        
    def _show_dashboard(self):
        """Display the main dashboard"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Header
        print("=" * 100)
        print("🤖 AI ACCOUNTS PAYABLE - LIVE PERFORMANCE MONITOR")
        print(f"🕒 System Time: {timestamp}")
        print("=" * 100)
        print()
        
        # System Overview
        self._show_system_overview()
        print()
        
        # Agent Performance Table
        self._show_agent_performance()
        print()
        
        # Recent Activities
        self._show_recent_activities()
        
    def _show_system_overview(self):
        """Show system-wide performance overview"""
        perf = self.tracker.get_system_performance()
        
        print("📈 SYSTEM OVERVIEW")
        print("-" * 30)
        print(f"Agents Active:     {perf['active_agents']}/{perf['total_agents']}")
        print(f"Tasks Completed:   {perf['successful_tasks']}")
        print(f"Tasks Failed:      {perf['failed_tasks']}")
        print(f"Success Rate:      {perf['success_rate']:.1f}%")
        print(f"Avg Processing:    {perf['avg_processing_time']:.2f}s")
        print()
        
    def _show_agent_performance(self):
        """Show detailed agent performance table"""
        print("📊 AGENT PERFORMANCE DETAILS")
        print("-" * 80)
        
        if not self.tracker.agent_stats:
            print("No agent data available yet.")
            return
            
        # Table header
        print(f"{'Agent':<15} {'Status':<10} {'Tasks':<8} {'Success':<8} {'Failed':<8} {'Avg Time':<10} {'Errors':<8}")
        print("-" * 80)
        
        for agent_name, stats in self.tracker.agent_stats.items():
            status = self._format_status(stats['current_status'])
            success_rate = (stats['successful_tasks'] / stats['total_tasks'] * 100) if stats['total_tasks'] > 0 else 0
            
            print(f"{agent_name:<15} {status:<10} {stats['total_tasks']:<8} "
                  f"{stats['successful_tasks']:<8} {stats['failed_tasks']:<8} "
                  f"{stats['avg_duration']:.2f}s   {stats['error_count']:<8}")
                  
    def _format_status(self, status: str) -> str:
        """Format status with appropriate emoji/color indicators"""
        status_map = {
            'idle': '🟢 Idle',
            'processing': '🔵 Active',
            'error': '🔴 Error'
        }
        return status_map.get(status, status)
        
    def _show_recent_activities(self):
        """Show recent agent activities"""
        print("📋 RECENT ACTIVITIES (Last 5 minutes)")
        print("-" * 60)
        
        recent_activities = self.tracker.get_recent_activities(5)
        
        if not recent_activities:
            print("No recent activities.")
            return
            
        # Show most recent first (limit to 15 items)
        for activity in reversed(recent_activities[-15:]):
            time_str = activity.timestamp.strftime('%H:%M:%S')
            agent = activity.agent_name[:12]  # Truncate long names
            
            if activity.activity_type == 'start':
                print(f"[{time_str}] 🚀 {agent:<12} Started: {activity.task_description[:40]}")
            elif activity.activity_type == 'complete':
                status = "✅" if activity.success else "❌"
                duration = f"({activity.duration:.2f}s)" if activity.duration else ""
                print(f"[{time_str}] {status} {agent:<12} Completed {duration}")
            elif activity.activity_type == 'error':
                print(f"[{time_str}] ⚠️  {agent:<12} Error: {activity.error_message[:40]}")
            elif activity.activity_type == 'retry':
                print(f"[{time_str}] 🔁 {agent:<12} Retry #{activity.retry_count}")

# Global monitor instance
monitor = LiveMonitor()

class MonitoredAgentMixin:
    """Mixin class to add monitoring capabilities to agents"""
    
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.current_task = None
        
    async def monitored_execute(self, task_description: str, coro):
        """Execute a coroutine with monitoring"""
        start_time = time.time()
        
        # Record start activity
        start_activity = AgentActivity(
            timestamp=datetime.now(),
            agent_name=self.agent_name,
            activity_type='start',
            task_description=task_description
        )
        monitor.record_activity(start_activity)
        
        try:
            # Execute the task
            result = await coro
            success = True
            error_msg = None
            
        except Exception as e:
            result = None
            success = False
            error_msg = str(e)
            
            # Record error
            error_activity = AgentActivity(
                timestamp=datetime.now(),
                agent_name=self.agent_name,
                activity_type='error',
                task_description=task_description,
                error_message=error_msg
            )
            monitor.record_activity(error_activity)
            
        finally:
            # Record completion
            duration = time.time() - start_time
            complete_activity = AgentActivity(
                timestamp=datetime.now(),
                agent_name=self.agent_name,
                activity_type='complete',
                task_description=task_description,
                duration=duration,
                success=success,
                error_message=error_msg
            )
            monitor.record_activity(complete_activity)
            
        return result, success

# Demo function to show the monitoring in action
async def run_performance_demo():
    """Run a demo showing live agent performance monitoring"""
    
    print("🚀 Starting AI AP Employee Performance Monitoring Demo")
    print("This will simulate multiple agents processing invoices in real-time")
    print("Press Ctrl+C to stop monitoring\n")
    
    # Start monitoring
    monitor.start_monitoring()
    
    # Create monitored agents
    class DemoAgent(MonitoredAgentMixin):
        def __init__(self, name: str):
            super().__init__(name)
            
        async def process_task(self, task_name: str, duration: float, fail_chance: float = 0.0):
            """Process a simulated task"""
            async def task_coro():
                await asyncio.sleep(duration)
                import random
                if random.random() < fail_chance:
                    raise Exception(f"Simulated failure in {task_name}")
                return f"Successfully completed {task_name}"
            
            return await self.monitored_execute(task_name, task_coro())
    
    # Create agent instances
    agents = {
        'capture': DemoAgent('InvoiceCapture'),
        'extract': DemoAgent('DataExtraction'),
        'validate': DemoAgent('Validation'),
        'match': DemoAgent('Matching'),
        'approve': DemoAgent('Approval'),
        'pay': DemoAgent('Payment')
    }
    
    # Task definitions
    tasks = [
        ('Processing email attachment', 1.5, 0.05),
        ('Running OCR on document', 2.0, 0.1),
        ('Validating vendor data', 0.8, 0.02),
        ('Checking 3-way match', 2.5, 0.15),
        ('Routing for approval', 1.0, 0.03),
        ('Executing payment', 1.8, 0.08),
        ('Updating audit trail', 0.5, 0.01),
        ('Sending notifications', 0.7, 0.02)
    ]
    
    try:
        # Continuous task processing simulation
        while True:
            import random
            
            # Randomly select agent and task
            agent_key = random.choice(list(agents.keys()))
            agent = agents[agent_key]
            task_desc, duration, fail_chance = random.choice(tasks)
            
            # Process the task
            await agent.process_task(task_desc, duration, fail_chance)
            
            # Random delay between tasks
            await asyncio.sleep(random.uniform(0.3, 1.5))
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping performance monitoring...")
        monitor.stop_monitoring()
        print("✅ Monitoring stopped. Thanks for watching!")

if __name__ == "__main__":
    asyncio.run(run_performance_demo())