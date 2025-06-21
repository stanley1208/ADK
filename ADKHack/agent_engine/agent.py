"""
Disaster Response System - Agent Engine Root Agent

This module defines the root agent for deployment to Vertex AI Agent Engine.
The root agent orchestrates the complete disaster response pipeline using
SequentialAgent to coordinate detection, analysis, and alerting.
"""

import sys
import os
from pathlib import Path

# Add python_agents to Python path for imports
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
python_agents_dir = parent_dir / "python_agents"
sys.path.insert(0, str(python_agents_dir))

try:
    from google.adk.agents import SequentialAgent
    from agents.detection_agent import DetectionAgent
    from agents.analysis_agent import AnalysisAgent
    from agents.alert_agent import AlertAgent
    ADK_AVAILABLE = True
except ImportError:
    print("⚠️  Google ADK not available, using mock classes")
    from python_agents.utils.mocks import MockSequentialAgent as SequentialAgent
    from python_agents.agents.detection_agent import DetectionAgent
    from python_agents.agents.analysis_agent import AnalysisAgent
    from python_agents.agents.alert_agent import AlertAgent
    ADK_AVAILABLE = False

# Root agent for Vertex AI Agent Engine deployment
root_agent = SequentialAgent(
    name="disaster_response_agent",
    description="Complete disaster response pipeline: detection → analysis → alert",
    sub_agents=[
        DetectionAgent(
            name="sensor_detection_agent",
            description="Detects and reads sensor data from JSON files with BigQuery logging"
        ),
        AnalysisAgent(
            name="disaster_analysis_agent", 
            description="Analyzes sensor data to determine risk levels (Low/Medium/High)"
        ),
        AlertAgent(
            name="disaster_alert_agent",
            description="Processes risk analysis and triggers appropriate alerts"
        )
    ]
)

# Agent metadata for Vertex AI Agent Engine
AGENT_CONFIG = {
    "name": "disaster_response_agent",
    "version": "1.0.0",
    "description": "AI-powered disaster response system with multi-agent pipeline",
    "capabilities": [
        "sensor_data_detection",
        "risk_analysis", 
        "emergency_alerting",
        "bigquery_logging",
        "historical_data_query"
    ],
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to JSON file containing sensor data"
            },
            "pattern": {
                "type": "string", 
                "description": "File pattern to match (default: *.json)",
                "default": "*.json"
            },
            "bigquery_config": {
                "type": "object",
                "description": "Optional BigQuery configuration for data logging",
                "properties": {
                    "project_id": {"type": "string"},
                    "dataset_id": {"type": "string"},
                    "table_id": {"type": "string"},
                    "location": {"type": "string"}
                }
            }
        }
    },
    "output_schema": {
        "type": "object",
        "properties": {
            "pipeline_status": {
                "type": "string",
                "enum": ["completed", "failed"]
            },
            "risk_level": {
                "type": "string", 
                "enum": ["Low", "Medium", "High"]
            },
            "priority": {
                "type": "string",
                "enum": ["NORMAL", "HIGH", "CRITICAL"] 
            },
            "detection": {
                "type": "object",
                "description": "Detection agent results"
            },
            "analysis": {
                "type": "object", 
                "description": "Risk analysis results"
            },
            "alerts": {
                "type": "object",
                "description": "Alert processing results"
            }
        }
    },
    "environment": {
        "python_version": "3.10",
        "dependencies": [
            "google-adk>=1.0.0",
            "google-cloud-bigquery>=3.0.0",
            "fastapi>=0.104.0",
            "pydantic>=2.0.0"
        ]
    },
    "deployment": {
        "platform": "vertex_ai_agent_engine",
        "region": "us-central1",
        "scaling": {
            "min_instances": 0,
            "max_instances": 10,
            "target_cpu_utilization": 70
        }
    }
}

# Export for Agent Engine discovery
__all__ = ["root_agent", "AGENT_CONFIG"] 