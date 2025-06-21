"""
Disaster Response System - Main Application Entry Point

This module provides the FastAPI application entry point for the disaster response system
using Google ADK Agent Engine.
"""

import os
import sys
from pathlib import Path

# Add python_agents to Python path
current_dir = Path(__file__).parent
python_agents_dir = current_dir / "python_agents"
sys.path.insert(0, str(python_agents_dir))

try:
    from google_adk.web import get_fast_api_app
    ADK_AVAILABLE = True
except ImportError:
    print("⚠️  Google ADK not available, using fallback web server")
    ADK_AVAILABLE = False

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from datetime import datetime

# Import our agents
from agents.detection_agent import DetectionAgent
from agents.analysis_agent import AnalysisAgent  
from agents.alert_agent import AlertAgent
from orchestrator import DisasterResponseOrchestrator


class SensorDataRequest(BaseModel):
    """Request model for sensor data analysis."""
    sensor_data: List[Dict[str, Any]]
    bigquery_config: Optional[Dict[str, str]] = None


class PipelineRequest(BaseModel):
    """Request model for pipeline execution."""
    file_path: Optional[str] = None
    pattern: Optional[str] = "*.json"
    bigquery_config: Optional[Dict[str, str]] = None


def create_fallback_app() -> FastAPI:
    """Create a fallback FastAPI app when Google ADK is not available."""
    app = FastAPI(
        title="Disaster Response System",
        description="Multi-agent disaster response pipeline with detection, analysis, and alerting",
        version="1.0.0"
    )
    
    # Enable CORS for web interface
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    @app.get("/")
    async def root():
        """Root endpoint with system information."""
        return {
            "message": "Disaster Response System API",
            "version": "1.0.0",
            "status": "operational",
            "agents": ["DetectionAgent", "AnalysisAgent", "AlertAgent"],
            "adk_available": ADK_AVAILABLE,
            "timestamp": datetime.now().isoformat() + 'Z'
        }
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint for container monitoring."""
        try:
            # Test basic agent initialization
            detection_agent = DetectionAgent()
            analysis_agent = AnalysisAgent()
            alert_agent = AlertAgent()
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat() + 'Z',
                "agents": {
                    "detection": detection_agent.name,
                    "analysis": analysis_agent.name,
                    "alerts": alert_agent.name
                },
                "adk_available": ADK_AVAILABLE
            }
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")
    
    @app.post("/analyze")
    async def analyze_sensor_data(request: SensorDataRequest):
        """Analyze sensor data directly through AnalysisAgent."""
        try:
            # Initialize analysis agent
            analysis_agent = AnalysisAgent()
            
            # Run analysis
            from utils.mocks import MockSession
            session = MockSession("api_session")
            result = await analysis_agent.run(session, {"sensor_data": request.sensor_data})
            
            return {
                "status": "success",
                "analysis_result": result,
                "timestamp": datetime.now().isoformat() + 'Z'
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    
    @app.post("/pipeline")
    async def run_pipeline(request: PipelineRequest):
        """Run the complete detection, analysis, and alert pipeline."""
        try:
            # Initialize orchestrator with optional BigQuery config
            orchestrator = DisasterResponseOrchestrator(
                bigquery_config=request.bigquery_config
            )
            
            # Prepare input data
            input_data = {}
            if request.file_path:
                input_data["file_path"] = request.file_path
            if request.pattern:
                input_data["pattern"] = request.pattern
            
            # Run pipeline
            result = await orchestrator.run_pipeline(input_data)
            
            return {
                "status": "success",
                "pipeline_result": result,
                "timestamp": datetime.now().isoformat() + 'Z'
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pipeline failed: {str(e)}")
    
    @app.get("/status")
    async def system_status():
        """Get comprehensive system status including BigQuery configuration."""
        try:
            orchestrator = DisasterResponseOrchestrator()
            bq_status = orchestrator.get_bigquery_status()
            
            return {
                "system": "operational",
                "agents": {
                    "detection": "ready",
                    "analysis": "ready", 
                    "alerts": "ready"
                },
                "bigquery": bq_status,
                "adk_available": ADK_AVAILABLE,
                "timestamp": datetime.now().isoformat() + 'Z'
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")
    
    return app


def get_app() -> FastAPI:
    """Get the FastAPI application, using ADK if available or fallback otherwise."""
    if ADK_AVAILABLE:
        try:
            # Get ADK FastAPI app
            agents_dir = str(python_agents_dir / "agents")
            app = get_fast_api_app(agents_dir=agents_dir, serve_web=True)
            
            print(f"✅ Google ADK FastAPI app initialized with agents from: {agents_dir}")
            return app
            
        except Exception as e:
            print(f"⚠️  Failed to initialize ADK app: {e}")
            print("   Falling back to custom FastAPI app")
            return create_fallback_app()
    else:
        print("📡 Using fallback FastAPI app (ADK not available)")
        return create_fallback_app()


# Create the FastAPI application
app = get_app()


if __name__ == "__main__":
    # Get port from environment or default to 8080
    port = int(os.environ.get("PORT", 8080))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Starting Disaster Response System on {host}:{port}")
    print(f"📊 ADK Available: {ADK_AVAILABLE}")
    print(f"📁 Python Agents Directory: {python_agents_dir}")
    
    # Run the server
    uvicorn.run(
        app, 
        host=host, 
        port=port,
        log_level="info",
        access_log=True
    ) 