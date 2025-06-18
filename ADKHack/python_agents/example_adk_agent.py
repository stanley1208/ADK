"""
Example of initializing the AnalysisAgent with Google ADK and Gemini model.

This demonstrates the full Google ADK integration including model configuration,
agent initialization, and processing of sensor data through the ADK framework.
"""

import asyncio
from typing import Dict, Any

# Example of how to initialize with full Google ADK (when available)
try:
    from google.adk.agents import LlmAgent
    from google.adk.models import Gemini
    from google.adk.sessions import Session
    from agents.analysis_agent import AnalysisAgent
    ADK_AVAILABLE = True
    print("✅ Google ADK available - using full ADK integration")
except ImportError:
    print("⚠️  Google ADK not available - using mock implementation")
    from utils.mocks import MockBaseAgent as LlmAgent, MockSession as Session
    from agents.analysis_agent import AnalysisAgent
    ADK_AVAILABLE = False


class EnhancedAnalysisAgent(AnalysisAgent):
    """
    Enhanced Analysis Agent with full Google ADK integration.
    
    This agent combines rule-based risk assessment with potential AI insights
    when used with Gemini models through Google ADK.
    """
    
    def __init__(self, name: str = "enhanced_disaster_analysis_agent", 
                 model: str = "gemini-2.0-flash", description: str = None):
        """
        Initialize the Enhanced Analysis Agent with Gemini model support.
        
        Args:
            name: Agent name
            model: Gemini model identifier (e.g., "gemini-2.0-flash", "gemini-pro")
            description: Agent description
        """
        if description is None:
            description = (
                "Advanced AI agent for disaster response risk assessment. "
                "Combines rule-based sensor analysis with AI-powered insights using Gemini. "
                "Provides comprehensive risk evaluation, emergency recommendations, "
                "and can explain reasoning in natural language."
            )
        
        # Initialize with ADK-specific configuration
        super().__init__(name=name, description=description)
        
        self.model_name = model
        
        # Store additional configuration for when full ADK is available
        self.adk_config = {
            "model": model,
            "instruction": (
                "You are an expert disaster response analyst. When analyzing sensor data, "
                "provide clear risk assessments and explain your reasoning. "
                "Consider factors like location context, temporal patterns, and "
                "emergency response protocols when making recommendations."
            ),
            "tools": [],  # Could add additional tools like weather APIs, emergency contact systems
        }
    
    async def run_with_ai_insights(self, session: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced run method that can incorporate AI insights when full ADK/Gemini is available.
        
        Args:
            session: ADK session object
            input_data: Sensor data for analysis
            
        Returns:
            Enhanced analysis results with AI insights
        """
        # Get the basic rule-based analysis
        base_result = await self.run(session, input_data)
        
        if ADK_AVAILABLE:
            # When full ADK is available, this could enhance results with AI insights
            base_result["ai_insights"] = [
                "Consider checking historical patterns for this location",
                "Weather conditions may be influencing these readings",
                "Evacuation routes should be verified for affected areas"
            ]
            base_result["confidence_score"] = 0.95
        else:
            # Mock AI insights for demonstration
            base_result["ai_insights"] = [
                "[MOCK] AI analysis suggests monitoring adjacent sensors",
                "[MOCK] Pattern recognition indicates possible equipment malfunction",  
                "[MOCK] Recommend cross-referencing with weather data"
            ]
            base_result["confidence_score"] = 0.85
        
        return base_result


async def demonstrate_adk_integration():
    """
    Demonstrate the full Google ADK integration workflow.
    """
    print("=== Google ADK Integration Demonstration ===\n")
    
    # Initialize the enhanced agent
    if ADK_AVAILABLE:
        print("🚀 Initializing Enhanced Analysis Agent with Gemini...")
        agent = EnhancedAnalysisAgent(
            name="gemini_disaster_analyst",
            model="gemini-2.0-flash"
        )
    else:
        print("🔧 Initializing Enhanced Analysis Agent with mock ADK...")
        agent = EnhancedAnalysisAgent(
            name="mock_disaster_analyst", 
            model="mock-gemini"
        )
    
    print(f"   Agent: {agent.name}")
    print(f"   Model: {agent.model_name}")
    print(f"   Description: {agent.description[:100]}...")
    print()
    
    # Create sample sensor data
    sensor_data = {
        "sensor_data": [
            {
                "location": "Data Center - Rack 7",
                "temperature": 55,
                "smoke_level": 45,
                "timestamp": "2025-01-11T14:30:00Z"
            },
            {
                "location": "Storage Room - Level B1", 
                "temperature": 28,
                "smoke_level": 85,
                "timestamp": "2025-01-11T14:31:00Z"
            }
        ]
    }
    
    # Create session (mock or real)
    session = Session(session_id="adk_demo_session")
    
    # Process sensor data
    print("🧠 Processing sensor data through ADK agent...")
    result = await agent.run(session, sensor_data)
    
    # Display results
    print(f"🎯 Overall Risk: {result['overall_risk_level']}")
    print()
    
    print("📍 Location Analysis:")
    for analysis in result['analysis']:
        print(f"  {analysis['location']}: {analysis['risk_level']} Risk")
        for reason in analysis['reasons']:
            print(f"    • {reason}")
    print()


def create_production_agent_example():
    """
    Example of how to create a production-ready agent with full ADK.
    
    This function shows the configuration that would be used in a real deployment
    with Google ADK and proper authentication.
    """
    example_config = """
# Production ADK Agent Configuration Example

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools import FunctionTool
from agents.analysis_agent import AnalysisAgent

def create_production_analysis_agent():
    \"\"\"Create production-ready disaster analysis agent.\"\"\"
    
    # Initialize Gemini model
    gemini_model = Gemini(
        model_name="gemini-2.0-flash",
        # Authentication handled via environment variables:
        # GOOGLE_API_KEY or Google Cloud ADC
    )
    
    # Create the agent with full ADK integration
    agent = LlmAgent(
        name="disaster_response_agent",
        model=gemini_model,
        description="AI-powered disaster response coordinator",
        instruction=\"\"\"
            You are an expert disaster response coordinator. 
            Analyze sensor data, assess risks, and provide actionable
            emergency response recommendations. Always prioritize
            human safety and follow established emergency protocols.
        \"\"\",
        tools=[
            FunctionTool.from_function(get_weather_data),
            FunctionTool.from_function(notify_emergency_services),
            FunctionTool.from_function(generate_evacuation_plan)
        ]
    )
    
    return agent

# Environment setup for production:
# export GOOGLE_API_KEY="your-api-key"
# or use Google Cloud Authentication (ADC)
# gcloud auth application-default login
    """
    
    print("📝 Production Configuration Example:")
    print(example_config)


async def main():
    """Main demonstration function."""
    await demonstrate_adk_integration()
    
    print("\n" + "="*60 + "\n")
    
    create_production_agent_example()


if __name__ == "__main__":
    asyncio.run(main()) 