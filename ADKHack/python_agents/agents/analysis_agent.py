"""
Analysis Agent for disaster response risk assessment.

Extracts and implements the core risk analysis logic from the JavaScript backend,
providing temperature and smoke level risk evaluation with detailed reasoning.
Wrapped as a Google ADK BaseAgent for integration into multi-agent systems.
"""

from datetime import datetime
from typing import Dict, List, Any, Union

# Try to import Google ADK components, fall back to mocks if not available
try:
    from google.adk.agents import BaseAgent
    from google.adk.events import Event
    from google.adk.sessions import Session
    ADK_AVAILABLE = True
except ImportError:
    print("⚠️  Google ADK not available, using mock classes for testing")
    from utils.mocks import MockBaseAgent as BaseAgent, MockSession as Session
    Event = dict  # Simple fallback for Event
    ADK_AVAILABLE = False


class AnalysisAgent(BaseAgent):
    """
    Agent responsible for analyzing sensor data and determining risk levels.
    
    Risk Assessment Thresholds:
    - High Risk: Temperature > 50°C OR Smoke Level > 70%
    - Medium Risk: Temperature > 35°C OR Smoke Level > 40%
    - Low Risk: All readings within normal parameters
    """
    
    def __init__(self, name: str = "disaster_analysis_agent", description: str = None):
        """
        Initialize the Analysis Agent with risk thresholds.
        
        Args:
            name: The name of the agent
            description: Description of the agent's capabilities
        """
        if description is None:
            description = (
                "AI agent specialized in disaster response risk assessment. "
                "Analyzes temperature and smoke sensor data to determine risk levels "
                "(Low, Medium, High) and provides detailed reasoning for emergency response coordination."
            )
        
        # Initialize the BaseAgent with ADK-specific parameters
        super().__init__(
            name=name,
            description=description
        )
        
        # Risk assessment thresholds
        self.high_temp_threshold = 50
        self.high_smoke_threshold = 70
        self.medium_temp_threshold = 35
        self.medium_smoke_threshold = 40
    
    async def run(self, session: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ADK-compatible run method for processing sensor data analysis requests.
        
        Args:
            session: ADK session object for maintaining state
            input_data: Dictionary containing sensor data for analysis
            
        Returns:
            Dictionary with risk analysis results
        """
        # Use the core analyze method for the actual risk assessment
        return self.analyze(input_data)
    
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sensor data and determine risk levels.
        
        Args:
            data: Dictionary containing 'sensor_data' key with sensor readings
            
        Returns:
            Dictionary with overall risk assessment and detailed analysis
        """
        sensor_data = data.get('sensor_data', [])
        
        # Handle both single readings and arrays
        if not isinstance(sensor_data, list):
            sensor_data = [sensor_data]
        
        if not sensor_data:
            raise ValueError("No sensor data provided")
        
        highest_risk = 'Low'
        analysis = []
        
        for reading in sensor_data:
            risk_assessment = self._assess_single_reading(reading)
            analysis.append(risk_assessment)
            
            # Track highest risk level across all readings
            if risk_assessment['risk_level'] == 'High':
                highest_risk = 'High'
            elif risk_assessment['risk_level'] == 'Medium' and highest_risk == 'Low':
                highest_risk = 'Medium'
        
        return {
            'overall_risk_level': highest_risk,
            'total_readings': len(sensor_data),
            'analysis': analysis,
            'timestamp': datetime.now().isoformat() + 'Z'
        }
    
    def _assess_single_reading(self, reading: Dict[str, Any]) -> Dict[str, Any]:
        """
        Assess risk level for a single sensor reading.
        
        Args:
            reading: Dictionary with temperature, smoke_level, location, timestamp
            
        Returns:
            Dictionary with detailed risk assessment for the reading
        """
        temperature = reading.get('temperature')
        smoke_level = reading.get('smoke_level')
        location = reading.get('location', 'Unknown')
        timestamp = reading.get('timestamp', datetime.now().isoformat() + 'Z')
        
        if temperature is None or smoke_level is None:
            raise ValueError("Each reading must include numeric temperature and smoke_level fields")
        
        if not isinstance(temperature, (int, float)) or not isinstance(smoke_level, (int, float)):
            raise ValueError("Temperature and smoke_level must be numeric values")
        
        risk_level = 'Low'
        reasons = []
        
        # Risk assessment logic - matches JavaScript implementation
        if temperature > self.high_temp_threshold or smoke_level > self.high_smoke_threshold:
            risk_level = 'High'
            if temperature > self.high_temp_threshold:
                reasons.append(f"Critical temperature: {temperature}°C")
            if smoke_level > self.high_smoke_threshold:
                reasons.append(f"Dangerous smoke level: {smoke_level}%")
        elif temperature > self.medium_temp_threshold or smoke_level > self.medium_smoke_threshold:
            risk_level = 'Medium'
            if temperature > self.medium_temp_threshold:
                reasons.append(f"Elevated temperature: {temperature}°C")
            if smoke_level > self.medium_smoke_threshold:
                reasons.append(f"Elevated smoke level: {smoke_level}%")
        else:
            reasons.append('All readings within normal parameters')
        
        return {
            'location': location,
            'timestamp': timestamp,
            'temperature': temperature,
            'smoke_level': smoke_level,
            'risk_level': risk_level,
            'reasons': reasons
        } 