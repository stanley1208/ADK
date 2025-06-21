"""
Test script for the Google ADK-wrapped disaster response pipeline system.

This script tests the DetectionAgent, AnalysisAgent, AlertAgent, and DisasterResponseOrchestrator
with SequentialAgent to ensure the complete 3-agent pipeline works correctly both with and without Google ADK installed.
Enhanced with BigQuery logging tests to verify data storage functionality.
"""

import asyncio
import os
import json
import tempfile
import shutil
import io
import sys
from contextlib import redirect_stdout
from orchestrator import run_orchestrator_demo, DisasterResponseOrchestrator
from agents.detection_agent import DetectionAgent
from agents.analysis_agent import AnalysisAgent
from agents.alert_agent import AlertAgent


async def test_individual_agents():
    """Test individual agents separately."""
    print("=== Testing Individual Agents ===\n")
    
    # Test DetectionAgent
    print("1. Testing DetectionAgent...")
    detection_agent = DetectionAgent()
    print(f"   ✅ DetectionAgent created: {detection_agent.name}")
    print(f"   📁 Data directory: {detection_agent.get_data_directory()}")
    
    # Test BigQuery status
    bq_status = detection_agent.get_bigquery_status()
    print(f"   📊 BigQuery Available: {bq_status['bigquery_available']}")
    print(f"   📊 BigQuery Enabled: {bq_status['bigquery_enabled']}")
    
    # Create temporary test file
    test_data = {
        "sensor_data": [{
            "location": "Test Detection Room",
            "temperature": 25,
            "smoke_level": 10,
            "timestamp": "2025-01-11T12:00:00Z"
        }]
    }
    
    # Ensure test directory exists
    os.makedirs(detection_agent.get_data_directory(), exist_ok=True)
    test_file_path = os.path.join(detection_agent.get_data_directory(), "test_detection.json")
    
    with open(test_file_path, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    # Test detection
    from utils.mocks import MockSession
    session = MockSession("test_detection_session")
    detection_result = await detection_agent.run(session, {})
    
    print(f"   ✅ Detection status: {detection_result.get('status')}")
    print(f"   📊 Sensor data found: {len(detection_result.get('sensor_data', []))} readings")
    
    # Check BigQuery logging status in result
    bq_logging = detection_result.get('bigquery_logging', {})
    print(f"   📊 BigQuery logging status: {bq_logging.get('status', 'unknown')}")
    print()
    
    # Test AnalysisAgent
    print("2. Testing AnalysisAgent...")
    analysis_agent = AnalysisAgent()
    print(f"   ✅ AnalysisAgent created: {analysis_agent.name}")
    
    # Test analysis with the detected data
    if detection_result.get('status') == 'data_detected':
        analysis_result = await analysis_agent.run(session, {"sensor_data": detection_result['sensor_data']})
        print(f"   ✅ Analysis completed: {analysis_result['overall_risk_level']} risk")
        print(f"   📊 Total readings: {analysis_result['total_readings']}")
    print()
    
    # Test AlertAgent
    print("3. Testing AlertAgent...")
    alert_agent = AlertAgent()
    print(f"   ✅ AlertAgent created: {alert_agent.name}")
    
    # Test alert with analysis data
    if analysis_result:
        # Capture stdout to check for alert printing
        alert_output = io.StringIO()
        with redirect_stdout(alert_output):
            alert_result = await alert_agent.run(session, analysis_result)
        
        alert_text = alert_output.getvalue()
        print(f"   ✅ Alert processing: {alert_result.get('alert_status')}")
        print(f"   📢 Total alerts: {alert_result.get('alert_summary', {}).get('total_alerts', 0)}")
        print(f"   🚨 Critical alerts: {alert_result.get('alert_summary', {}).get('critical_alerts', 0)}")
        if alert_text.strip():
            print(f"   📝 Alert output captured: {alert_text.strip()}")
    print()


async def test_bigquery_functionality():
    """Test BigQuery-specific functionality."""
    print("=== Testing BigQuery Functionality ===\n")
    
    # Test 1: DetectionAgent without BigQuery config
    print("1. Testing DetectionAgent without BigQuery...")
    detection_agent_no_bq = DetectionAgent()
    bq_status = detection_agent_no_bq.get_bigquery_status()
    
    print(f"   📊 BigQuery Available: {bq_status['bigquery_available']}")
    print(f"   📊 BigQuery Enabled: {bq_status['bigquery_enabled']}")
    
    if not bq_status['bigquery_enabled']:
        print("   ✅ BigQuery correctly disabled without configuration")
    else:
        print("   ❌ BigQuery unexpectedly enabled")
    print()
    
    # Test 2: DetectionAgent with BigQuery config (but likely no real project)
    print("2. Testing DetectionAgent with BigQuery config...")
    test_bigquery_config = {
        "project_id": "test-project-id",
        "dataset_id": "test_dataset",
        "table_id": "test_table"
    }
    
    detection_agent_with_bq = DetectionAgent(bigquery_config=test_bigquery_config)
    bq_status_with_config = detection_agent_with_bq.get_bigquery_status()
    
    print(f"   📊 Project ID: {bq_status_with_config['project_id']}")
    print(f"   📊 Dataset ID: {bq_status_with_config['dataset_id']}")
    print(f"   📊 Table ID: {bq_status_with_config['table_id']}")
    print(f"   📊 BigQuery Enabled: {bq_status_with_config['bigquery_enabled']}")
    
    if not bq_status_with_config['bigquery_enabled']:
        print("   ✅ BigQuery correctly disabled (likely no valid GCP credentials)")
    else:
        print("   ✅ BigQuery successfully enabled with valid credentials")
    print()
    
    # Test 3: Orchestrator with BigQuery config
    print("3. Testing Orchestrator with BigQuery config...")
    orchestrator_with_bq = DisasterResponseOrchestrator(bigquery_config=test_bigquery_config)
    orchestrator_bq_status = orchestrator_with_bq.get_bigquery_status()
    
    print(f"   📊 Orchestrator BigQuery Status: {orchestrator_bq_status['bigquery_enabled']}")
    print(f"   📊 Full Table ID: {orchestrator_bq_status.get('full_table_id', 'Not configured')}")
    print()
    
    # Test 4: Data detection with BigQuery logging attempt
    print("4. Testing data detection with BigQuery logging...")
    
    # Create test data
    test_data = {
        "sensor_data": [{
            "location": "BigQuery Test Location",
            "temperature": 35,
            "smoke_level": 25,
            "timestamp": "2025-01-11T13:00:00Z"
        }]
    }
    
    data_dir = os.path.join(os.path.dirname(__file__), 'simulated_data')
    os.makedirs(data_dir, exist_ok=True)
    test_file_path = os.path.join(data_dir, "bigquery_test.json")
    
    with open(test_file_path, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    # Run detection with BigQuery config
    from utils.mocks import MockSession
    session = MockSession("bigquery_test_session")
    result = await detection_agent_with_bq.run(session, {"file_path": "bigquery_test.json"})
    
    # Check BigQuery logging in result
    bq_logging = result.get('bigquery_logging', {})
    print(f"   📊 Detection Status: {result.get('status')}")
    print(f"   📊 BigQuery Logging Enabled: {bq_logging.get('enabled', False)}")
    print(f"   📊 BigQuery Logging Status: {bq_logging.get('status', 'unknown')}")
    
    if bq_logging.get('status') == 'bigquery_not_enabled':
        print("   ✅ BigQuery logging correctly reports as not enabled")
    elif bq_logging.get('status') == 'success':
        print(f"   ✅ BigQuery logging successful: {bq_logging.get('rows_inserted')} rows")
    elif bq_logging.get('status') == 'error':
        print(f"   ⚠️  BigQuery logging error (expected): {bq_logging.get('error')}")
    
    # Clean up test file
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
    print()


async def test_pipeline_functionality():
    """Test the complete 3-agent sequential pipeline."""
    print("=== Testing 3-Agent Pipeline Functionality ===\n")
    
    # Initialize orchestrator
    print("1. Testing 3-Agent Pipeline Initialization...")
    orchestrator = DisasterResponseOrchestrator()
    print(f"   ✅ Orchestrator created with workflow: {orchestrator.workflow.name}")
    print(f"   🔗 Sub-agents: {len(orchestrator.workflow.sub_agents)}")
    for i, agent in enumerate(orchestrator.workflow.sub_agents):
        print(f"      {i+1}. {agent.name}")
    print()
    
    # Create test data files with different risk levels
    test_scenarios = [
        {
            "filename": "low_risk_test.json",
            "data": {
                "sensor_data": [{
                    "location": "Safe Area",
                    "temperature": 22,
                    "smoke_level": 5,
                    "timestamp": "2025-01-11T12:00:00Z"
                }]
            },
            "expected_risk": "Low",
            "should_have_critical_alerts": False
        },
        {
            "filename": "medium_risk_test.json",
            "data": {
                "sensor_data": [{
                    "location": "Moderate Risk Area",
                    "temperature": 40,
                    "smoke_level": 50,
                    "timestamp": "2025-01-11T12:01:00Z"
                }]
            },
            "expected_risk": "Medium",
            "should_have_critical_alerts": False
        },
        {
            "filename": "high_risk_test.json",
            "data": {
                "sensor_data": [{
                    "location": "Danger Zone",
                    "temperature": 70,
                    "smoke_level": 80,
                    "timestamp": "2025-01-11T12:02:00Z"
                }]
            },
            "expected_risk": "High",
            "should_have_critical_alerts": True
        }
    ]
    
    # Ensure simulated_data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), 'simulated_data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Test each scenario
    for i, scenario in enumerate(test_scenarios):
        print(f"{i+2}. Testing {scenario['expected_risk']} Risk Pipeline...")
        
        # Create test file
        test_file_path = os.path.join(data_dir, scenario['filename'])
        with open(test_file_path, 'w') as f:
            json.dump(scenario['data'], f, indent=2)
        
        # Capture stdout to check for alert printing
        pipeline_output = io.StringIO()
        
        with redirect_stdout(pipeline_output):
            # Run pipeline on specific file
            result = await orchestrator.process_file(scenario['filename'])
        
        captured_output = pipeline_output.getvalue()
        
        # Verify results
        detected_risk = result.get('risk_level')
        print(f"   📊 Expected: {scenario['expected_risk']}, Got: {detected_risk}")
        
        if detected_risk == scenario['expected_risk']:
            print(f"   ✅ Risk assessment correct!")
        else:
            print(f"   ❌ Risk assessment mismatch!")
        
        # Check alert functionality
        alerts = result.get('alerts', {})
        critical_alerts = alerts.get('critical_alerts', 0)
        
        if scenario['should_have_critical_alerts']:
            if critical_alerts > 0:
                print(f"   ✅ Critical alerts triggered as expected: {critical_alerts}")
            else:
                print(f"   ❌ Expected critical alerts but got none!")
            
            # Check if alert was printed to stdout
            if "🚨 ALERT: High risk detected" in captured_output:
                print(f"   ✅ Alert message printed to stdout")
            else:
                print(f"   ❌ Expected alert message in output but not found")
        else:
            if critical_alerts == 0:
                print(f"   ✅ No critical alerts as expected")
            else:
                print(f"   ❌ Unexpected critical alerts: {critical_alerts}")
        
        # Check BigQuery logging status
        detection = result.get('detection', {})
        bq_logging = detection.get('bigquery_logging', {})
        print(f"   📊 BigQuery logging: {bq_logging.get('status', 'unknown')}")
        
        print(f"   🔍 Pipeline status: {result.get('pipeline_status')}")
        print(f"   📂 Detection status: {result.get('detection', {}).get('status')}")
        print(f"   🚨 Total alerts: {alerts.get('total_alerts', 0)}")
        print()
        
        # Clean up test file
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


async def test_alert_scenarios():
    """Test specific alert scenarios in detail."""
    print("=== Testing Alert Scenarios ===\n")
    
    orchestrator = DisasterResponseOrchestrator()
    data_dir = os.path.join(os.path.dirname(__file__), 'simulated_data')
    os.makedirs(data_dir, exist_ok=True)
    
    # Test 1: High Risk - Should trigger alerts
    print("1. Testing High Risk Alert Triggering...")
    high_risk_data = {
        "sensor_data": [
            {
                "location": "Emergency Test Building",
                "temperature": 85,
                "smoke_level": 95,
                "timestamp": "2025-01-11T15:00:00Z"
            }
        ]
    }
    
    test_file = os.path.join(data_dir, "high_risk_alert_test.json")
    with open(test_file, 'w') as f:
        json.dump(high_risk_data, f, indent=2)
    
    # Capture both stdout and the result
    alert_output = io.StringIO()
    with redirect_stdout(alert_output):
        result = await orchestrator.process_file("high_risk_alert_test.json")
    
    alert_text = alert_output.getvalue()
    
    # Verify alert was triggered
    alerts = result.get('alerts', {})
    print(f"   📊 Risk Level: {result.get('risk_level')}")
    print(f"   🚨 Critical Alerts: {alerts.get('critical_alerts', 0)}")
    print(f"   📢 Total Alerts: {alerts.get('total_alerts', 0)}")
    
    if alerts.get('critical_alerts', 0) > 0:
        print(f"   ✅ Critical alerts triggered correctly")
    else:
        print(f"   ❌ Expected critical alerts but none triggered")
    
    if "🚨 ALERT: High risk detected at Emergency Test Building" in alert_text:
        print(f"   ✅ Alert message printed correctly")
    else:
        print(f"   ❌ Expected specific alert message not found")
        print(f"   📝 Actual output: {alert_text}")
    
    # Clean up
    os.remove(test_file)
    print()
    
    # Test 2: Low Risk - Should not trigger critical alerts
    print("2. Testing Low Risk - No Critical Alerts...")
    low_risk_data = {
        "sensor_data": [
            {
                "location": "Safe Test Building",
                "temperature": 20,
                "smoke_level": 3,
                "timestamp": "2025-01-11T15:01:00Z"
            }
        ]
    }
    
    test_file = os.path.join(data_dir, "low_risk_no_alert_test.json")
    with open(test_file, 'w') as f:
        json.dump(low_risk_data, f, indent=2)
    
    # Capture output
    no_alert_output = io.StringIO()
    with redirect_stdout(no_alert_output):
        result = await orchestrator.process_file("low_risk_no_alert_test.json")
    
    no_alert_text = no_alert_output.getvalue()
    
    # Verify no critical alerts
    alerts = result.get('alerts', {})
    print(f"   📊 Risk Level: {result.get('risk_level')}")
    print(f"   🚨 Critical Alerts: {alerts.get('critical_alerts', 0)}")
    print(f"   📢 Total Alerts: {alerts.get('total_alerts', 0)}")
    
    if alerts.get('critical_alerts', 0) == 0:
        print(f"   ✅ No critical alerts as expected")
    else:
        print(f"   ❌ Unexpected critical alerts triggered")
    
    if "🚨 ALERT: High risk detected" not in no_alert_text:
        print(f"   ✅ No critical alert messages printed")
    else:
        print(f"   ❌ Unexpected critical alert message found")
    
    # Clean up
    os.remove(test_file)
    print()


async def test_error_handling():
    """Test error handling scenarios."""
    print("=== Testing Error Handling ===\n")
    
    orchestrator = DisasterResponseOrchestrator()
    
    # Test with non-existent file
    print("1. Testing Non-existent File...")
    result = await orchestrator.process_file("non_existent_file.json")
    print(f"   📂 Detection status: {result.get('detection', {}).get('status')}")
    print(f"   🔍 Pipeline status: {result.get('pipeline_status')}")
    
    # Check BigQuery logging status for error case
    bq_logging = result.get('detection', {}).get('bigquery_logging', {})
    print(f"   📊 BigQuery logging: {bq_logging.get('status', 'unknown')}")
    print()
    
    # Test with empty directory
    print("2. Testing Empty Directory...")
    # Temporarily clear the directory
    data_dir = os.path.join(os.path.dirname(__file__), 'simulated_data')
    if os.path.exists(data_dir):
        # Remove all JSON files
        for file in os.listdir(data_dir):
            if file.endswith('.json'):
                os.remove(os.path.join(data_dir, file))
    
    result = await orchestrator.process_directory()
    print(f"   📂 Detection status: {result.get('detection', {}).get('status')}")
    print(f"   🔍 Pipeline status: {result.get('pipeline_status')}")
    
    # Check BigQuery logging status for no data case
    bq_logging = result.get('detection', {}).get('bigquery_logging', {})
    print(f"   📊 BigQuery logging: {bq_logging.get('status', 'unknown')}")
    print()
    
    # Test with invalid JSON
    print("3. Testing Invalid JSON...")
    invalid_file_path = os.path.join(data_dir, "invalid.json")
    with open(invalid_file_path, 'w') as f:
        f.write("{ invalid json content")
    
    result = await orchestrator.process_file("invalid.json")
    print(f"   📂 Detection status: {result.get('detection', {}).get('status')}")
    print(f"   🔍 Pipeline status: {result.get('pipeline_status')}")
    
    # Check BigQuery logging status for invalid JSON case
    bq_logging = result.get('detection', {}).get('bigquery_logging', {})
    print(f"   📊 BigQuery logging: {bq_logging.get('status', 'unknown')}")
    print()
    
    # Clean up
    if os.path.exists(invalid_file_path):
        os.remove(invalid_file_path)


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
        import traceback
        traceback.print_exc()


async def main():
    """Main test function."""
    print("🧪 Starting Disaster Response 3-Agent Pipeline Tests with BigQuery\n")
    
    try:
        # Test individual agents
        await test_individual_agents()
        
        # Test BigQuery functionality
        await test_bigquery_functionality()
        
        # Test pipeline functionality
        await test_pipeline_functionality()
        
        # Test specific alert scenarios
        await test_alert_scenarios()
        
        # Test error handling
        await test_error_handling()
        
        # Test sync functionality
        test_sync_functionality()
        
        print("\n🎉 All 3-agent pipeline tests with BigQuery completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        import traceback
        traceback.print_exc()


def run_tests():
    """Synchronous wrapper for running tests."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")


if __name__ == "__main__":
    run_tests() 