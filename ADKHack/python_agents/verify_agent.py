"""
Simple verification script to test AnalysisAgent functionality.
This provides a quick way to verify the agent works correctly.
"""

from agents.analysis_agent import AnalysisAgent

def test_sample_scenarios():
    """Test the AnalysisAgent with sample scenarios."""
    agent = AnalysisAgent()
    
    print("=== AnalysisAgent Verification ===\n")
    
    # Test 1: Low Risk
    print("Test 1: Low Risk Scenario")
    low_risk_data = {
        'sensor_data': [{
            'location': 'Building A - Floor 1',
            'temperature': 25,
            'smoke_level': 15,
            'timestamp': '2025-01-11T10:30:00Z'
        }]
    }
    
    result = agent.analyze(low_risk_data)
    print(f"Overall Risk: {result['overall_risk_level']}")
    print(f"Reasons: {result['analysis'][0]['reasons']}")
    print()
    
    # Test 2: Medium Risk
    print("Test 2: Medium Risk Scenario")
    medium_risk_data = {
        'sensor_data': [{
            'location': 'Building B - Floor 2',
            'temperature': 45,
            'smoke_level': 55,
            'timestamp': '2025-01-11T10:31:00Z'
        }]
    }
    
    result = agent.analyze(medium_risk_data)
    print(f"Overall Risk: {result['overall_risk_level']}")
    print(f"Reasons: {result['analysis'][0]['reasons']}")
    print()
    
    # Test 3: High Risk
    print("Test 3: High Risk Scenario")
    high_risk_data = {
        'sensor_data': [{
            'location': 'Building C - Basement',
            'temperature': 65,
            'smoke_level': 85,
            'timestamp': '2025-01-11T10:32:00Z'
        }]
    }
    
    result = agent.analyze(high_risk_data)
    print(f"Overall Risk: {result['overall_risk_level']}")
    print(f"Reasons: {result['analysis'][0]['reasons']}")
    print()
    
    # Test 4: Multiple Readings
    print("Test 4: Multiple Readings (Mixed Risk Levels)")
    mixed_data = {
        'sensor_data': [
            {
                'location': 'Location A',
                'temperature': 30,
                'smoke_level': 20,
                'timestamp': '2025-01-11T10:30:00Z'
            },
            {
                'location': 'Location B',
                'temperature': 45,
                'smoke_level': 35,
                'timestamp': '2025-01-11T10:31:00Z'
            },
            {
                'location': 'Location C',
                'temperature': 75,
                'smoke_level': 25,
                'timestamp': '2025-01-11T10:32:00Z'
            }
        ]
    }
    
    result = agent.analyze(mixed_data)
    print(f"Overall Risk: {result['overall_risk_level']}")
    print(f"Total Readings: {result['total_readings']}")
    for i, analysis in enumerate(result['analysis']):
        print(f"  Location {i+1}: {analysis['location']} - {analysis['risk_level']} Risk")
        print(f"    Reasons: {analysis['reasons']}")
    
    print("\n=== All tests completed successfully! ===")

if __name__ == "__main__":
    test_sample_scenarios() 