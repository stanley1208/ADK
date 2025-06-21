"""
Alert Agent for disaster response notification system.

This agent is responsible for processing risk analysis results and triggering
appropriate alerts based on the severity level. It handles high-priority
emergency notifications and maintains alert logs.
"""

from datetime import datetime
from typing import Dict, List, Any, Optional

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


class AlertAgent(BaseAgent):
    """
    Agent responsible for processing risk analysis results and triggering alerts.
    
    This agent receives risk assessment data and determines appropriate alert actions
    based on severity levels. High-risk situations trigger immediate alerts while
    lower risk levels receive standard notifications.
    """
    
    def __init__(self, name: str = "disaster_alert_agent", description: str = None):
        """
        Initialize the Alert Agent.
        
        Args:
            name: The name of the agent
            description: Description of the agent's capabilities
        """
        if description is None:
            description = (
                "AI agent specialized in disaster response alert notifications. "
                "Processes risk assessment results and triggers appropriate alerts "
                "based on severity levels for emergency response coordination."
            )
        
        # Initialize the BaseAgent with ADK-specific parameters
        super().__init__(
            name=name,
            description=description
        )
        
        # Alert configuration
        self.alert_thresholds = {
            "High": "CRITICAL",
            "Medium": "WARNING", 
            "Low": "INFO"
        }
        
        # Alert history for tracking
        self.alert_history = []
    
    async def run(self, session: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ADK-compatible run method for processing alert requests.
        
        Args:
            session: ADK session object for maintaining state
            input_data: Dictionary containing risk analysis results
            
        Returns:
            Dictionary containing alert processing results
        """
        return self.process_alerts(input_data)
    
    def process_alerts(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process risk analysis data and trigger appropriate alerts.
        
        Args:
            input_data: Dictionary containing risk analysis results with:
                - overall_risk_level: Overall risk assessment
                - analysis: List of location-specific analyses
                - timestamp: Analysis timestamp
                
        Returns:
            Dictionary containing alert processing results
        """
        # Extract risk information from input
        overall_risk = input_data.get('overall_risk_level', 'Unknown')
        analysis_data = input_data.get('analysis', [])
        timestamp = input_data.get('timestamp', datetime.now().isoformat() + 'Z')
        
        # Process alerts for overall risk and individual locations
        alerts_triggered = []
        alert_summary = {
            "total_alerts": 0,
            "critical_alerts": 0,
            "warning_alerts": 0,
            "info_alerts": 0
        }
        
        # Process overall risk alert
        overall_alert = self._generate_alert(overall_risk, "Overall Assessment", timestamp)
        if overall_alert:
            alerts_triggered.append(overall_alert)
            self._update_alert_summary(alert_summary, overall_alert['severity'])
        
        # Process location-specific alerts
        for location_analysis in analysis_data:
            location = location_analysis.get('location', 'Unknown Location')
            risk_level = location_analysis.get('risk_level', 'Unknown')
            
            location_alert = self._generate_alert(risk_level, location, timestamp)
            if location_alert:
                alerts_triggered.append(location_alert)
                self._update_alert_summary(alert_summary, location_alert['severity'])
        
        # Store alerts in history
        self.alert_history.extend(alerts_triggered)
        
        # Prepare response
        response = {
            "alert_status": "processed",
            "alerts_triggered": alerts_triggered,
            "alert_summary": alert_summary,
            "timestamp": datetime.now().isoformat() + 'Z',
            "input_risk_level": overall_risk,
            "total_locations_processed": len(analysis_data)
        }
        
        # Add the original analysis data for downstream processing
        response.update(input_data)
        
        return response
    
    def _generate_alert(self, risk_level: str, location: str, timestamp: str) -> Optional[Dict[str, Any]]:
        """
        Generate an alert based on risk level and location.
        
        Args:
            risk_level: Risk level (High, Medium, Low)
            location: Location identifier
            timestamp: Alert timestamp
            
        Returns:
            Alert dictionary or None if no alert needed
        """
        if risk_level == "High":
            alert_message = f"🚨 ALERT: High risk detected at {location}"
            severity = "CRITICAL"
            action_required = True
            
            # Print the alert immediately for high-risk situations
            print(alert_message)
            
        elif risk_level == "Medium":
            alert_message = f"⚠️  WARNING: Medium risk detected at {location}"
            severity = "WARNING"
            action_required = True
            
        elif risk_level == "Low":
            alert_message = f"ℹ️  INFO: Low risk monitoring at {location}"
            severity = "INFO"
            action_required = False
            
        else:
            # Unknown risk level - log but don't alert
            return None
        
        alert_data = {
            "alert_id": f"alert_{len(self.alert_history) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "message": alert_message,
            "severity": severity,
            "risk_level": risk_level,
            "location": location,
            "timestamp": timestamp,
            "action_required": action_required,
            "alert_generated_at": datetime.now().isoformat() + 'Z'
        }
        
        return alert_data
    
    def _update_alert_summary(self, summary: Dict[str, int], severity: str):
        """
        Update alert summary counters.
        
        Args:
            summary: Alert summary dictionary to update
            severity: Alert severity level
        """
        summary["total_alerts"] += 1
        
        if severity == "CRITICAL":
            summary["critical_alerts"] += 1
        elif severity == "WARNING":
            summary["warning_alerts"] += 1
        elif severity == "INFO":
            summary["info_alerts"] += 1
    
    def get_alert_history(self) -> List[Dict[str, Any]]:
        """
        Get the complete alert history.
        
        Returns:
            List of all alerts that have been triggered
        """
        return self.alert_history.copy()
    
    def clear_alert_history(self):
        """Clear the alert history."""
        self.alert_history.clear()
    
    def get_recent_alerts(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most recent alerts.
        
        Args:
            count: Number of recent alerts to return
            
        Returns:
            List of recent alerts
        """
        return self.alert_history[-count:] if self.alert_history else [] 