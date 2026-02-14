#!/usr/bin/env python3
"""
Agentic AI Network Troubleshooting Assistant
Multi-agent system for automated network issue diagnosis
"""

import os
import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime
import argparse

# Using OpenAI directly (in production, would use LangChain)
# This demonstrates the concept with simpler code for learning

class NetworkAgent:
    """Base agent class for network troubleshooting"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.api_key = os.getenv('OPENAI_API_KEY', 'demo-mode')
        
    def execute(self, context: Dict) -> Dict:
        """Execute agent's task based on context"""
        raise NotImplementedError


class AnalyzerAgent(NetworkAgent):
    """Analyzes network data and identifies issues"""
    
    def __init__(self):
        super().__init__("Analyzer", "Network Data Analysis")
    
    def execute(self, context: Dict) -> Dict:
        """Analyze network metrics and logs"""
        issue = context.get('issue', '')
        target = context.get('target', '8.8.8.8')
        
        # Run basic network diagnostics
        ping_result = self._run_ping(target)
        
        analysis = {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'findings': {
                'ping_loss': ping_result.get('loss', 0),
                'avg_latency': ping_result.get('avg_time', 0),
                'status': 'degraded' if ping_result.get('loss', 0) > 5 else 'normal'
            },
            'recommendation': 'Proceed with detailed route analysis'
        }
        
        return analysis
    
    def _run_ping(self, target: str, count: int = 4) -> Dict:
        """Run ping command and parse results"""
        try:
            result = subprocess.run(
                ['ping', '-c', str(count), target],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Simple parsing of ping output
            output = result.stdout
            loss = 0
            avg_time = 0
            
            for line in output.split('\n'):
                if 'packet loss' in line:
                    loss = float(line.split('%')[0].split()[-1])
                if 'avg' in line or 'rtt' in line:
                    parts = line.split('=')
                    if len(parts) > 1:
                        times = parts[1].split('/')
                        if len(times) > 1:
                            avg_time = float(times[1])
            
            return {'loss': loss, 'avg_time': avg_time, 'reachable': result.returncode == 0}
            
        except Exception as e:
            return {'loss': 100, 'avg_time': 0, 'reachable': False, 'error': str(e)}


class PlannerAgent(NetworkAgent):
    """Creates troubleshooting strategy"""
    
    def __init__(self):
        super().__init__("Planner", "Strategy Development")
    
    def execute(self, context: Dict) -> Dict:
        """Develop troubleshooting plan based on analysis"""
        analyzer_findings = context.get('analyzer_findings', {})
        
        # Intelligent planning based on findings
        findings = analyzer_findings.get('findings', {})
        loss = findings.get('ping_loss', 0)
        latency = findings.get('avg_latency', 0)
        
        plan = {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'strategy': self._create_strategy(loss, latency),
            'steps': self._generate_steps(loss, latency),
            'priority': 'high' if loss > 20 or latency > 200 else 'medium'
        }
        
        return plan
    
    def _create_strategy(self, loss: float, latency: float) -> str:
        """Create strategy based on metrics"""
        if loss > 20:
            return "Focus on packet loss - check route, interfaces, and network congestion"
        elif latency > 200:
            return "Address high latency - analyze routing hops and bandwidth"
        elif loss > 5:
            return "Investigate intermittent packet loss - monitor for patterns"
        else:
            return "Perform general health check and optimization"
    
    def _generate_steps(self, loss: float, latency: float) -> List[str]:
        """Generate troubleshooting steps"""
        steps = []
        
        if loss > 5:
            steps.extend([
                "Run traceroute to identify problem hop",
                "Check interface statistics for errors",
                "Analyze recent network changes"
            ])
        
        if latency > 100:
            steps.extend([
                "Measure bandwidth utilization",
                "Check for routing loops",
                "Verify QoS policies"
            ])
        
        if not steps:
            steps = ["Baseline measurements", "Continuous monitoring"]
        
        return steps


class ExecutorAgent(NetworkAgent):
    """Executes diagnostic commands"""
    
    def __init__(self):
        super().__init__("Executor", "Command Execution")
    
    def execute(self, context: Dict) -> Dict:
        """Execute planned diagnostic steps"""
        plan = context.get('plan', {})
        target = context.get('target', '8.8.8.8')
        
        execution_results = {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'commands_run': [],
            'results': {}
        }
        
        # Execute traceroute
        traceroute_result = self._run_traceroute(target)
        execution_results['commands_run'].append('traceroute')
        execution_results['results']['traceroute'] = traceroute_result
        
        return execution_results
    
    def _run_traceroute(self, target: str) -> Dict:
        """Run traceroute command"""
        try:
            # Use traceroute or tracert depending on OS
            cmd = ['traceroute', '-m', '15', target]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            hops = len([line for line in result.stdout.split('\n') if line.strip()])
            
            return {
                'success': result.returncode == 0,
                'hops': hops,
                'output_lines': result.stdout.split('\n')[:10]  # First 10 hops
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}


class ValidatorAgent(NetworkAgent):
    """Validates solutions and findings"""
    
    def __init__(self):
        super().__init__("Validator", "Solution Validation")
    
    def execute(self, context: Dict) -> Dict:
        """Validate execution results"""
        execution = context.get('execution', {})
        
        validation = {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'validated': True,
            'confidence': 0.85,
            'issues_found': []
        }
        
        # Validate traceroute results
        traceroute = execution.get('results', {}).get('traceroute', {})
        if not traceroute.get('success'):
            validation['issues_found'].append("Traceroute execution failed")
            validation['confidence'] = 0.5
        
        return validation


class ReporterAgent(NetworkAgent):
    """Generates troubleshooting reports"""
    
    def __init__(self):
        super().__init__("Reporter", "Report Generation")
    
    def execute(self, context: Dict) -> Dict:
        """Generate comprehensive report"""
        report = {
            'agent': self.name,
            'timestamp': datetime.now().isoformat(),
            'summary': self._generate_summary(context),
            'details': self._compile_details(context),
            'recommendations': self._generate_recommendations(context)
        }
        
        return report
    
    def _generate_summary(self, context: Dict) -> str:
        """Generate executive summary"""
        analyzer = context.get('analyzer_findings', {}).get('findings', {})
        status = analyzer.get('status', 'unknown')
        
        return f"Network status: {status}. Automated diagnosis completed with multi-agent analysis."
    
    def _compile_details(self, context: Dict) -> Dict:
        """Compile all findings"""
        return {
            'analysis': context.get('analyzer_findings', {}),
            'planning': context.get('plan', {}),
            'execution': context.get('execution', {}),
            'validation': context.get('validation', {})
        }
    
    def _generate_recommendations(self, context: Dict) -> List[str]:
        """Generate actionable recommendations"""
        findings = context.get('analyzer_findings', {}).get('findings', {})
        loss = findings.get('ping_loss', 0)
        
        recommendations = []
        
        if loss > 20:
            recommendations.append("Critical: Investigate packet loss - possible link failure")
        elif loss > 5:
            recommendations.append("Warning: Monitor intermittent packet loss")
        else:
            recommendations.append("Network operating normally - continue monitoring")
        
        recommendations.append("Schedule regular automated diagnostics")
        
        return recommendations


class AgentOrchestrator:
    """Orchestrates multi-agent workflow"""
    
    def __init__(self):
        self.agents = {
            'analyzer': AnalyzerAgent(),
            'planner': PlannerAgent(),
            'executor': ExecutorAgent(),
            'validator': ValidatorAgent(),
            'reporter': ReporterAgent()
        }
        
    def run_troubleshooting(self, issue: str, target: str = '8.8.8.8') -> Dict:
        """Execute complete troubleshooting workflow"""
        context = {
            'issue': issue,
            'target': target,
            'start_time': datetime.now().isoformat()
        }
        
        print(f"\n🤖 Starting AI-powered network troubleshooting...")
        print(f"📋 Issue: {issue}")
        print(f"🎯 Target: {target}\n")
        
        # Step 1: Analyze
        print("1️⃣ Analyzer Agent: Examining network data...")
        context['analyzer_findings'] = self.agents['analyzer'].execute(context)
        print(f"   ✓ Status: {context['analyzer_findings']['findings']['status']}")
        
        # Step 2: Plan
        print("\n2️⃣ Planner Agent: Developing strategy...")
        context['plan'] = self.agents['planner'].execute(context)
        print(f"   ✓ Strategy: {context['plan']['strategy'][:60]}...")
        
        # Step 3: Execute
        print("\n3️⃣ Executor Agent: Running diagnostics...")
        context['execution'] = self.agents['executor'].execute(context)
        print(f"   ✓ Commands executed: {len(context['execution']['commands_run'])}")
        
        # Step 4: Validate
        print("\n4️⃣ Validator Agent: Verifying results...")
        context['validation'] = self.agents['validator'].execute(context)
        print(f"   ✓ Confidence: {context['validation']['confidence']*100:.0f}%")
        
        # Step 5: Report
        print("\n5️⃣ Reporter Agent: Generating report...")
        context['report'] = self.agents['reporter'].execute(context)
        print(f"   ✓ Report generated\n")
        
        return context


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='AI Network Troubleshooting Agent')
    parser.add_argument('--issue', type=str, default='general health check',
                       help='Network issue to troubleshoot')
    parser.add_argument('--target', type=str, default='8.8.8.8',
                       help='Target IP or hostname')
    
    args = parser.parse_args()
    
    # Run orchestrator
    orchestrator = AgentOrchestrator()
    result = orchestrator.run_troubleshooting(args.issue, args.target)
    
    # Print final report
    print("=" * 60)
    print("📊 FINAL REPORT")
    print("=" * 60)
    print(f"\nSummary: {result['report']['summary']}")
    print(f"\nRecommendations:")
    for i, rec in enumerate(result['report']['recommendations'], 1):
        print(f"  {i}. {rec}")
    print("\n" + "=" * 60)
    
    # Save detailed results
    output_file = f"network_diagnosis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2, default=str)
    
    print(f"\n💾 Detailed results saved to: {output_file}")


if __name__ == "__main__":
    main()
