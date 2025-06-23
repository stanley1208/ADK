#!/usr/bin/env python3
"""
🎯 GOOGLE ADK DISASTER RESPONSE SYSTEM - DEMO SCRIPT
=====================================================

This script demonstrates the complete disaster response system:
1. Live Cloud Run deployment 
2. Real Google ADK agents
3. Multi-agent coordination pipeline
4. Emergency response workflow

Perfect for hackathon presentations!
"""

import requests
import json
import asyncio
import os
from datetime import datetime

# Your deployed system URL
DEPLOYED_URL = "https://disaster-response-system-838920435800.us-central1.run.app"

def demo_deployed_system():
    """Demo the live deployed system on Google Cloud Run."""
    
    print("🚀 DEMO: Live Google Cloud Run Deployment")
    print("=" * 60)
    
    # Test main endpoint
    try:
        print("\n🔍 Testing main API endpoint...")
        response = requests.get(f"{DEPLOYED_URL}/")
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"📱 System: {data['message']}")
        print(f"🤖 Agents: {', '.join(data['agents'])}")
        print(f"⏰ Timestamp: {data['timestamp']}")
        
    except Exception as e:
        print(f"❌ Error testing main endpoint: {e}")
    
    # Test health endpoint
    try:
        print("\n🔍 Testing health endpoint...")
        response = requests.get(f"{DEPLOYED_URL}/health")
        print(f"✅ Status: {response.status_code}")
        data = response.json()
        print(f"🏥 Health Status: {data['status']}")
        print(f"🤖 Agent Status: {data['agents']}")
        
    except Exception as e:
        print(f"❌ Error testing health endpoint: {e}")
    
    # Test analysis endpoint with HIGH RISK scenario
    try:
        print("\n🔍 Testing disaster analysis with HIGH RISK scenario...")
        
        # Simulate critical disaster conditions
        sensor_data = {
            "sensor_data": [
                {
                    "location": "Hackathon Demo - Data Center",
                    "temperature": 78,  # Critical temperature
                    "smoke_level": 90   # Dangerous smoke
                },
                {
                    "location": "Hackathon Demo - Conference Room", 
                    "temperature": 65,  # Elevated temperature
                    "smoke_level": 15   # Low smoke
                }
            ]
        }
        
        response = requests.post(
            f"{DEPLOYED_URL}/analyze",
            json=sensor_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"✅ Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"⚠️  Overall Risk: {data.get('overall_risk_level', 'Unknown')}")
            print(f"📊 Readings Analyzed: {data.get('total_readings', 0)}")
            
            # Show detailed analysis
            for analysis in data.get('analysis', []):
                risk_emoji = "🚨" if analysis['risk_level'] == 'High' else "⚠️" if analysis['risk_level'] == 'Medium' else "✅"
                print(f"   {risk_emoji} {analysis['location']}: {analysis['risk_level']} Risk")
                if analysis.get('reasons'):
                    print(f"      Reasons: {', '.join(analysis['reasons'])}")
        else:
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing analysis endpoint: {e}")

def demo_real_adk_agents():
    """Demo the real Google ADK agents."""
    
    print("\n🤖 DEMO: Real Google ADK Multi-Agent System")
    print("=" * 60)
    
    # Import the real ADK test
    import sys
    sys.path.append('.')
    
    try:
        # Set API key (you'll need to add your real key)
        os.environ['GOOGLE_API_KEY'] = 'your-api-key-here'
        
        # Import and run the real ADK pipeline
        from test_real_adk_simple import test_disaster_pipeline
        
        print("🧪 Running REAL Google ADK Multi-Agent Pipeline...")
        result = asyncio.run(test_disaster_pipeline())
        
        if result:
            print(f"\n🎉 Real ADK Pipeline Results:")
            print(f"   Session: {result['session_id']}")
            print(f"   Sensor Readings: {result['detection']['total_readings']}")
            print(f"   Risk Level: {result['analysis']['overall_risk_level']}")
            print(f"   Alerts Generated: {result['alerts']['total_alerts']}")
            
            # Show alerts
            for alert in result['alerts'].get('alerts_triggered', []):
                print(f"   🚨 {alert['severity']}: {alert['message']}")
                
    except ImportError:
        print("❌ Google ADK not available - install with: pip install google-adk")
    except Exception as e:
        print(f"❌ Error running real ADK agents: {e}")

def demo_architecture():
    """Show the system architecture."""
    
    print("\n🏗️  DEMO: System Architecture")
    print("=" * 60)
    
    print("""
📋 GOOGLE ADK DISASTER RESPONSE SYSTEM ARCHITECTURE:

🌐 Frontend (React + TypeScript + Vite)
   ├── Modern UI for disaster monitoring
   ├── Real-time sensor data visualization  
   └── Emergency alert dashboard

⚡ Backend (Express.js + FastAPI)
   ├── RESTful API endpoints
   ├── Real-time data processing
   └── Multi-agent coordination

🤖 Agent System (Google ADK + Python)
   ├── DetectionAgent: Sensor data collection
   ├── AnalysisAgent: Risk assessment (High/Medium/Low)
   └── AlertAgent: Emergency response coordination

☁️  Google Cloud Infrastructure
   ├── Cloud Run: Auto-scaling deployment
   ├── Container Registry: Docker image storage
   ├── BigQuery: Data logging and analytics
   └── IAM: Security and authentication

🔄 Multi-Agent Workflow:
   1. DetectionAgent → Collects sensor data
   2. AnalysisAgent → Analyzes risk (temp >50°C or smoke >70% = High Risk)
   3. AlertAgent → Generates emergency alerts and evacuation orders
    """)

def demo_real_world_impact():
    """Show real-world impact and use cases."""
    
    print("\n🌍 DEMO: Real-World Impact")
    print("=" * 60)
    
    print("""
🚨 DISASTER RESPONSE USE CASES:

🔥 Fire Detection & Response
   • Automatic smoke/temperature monitoring
   • Instant evacuation alerts
   • Emergency services coordination

🌊 Flood Monitoring
   • Water level sensors
   • Early warning systems
   • Evacuation route optimization

⚡ Infrastructure Monitoring
   • Data center temperature control
   • Power grid monitoring
   • Critical facility protection

🏥 Healthcare Emergency Response
   • Hospital evacuation protocols
   • Patient safety monitoring
   • Medical equipment alerts

💰 BUSINESS VALUE:
   • Saves lives through early detection
   • Reduces property damage
   • Automates emergency response
   • Scales to any size operation
   • Integrates with existing systems
    """)

def main():
    """Run the complete demo."""
    
    print("🎯 GOOGLE ADK DISASTER RESPONSE SYSTEM")
    print("🏆 HACKATHON DEMO PRESENTATION")
    print("=" * 60)
    print("Built with: Google ADK, Python, React, Google Cloud Run")
    print("Team: Disaster Response AI")
    print("=" * 60)
    
    # Demo components
    demo_deployed_system()
    demo_real_adk_agents() 
    demo_architecture()
    demo_real_world_impact()
    
    print("\n🎉 DEMO COMPLETE!")
    print("🚀 Live System: https://disaster-response-system-838920435800.us-central1.run.app")
    print("📱 Ready for production deployment!")

if __name__ == "__main__":
    main() 