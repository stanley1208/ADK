"""
Test script for the Google ADK-wrapped disaster response system.

This script tests the AnalysisAgent and DisasterResponseOrchestrator
to ensure they work correctly both with and without Google ADK installed.
"""

import asyncio
from orchestrator import run_orchestrator_demo, DisasterResponseOrchestrator


async def test_individual_components():
    """Test individual components of the system."""
    print("=== Testing Individual Components ===\n")
    
    # Test orchestrator initialization
    print("1. Testing Orchestrator Initialization...")
    orchestrator = DisasterResponseOrchestrator()
    print(f"   ✅ Orchestrator created: {orchestrator.analysis_agent.name}")
    print(f"   📋 Agent description: {orchestrator.analysis_agent.description}")
    print()
    
    # Test simple sensor data analysis
    print("2. Testing Simple Sensor Data Analysis...")
    simple_data = {
        "sensor_data": [{
            "location": "Test Room",
            "temperature": 30,
            "smoke_level": 20,
            "timestamp": "2025-01-11T12:00:00Z"
        }]
    }
    
    result = await orchestrator.analyze_sensor_data(simple_data)
    print(f"   ✅ Analysis completed: {result['overall_risk_level']} risk")
    print(f"   📊 Total readings: {result['total_readings']}")
    print()
    
    # Test emergency request processing
    print("3. Testing Emergency Request Processing...")
    emergency_data = {
        "sensor_data": [{
            "location": "Emergency Test Location",
            "temperature": 80,
            "smoke_level": 90,
            "timestamp": "2025-01-11T12:05:00Z"
        }]
    }
    
    emergency_result = await orchestrator.process_emergency_request(emergency_data)
    print(f"   🚨 Emergency analysis: {emergency_result['overall_risk_level']} risk")
    print(f"   ⚡ Priority: {emergency_result['priority']}")
    print(f"   📋 Action count: {len(emergency_result['emergency_actions'])}")
    print()


def test_sync_functionality():
    """Test synchronous functionality."""
    print("=== Testing Synchronous Functionality ===\n")
    
    # Test the sync wrapper
    print("Running full orchestrator demo...")
    try:
        run_orchestrator_demo()
        print("✅ Orchestrator demo completed successfully!")
    except Exception as e:
        print(f"❌ Error in orchestrator demo: {e}")


async def main():
    """Main test function."""
    print("🧪 Starting Disaster Response System Tests\n")
    
    # Test individual components
    await test_individual_components()
    
    # Test sync functionality
    test_sync_functionality()
    
    print("\n🎉 All tests completed!")


if __name__ == "__main__":
    asyncio.run(main()) 