"""
Disaster Response Orchestrator for Google ADK.

This module provides orchestration capabilities for the disaster response multi-agent system,
coordinating between various agents to analyze sensor data and determine risk levels.
The orchestrator initializes agents, manages their interactions, and processes requests.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from agents.analysis_agent import AnalysisAgent

# Try to import Google ADK Session, fall back to mock if not available
try:
    from google.adk.sessions import Session
    ADK_AVAILABLE = True
except ImportError:
    print("⚠️  Google ADK not available, using mock Session class")
    from utils.mocks import MockSession as Session
    ADK_AVAILABLE = False


class DisasterResponseOrchestrator:
    """
    Main orchestrator for the disaster response system.
    
    Coordinates between various agents (currently AnalysisAgent) to process
    sensor data and provide comprehensive risk assessments for emergency
    response coordination.
    """
    
    def __init__(self):
        """Initialize the orchestrator with required agents."""
        self.analysis_agent = AnalysisAgent(
            name="disaster_analysis_agent",
            description=(
                "Specialized agent for disaster risk assessment based on "
                "temperature and smoke sensor readings from multiple locations."
            )
        )
        self.session = None
    
    async def initialize_session(self) -> Session:
        """
        Initialize an ADK session for agent interactions.
        
        Returns:
            Session: Initialized ADK session object
        """
        # In a real implementation, this would create a proper ADK session
        # For now, we'll create a mock session object
        self.session = Session(session_id=f"disaster_response_{datetime.now().isoformat()}")
        return self.session
    
    async def analyze_sensor_data(self, sensor_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process sensor data through the analysis agent to determine risk levels.
        
        Args:
            sensor_data (Dict[str, Any]): Dictionary containing sensor readings.
                Expected format:
                {
                    "sensor_data": [
                        {
                            "location": str,           # Location identifier
                            "temperature": float,      # Temperature in Celsius  
                            "smoke_level": float,      # Smoke percentage (0-100)
                            "timestamp": str           # ISO format timestamp
                        },
                        ... additional readings
                    ]
                }
        
        Returns:
            Dict[str, Any]: Risk analysis results containing:
                {
                    "overall_risk_level": str,     # "Low", "Medium", or "High"
                    "total_readings": int,         # Number of sensor readings processed
                    "analysis": List[Dict],        # Detailed analysis per location
                    "timestamp": str,              # Analysis timestamp
                    "agent_info": Dict            # Information about the analyzing agent
                }
        """
        if not self.session:
            await self.initialize_session()
        
        # Process the sensor data through the analysis agent
        result = await self.analysis_agent.run(self.session, sensor_data)
        
        # Add orchestrator metadata
        result["agent_info"] = {
            "agent_name": self.analysis_agent.name,
            "agent_description": self.analysis_agent.description,
            "processing_timestamp": datetime.now().isoformat() + 'Z'
        }
        
        return result
    
    async def process_emergency_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an emergency request with sensor data and return comprehensive analysis.
        
        Args:
            request_data (Dict[str, Any]): Emergency request containing sensor data
            
        Returns:
            Dict[str, Any]: Comprehensive emergency response analysis
        """
        print(f"🚨 Processing emergency request at {datetime.now().isoformat()}")
        
        # Analyze the sensor data
        analysis_result = await self.analyze_sensor_data(request_data)
        
        # Add emergency response recommendations based on risk level
        risk_level = analysis_result["overall_risk_level"]
        
        if risk_level == "High":
            analysis_result["emergency_actions"] = [
                "IMMEDIATE EVACUATION required for affected areas",
                "Deploy emergency response teams to high-risk locations",
                "Activate fire suppression systems if available",
                "Notify emergency services and local authorities",
                "Establish emergency communication protocols"
            ]
            analysis_result["priority"] = "CRITICAL"
        elif risk_level == "Medium":
            analysis_result["emergency_actions"] = [
                "Monitor situation closely for escalation",
                "Prepare evacuation plans for affected areas", 
                "Alert emergency response teams to standby",
                "Increase sensor monitoring frequency",
                "Notify facility management and safety teams"
            ]
            analysis_result["priority"] = "HIGH"
        else:
            analysis_result["emergency_actions"] = [
                "Continue routine monitoring",
                "Log readings for trend analysis",
                "Maintain standard safety protocols"
            ]
            analysis_result["priority"] = "NORMAL"
        
        return analysis_result


async def run_sample_analysis():
    """
    Demonstration function showing how to use the orchestrator with sample data.
    
    This function creates sample sensor data, processes it through the orchestrator,
    and displays the results. Useful for testing and demonstration purposes.
    """
    print("=== Disaster Response Orchestrator Demo ===\n")
    
    # Initialize the orchestrator
    orchestrator = DisasterResponseOrchestrator()
    
    # Sample sensor data representing different risk scenarios
    sample_data = {
        "sensor_data": [
            {
                "location": "Building A - Floor 3",
                "temperature": 25,
                "smoke_level": 15,
                "timestamp": "2025-01-11T10:30:00Z"
            },
            {
                "location": "Building B - Basement",
                "temperature": 45,
                "smoke_level": 55,
                "timestamp": "2025-01-11T10:31:00Z"
            },
            {
                "location": "Building C - Server Room",
                "temperature": 75,
                "smoke_level": 85,
                "timestamp": "2025-01-11T10:32:00Z"
            }
        ]
    }
    
    print("📊 Sample Sensor Data:")
    for reading in sample_data["sensor_data"]:
        print(f"  {reading['location']}: {reading['temperature']}°C, {reading['smoke_level']}% smoke")
    print()
    
    # Process the emergency request
    try:
        result = await orchestrator.process_emergency_request(sample_data)
        
        print("🔍 Analysis Results:")
        print(f"Overall Risk Level: {result['overall_risk_level']}")
        print(f"Priority: {result['priority']}")
        print(f"Total Readings Processed: {result['total_readings']}")
        print()
        
        print("📍 Location-Specific Analysis:")
        for analysis in result["analysis"]:
            print(f"  {analysis['location']}: {analysis['risk_level']} Risk")
            for reason in analysis['reasons']:
                print(f"    • {reason}")
        print()
        
        print("⚡ Recommended Emergency Actions:")
        for action in result["emergency_actions"]:
            print(f"  • {action}")
        print()
        
        print(f"🤖 Agent: {result['agent_info']['agent_name']}")
        print(f"📋 Description: {result['agent_info']['agent_description']}")
        
    except Exception as e:
        print(f"❌ Error processing emergency request: {e}")


# Standalone orchestrator functions for simple use cases
async def analyze_sensor_data_simple(sensor_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simple function for analyzing sensor data without full orchestrator setup.
    
    Args:
        sensor_data (Dict[str, Any]): Sensor data dictionary
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    orchestrator = DisasterResponseOrchestrator()
    return await orchestrator.analyze_sensor_data(sensor_data)


def run_orchestrator_demo():
    """
    Synchronous wrapper for running the orchestrator demonstration.
    """
    asyncio.run(run_sample_analysis())


if __name__ == "__main__":
    # Run the demonstration when script is executed directly
    run_orchestrator_demo() 