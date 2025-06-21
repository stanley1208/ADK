"""
Disaster Response Orchestrator for Google ADK.

This module provides orchestration capabilities for the disaster response multi-agent system,
using SequentialAgent to coordinate between DetectionAgent, AnalysisAgent, and AlertAgent to 
process sensor data from JSON files, analyze risk levels, and trigger appropriate alerts.
Enhanced with BigQuery logging for historical data storage and analysis.
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from agents.detection_agent import DetectionAgent
from agents.analysis_agent import AnalysisAgent
from agents.alert_agent import AlertAgent

# Try to import Google ADK components, fall back to mocks if not available
try:
    from google.adk.agents import SequentialAgent
    from google.adk.sessions import Session
    ADK_AVAILABLE = True
except ImportError:
    print("⚠️  Google ADK not available, using mock classes for testing")
    from utils.mocks import MockSequentialAgent as SequentialAgent, MockSession as Session
    ADK_AVAILABLE = False


class DisasterResponseOrchestrator:
    """
    Main orchestrator for the disaster response system using SequentialAgent.
    
    Coordinates between DetectionAgent (reads JSON files), AnalysisAgent (analyzes risk),
    and AlertAgent (triggers notifications) in a sequential pipeline to provide 
    comprehensive disaster response with automated alerting and optional BigQuery logging.
    """
    
    def __init__(self, bigquery_config: Optional[Dict[str, str]] = None):
        """
        Initialize the orchestrator with 3-agent sequential workflow and optional BigQuery logging.
        
        Args:
            bigquery_config: Optional BigQuery configuration for DetectionAgent logging:
                - project_id: Google Cloud project ID
                - dataset_id: BigQuery dataset ID (default: "disaster_response")
                - table_id: BigQuery table ID (default: "sensor_readings")
                - location: BigQuery dataset location (default: "US")
        """
        # Initialize individual agents
        self.detection_agent = DetectionAgent(
            name="sensor_detection_agent",
            description="Detects and reads sensor data from JSON files with BigQuery logging",
            bigquery_config=bigquery_config
        )
        
        self.analysis_agent = AnalysisAgent(
            name="disaster_analysis_agent",
            description="Analyzes sensor data to determine risk levels and provide emergency recommendations"
        )
        
        self.alert_agent = AlertAgent(
            name="disaster_alert_agent",
            description="Processes risk analysis results and triggers appropriate alerts based on severity"
        )
        
        # Create sequential workflow with all 3 agents
        self.workflow = SequentialAgent(
            name="disaster_workflow",
            sub_agents=[self.detection_agent, self.analysis_agent, self.alert_agent],
            description="Complete workflow: detect sensor data → analyze risk levels → trigger alerts"
        )
        
        self.session = None
        self.bigquery_config = bigquery_config
    
    async def initialize_session(self) -> Session:
        """
        Initialize an ADK session for agent interactions.
        
        Returns:
            Session: Initialized ADK session object
        """
        self.session = Session(session_id=f"disaster_response_{datetime.now().isoformat()}")
        return self.session
    
    async def run_pipeline(self, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Run the complete detection, analysis, and alert pipeline.
        
        Args:
            input_data: Optional input data containing:
                - file_path: Specific file to process
                - pattern: File pattern to search for
                
        Returns:
            Dictionary containing complete pipeline results with alerts and BigQuery status
        """
        if not self.session:
            await self.initialize_session()
        
        if input_data is None:
            input_data = {}
        
        print(f"🚨 Starting disaster response pipeline at {datetime.now().isoformat()}")
        
        # Run the sequential workflow (Detection → Analysis → Alert)
        result = await self.workflow.run(self.session, input_data)
        
        # Extract and format results
        return self._format_pipeline_results(result)
    
    def _format_pipeline_results(self, workflow_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format the sequential workflow results for better readability.
        
        Args:
            workflow_result: Results from the 3-agent SequentialAgent workflow
            
        Returns:
            Formatted results dictionary with BigQuery logging information
        """
        if not workflow_result.get('results'):
            return {
                "status": "pipeline_failed",
                "error": "No results from workflow",
                "timestamp": datetime.now().isoformat() + 'Z'
            }
        
        # Extract results from each agent
        detection_result = None
        analysis_result = None
        alert_result = None
        
        for step_result in workflow_result['results']:
            agent_name = step_result.get('agent_name')
            if agent_name == 'sensor_detection_agent':
                detection_result = step_result.get('result')
            elif agent_name == 'disaster_analysis_agent':
                analysis_result = step_result.get('result')
            elif agent_name == 'disaster_alert_agent':
                alert_result = step_result.get('result')
        
        # Format final response
        formatted_result = {
            "pipeline_status": workflow_result.get('status', 'unknown'),
            "workflow_name": workflow_result.get('workflow_name'),
            "total_steps": workflow_result.get('total_steps'),
            "completed_steps": workflow_result.get('completed_steps'),
            "timestamp": workflow_result.get('timestamp')
        }
        
        # Add detection information with BigQuery status
        if detection_result:
            formatted_result["detection"] = {
                "status": detection_result.get('status'),
                "file_info": detection_result.get('detection_info'),
                "data_found": detection_result.get('status') == 'data_detected',
                "bigquery_logging": detection_result.get('bigquery_logging', {})
            }
        
        # Add analysis information
        if analysis_result:
            formatted_result["analysis"] = analysis_result
            # Extract key analysis metrics for easy access
            formatted_result["risk_level"] = analysis_result.get('overall_risk_level')
            formatted_result["priority"] = self._determine_priority(analysis_result.get('overall_risk_level'))
        
        # Add alert information
        if alert_result:
            formatted_result["alerts"] = {
                "status": alert_result.get('alert_status'),
                "summary": alert_result.get('alert_summary'),
                "alerts_triggered": alert_result.get('alerts_triggered', []),
                "total_alerts": alert_result.get('alert_summary', {}).get('total_alerts', 0),
                "critical_alerts": alert_result.get('alert_summary', {}).get('critical_alerts', 0)
            }
        
        return formatted_result
    
    def _determine_priority(self, risk_level: str) -> str:
        """
        Determine priority level based on risk assessment.
        
        Args:
            risk_level: Risk level (High, Medium, Low)
            
        Returns:
            Priority level string
        """
        if risk_level == "High":
            return "CRITICAL"
        elif risk_level == "Medium":
            return "HIGH"
        else:
            return "NORMAL"
    
    async def process_file(self, file_path: str) -> Dict[str, Any]:
        """
        Process a specific file through the pipeline.
        
        Args:
            file_path: Path to the JSON file to process
            
        Returns:
            Pipeline results for the specified file
        """
        return await self.run_pipeline({"file_path": file_path})
    
    async def process_directory(self) -> Dict[str, Any]:
        """
        Process the first available file in the simulated_data directory.
        
        Returns:
            Pipeline results for the first available file
        """
        return await self.run_pipeline()
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """
        Get the alert history from the AlertAgent.
        
        Returns:
            List of all alerts that have been triggered
        """
        return self.alert_agent.get_alert_history()
    
    def get_bigquery_status(self) -> Dict[str, Any]:
        """
        Get the BigQuery configuration and status from the DetectionAgent.
        
        Returns:
            Dictionary with BigQuery status information
        """
        return self.detection_agent.get_bigquery_status()
    
    async def query_historical_data(self, location: Optional[str] = None, 
                                   hours_back: int = 24) -> Optional[List[Dict[str, Any]]]:
        """
        Query historical sensor data from BigQuery via the DetectionAgent.
        
        Args:
            location: Optional location filter
            hours_back: Number of hours back to query (default: 24)
            
        Returns:
            List of historical readings or None if BigQuery not available
        """
        return self.detection_agent.query_historical_data(location, hours_back)


async def main():
    """
    Main function demonstrating the complete disaster response pipeline with BigQuery logging.
    
    Creates sample data, runs the pipeline, and displays results including BigQuery status.
    """
    print("=== Disaster Response Pipeline with BigQuery Logging Demo ===\n")
    
    # Configure BigQuery (optional - comment out if you don't have a GCP project)
    # To enable BigQuery logging, set your project ID here:
    bigquery_config = {
        # "project_id": "your-gcp-project-id",  # Uncomment and set your project ID
        # "dataset_id": "disaster_response",    # Optional: custom dataset name
        # "table_id": "sensor_readings",        # Optional: custom table name
        # "location": "US"                      # Optional: custom location
    }
    
    # Initialize orchestrator with optional BigQuery config
    orchestrator = DisasterResponseOrchestrator(
        bigquery_config=bigquery_config if bigquery_config.get("project_id") else None
    )
    
    # Display BigQuery status
    bq_status = orchestrator.get_bigquery_status()
    print("📊 BigQuery Configuration:")
    print(f"   Available: {bq_status['bigquery_available']}")
    print(f"   Enabled: {bq_status['bigquery_enabled']}")
    if bq_status['project_id']:
        print(f"   Project: {bq_status['project_id']}")
        print(f"   Table: {bq_status['full_table_id']}")
    else:
        print("   ⚠️  No project configured - BigQuery logging disabled")
    print()
    
    # Create sample data files with different risk levels for alert testing
    sample_scenarios = [
        {
            "filename": "high_risk_bigquery_demo.json",
            "data": {
                "sensor_data": [
                    {
                        "location": "Data Center - Zone A",
                        "temperature": 78,
                        "smoke_level": 88,
                        "timestamp": "2025-01-11T10:30:00Z"
                    },
                    {
                        "location": "Data Center - Zone B",
                        "temperature": 65,
                        "smoke_level": 75,
                        "timestamp": "2025-01-11T10:31:00Z"
                    }
                ]
            },
            "description": "High Risk Scenario with BigQuery Logging"
        },
        {
            "filename": "low_risk_bigquery_demo.json",
            "data": {
                "sensor_data": [
                    {
                        "location": "Office Building - Floor 1",
                        "temperature": 23,
                        "smoke_level": 6,
                        "timestamp": "2025-01-11T10:32:00Z"
                    }
                ]
            },
            "description": "Low Risk Scenario with BigQuery Logging"
        }
    ]
    
    # Ensure simulated_data directory exists
    data_dir = os.path.join(os.path.dirname(__file__), 'simulated_data')
    os.makedirs(data_dir, exist_ok=True)
    
    for i, scenario in enumerate(sample_scenarios):
        print(f"📋 Scenario {i+1}: {scenario['description']}")
        
        # Create test file
        sample_file_path = os.path.join(data_dir, scenario['filename'])
        import json
        with open(sample_file_path, 'w') as f:
            json.dump(scenario['data'], f, indent=2)
        
        print(f"📁 Created test file: {scenario['filename']}")
        print("📊 Sample sensor data:")
        for reading in scenario['data']["sensor_data"]:
            print(f"  {reading['location']}: {reading['temperature']}°C, {reading['smoke_level']}% smoke")
        print()
        
        try:
            # Run the pipeline
            result = await orchestrator.process_file(scenario['filename'])
            
            print("🔍 Pipeline Results:")
            print(f"Status: {result.get('pipeline_status')}")
            print(f"Steps Completed: {result.get('completed_steps')}/{result.get('total_steps')}")
            print()
            
            # Display detection results with BigQuery status
            if 'detection' in result:
                detection = result['detection']
                print("📂 Detection Results:")
                print(f"  Status: {detection.get('status')}")
                if detection.get('file_info'):
                    file_info = detection['file_info']
                    print(f"  File: {file_info.get('file_name')}")
                
                # Show BigQuery logging status
                bq_logging = detection.get('bigquery_logging', {})
                print(f"  📊 BigQuery Logging:")
                print(f"     Enabled: {bq_logging.get('enabled', False)}")
                print(f"     Status: {bq_logging.get('status', 'unknown')}")
                if bq_logging.get('rows_inserted'):
                    print(f"     Rows Inserted: {bq_logging.get('rows_inserted')}")
                    print(f"     Table: {bq_logging.get('table_id')}")
                elif bq_logging.get('error'):
                    print(f"     Error: {bq_logging.get('error')}")
                print()
            
            # Display analysis results
            if 'analysis' in result:
                analysis = result['analysis']
                print("🔍 Analysis Results:")
                print(f"Overall Risk Level: {analysis.get('overall_risk_level')}")
                print(f"Priority: {result.get('priority')}")
                print(f"Total Readings: {analysis.get('total_readings')}")
                print()
                
                print("📍 Location-Specific Analysis:")
                for location_analysis in analysis.get('analysis', []):
                    print(f"  {location_analysis['location']}: {location_analysis['risk_level']} Risk")
                    for reason in location_analysis['reasons']:
                        print(f"    • {reason}")
                print()
            
            # Display alert results
            if 'alerts' in result:
                alerts = result['alerts']
                print("🚨 Alert Results:")
                print(f"Alert Status: {alerts.get('status')}")
                print(f"Total Alerts: {alerts.get('total_alerts')}")
                print(f"Critical Alerts: {alerts.get('critical_alerts')}")
                
                if alerts.get('alerts_triggered'):
                    print("\n📢 Alerts Triggered:")
                    for alert in alerts['alerts_triggered']:
                        print(f"  • {alert['message']} (Severity: {alert['severity']})")
                print()
            
            print(f"⏰ Pipeline completed at {result.get('timestamp')}")
            print("=" * 70)
            print()
            
        except Exception as e:
            print(f"❌ Pipeline failed: {e}")
            import traceback
            traceback.print_exc()
            print()
        
        finally:
            # Clean up test file
            if os.path.exists(sample_file_path):
                os.remove(sample_file_path)
    
    # Demonstrate historical data querying if BigQuery is enabled
    if bq_status['bigquery_enabled']:
        print("📊 Querying Historical Data from BigQuery...")
        try:
            historical_data = await orchestrator.query_historical_data(hours_back=1)
            if historical_data:
                print(f"   Found {len(historical_data)} historical readings")
                for reading in historical_data[:3]:  # Show first 3
                    print(f"   • {reading['location']}: {reading['temperature']}°C at {reading['sensor_timestamp']}")
            else:
                print("   No historical data found")
        except Exception as e:
            print(f"   Error querying historical data: {e}")
        print()


def run_orchestrator_demo():
    """
    Synchronous wrapper for running the orchestrator demonstration.
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Pipeline interrupted by user")
    except Exception as e:
        print(f"❌ Failed to run orchestrator demo: {e}")


if __name__ == "__main__":
    # Run the demonstration when script is executed directly
    run_orchestrator_demo() 