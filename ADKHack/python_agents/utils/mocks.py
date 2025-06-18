"""
Mock classes for Google ADK components.

These mocks allow the disaster response system to run and be tested even
without full Google ADK installation or when ADK imports fail.
"""

from typing import Dict, Any, Optional
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