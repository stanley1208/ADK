"""
Mock classes for Google ADK components.

These mocks allow the disaster response system to run and be tested even
without full Google ADK installation or when ADK imports fail.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime


class MockSession:
    """Mock session class for testing without full ADK setup."""
    
    def __init__(self, session_id: str = None):
        self.session_id = session_id or f"mock_session_{datetime.now().isoformat()}"
        self.created_at = datetime.now()
        self.data = {}
    
    def get(self, key: str, default=None):
        """Get data from session."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set data in session."""
        self.data[key] = value
    
    def __repr__(self):
        return f"MockSession(session_id='{self.session_id}')"


class MockBaseAgent:
    """Mock base agent class for testing without full ADK setup."""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.created_at = datetime.now()
    
    async def run(self, session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock run method - should be overridden by subclasses."""
        return {"status": "mock_response", "agent": self.name}
    
    def __repr__(self):
        return f"MockBaseAgent(name='{self.name}')"


class MockSequentialAgent:
    """Mock sequential agent class for testing without full ADK setup."""
    
    def __init__(self, name: str, sub_agents: List[MockBaseAgent], description: str = ""):
        self.name = name
        self.sub_agents = sub_agents or []
        self.description = description
        self.created_at = datetime.now()
    
    async def run(self, session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock sequential agent run method that processes through sub-agents in order.
        
        Args:
            session: Mock session object
            input_data: Input data for the first agent
            
        Returns:
            Dictionary containing results from all sub-agents
        """
        results = []
        current_data = input_data
        
        for i, agent in enumerate(self.sub_agents):
            try:
                result = await agent.run(session, current_data)
                results.append({
                    "agent_name": agent.name,
                    "agent_description": agent.description,
                    "step": i + 1,
                    "result": result
                })
                
                # Pass the result of this agent as input to the next agent
                # For detection -> analysis pipeline, the detected data becomes the analysis input
                if hasattr(result, 'get') and result.get('sensor_data'):
                    current_data = {"sensor_data": result['sensor_data']}
                else:
                    current_data = result
                    
            except Exception as e:
                results.append({
                    "agent_name": agent.name,
                    "step": i + 1,
                    "error": str(e),
                    "status": "failed"
                })
                break
        
        return {
            "workflow_name": self.name,
            "workflow_description": self.description,
            "total_steps": len(self.sub_agents),
            "completed_steps": len(results),
            "results": results,
            "final_result": results[-1]["result"] if results and "result" in results[-1] else None,
            "status": "completed" if len(results) == len(self.sub_agents) else "failed",
            "timestamp": datetime.now().isoformat() + 'Z'
        }
    
    def __repr__(self):
        return f"MockSequentialAgent(name='{self.name}', sub_agents={len(self.sub_agents)})" 