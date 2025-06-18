"""
Comprehensive tests for AnalysisAgent class.

Tests cover all risk levels (Low, Medium, High), edge cases, multiple readings,
and error handling scenarios to ensure accurate risk assessment.
"""

import pytest
from datetime import datetime
from agents.analysis_agent import AnalysisAgent


class TestAnalysisAgent:
    """Test suite for AnalysisAgent class."""
    
    def setup_method(self):
        """Set up test fixture with fresh AnalysisAgent instance."""
        self.agent = AnalysisAgent()
    
    # Low Risk Tests
    def test_low_risk_normal_conditions(self):
        """Test low risk with normal temperature and smoke levels."""
        data = {
            'sensor_data': [{
                'location': 'Test Location',
                'temperature': 25,
                'smoke_level': 15,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'Low'
        assert result['total_readings'] == 1
        assert len(result['analysis']) == 1
        
        analysis = result['analysis'][0]
        assert analysis['risk_level'] == 'Low'
        assert analysis['temperature'] == 25
        assert analysis['smoke_level'] == 15
        assert analysis['location'] == 'Test Location'
        assert 'All readings within normal parameters' in analysis['reasons']
    
    def test_low_risk_boundary_values(self):
        """Test low risk at boundary values (35°C temperature, 40% smoke)."""
        data = {
            'sensor_data': [{
                'location': 'Boundary Test',
                'temperature': 35,
                'smoke_level': 40,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'Low'
        assert result['analysis'][0]['risk_level'] == 'Low'
        assert 'All readings within normal parameters' in result['analysis'][0]['reasons']
    
    # Medium Risk Tests
    def test_medium_risk_elevated_temperature(self):
        """Test medium risk due to elevated temperature (>35°C, ≤50°C)."""
        data = {
            'sensor_data': [{
                'location': 'Medium Temp Test',
                'temperature': 45,
                'smoke_level': 25,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'Medium'
        assert result['analysis'][0]['risk_level'] == 'Medium'
        assert 'Elevated temperature: 45°C' in result['analysis'][0]['reasons']
        assert len(result['analysis'][0]['reasons']) == 1
    
    def test_medium_risk_elevated_smoke(self):
        """Test medium risk due to elevated smoke level (>40%, ≤70%)."""
        data = {
            'sensor_data': [{
                'location': 'Medium Smoke Test',
                'temperature': 30,
                'smoke_level': 55,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'Medium'
        assert result['analysis'][0]['risk_level'] == 'Medium'
        assert 'Elevated smoke level: 55%' in result['analysis'][0]['reasons']
        assert len(result['analysis'][0]['reasons']) == 1
    
    def test_medium_risk_both_elevated(self):
        """Test medium risk with both temperature and smoke elevated."""
        data = {
            'sensor_data': [{
                'location': 'Both Elevated Test',
                'temperature': 40,
                'smoke_level': 50,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'Medium'
        assert result['analysis'][0]['risk_level'] == 'Medium'
        assert 'Elevated temperature: 40°C' in result['analysis'][0]['reasons']
        assert 'Elevated smoke level: 50%' in result['analysis'][0]['reasons']
        assert len(result['analysis'][0]['reasons']) == 2
    
    def test_medium_risk_boundary_values(self):
        """Test medium risk at boundary values (36°C temperature, 41% smoke)."""
        data = {
            'sensor_data': [{
                'location': 'Medium Boundary Test',
                'temperature': 36,
                'smoke_level': 41,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'Medium'
        assert result['analysis'][0]['risk_level'] == 'Medium'
        assert 'Elevated temperature: 36°C' in result['analysis'][0]['reasons']
        assert 'Elevated smoke level: 41%' in result['analysis'][0]['reasons']
    
    # High Risk Tests
    def test_high_risk_critical_temperature(self):
        """Test high risk due to critical temperature (>50°C)."""
        data = {
            'sensor_data': [{
                'location': 'High Temp Test',
                'temperature': 65,
                'smoke_level': 30,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'High'
        assert result['analysis'][0]['risk_level'] == 'High'
        assert 'Critical temperature: 65°C' in result['analysis'][0]['reasons']
        assert len(result['analysis'][0]['reasons']) == 1
    
    def test_high_risk_dangerous_smoke(self):
        """Test high risk due to dangerous smoke level (>70%)."""
        data = {
            'sensor_data': [{
                'location': 'High Smoke Test',
                'temperature': 35,
                'smoke_level': 85,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'High'
        assert result['analysis'][0]['risk_level'] == 'High'
        assert 'Dangerous smoke level: 85%' in result['analysis'][0]['reasons']
        assert len(result['analysis'][0]['reasons']) == 1
    
    def test_high_risk_both_critical(self):
        """Test high risk with both temperature and smoke at critical levels."""
        data = {
            'sensor_data': [{
                'location': 'Both Critical Test',
                'temperature': 75,
                'smoke_level': 90,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'High'
        assert result['analysis'][0]['risk_level'] == 'High'
        assert 'Critical temperature: 75°C' in result['analysis'][0]['reasons']
        assert 'Dangerous smoke level: 90%' in result['analysis'][0]['reasons']
        assert len(result['analysis'][0]['reasons']) == 2
    
    def test_high_risk_boundary_values(self):
        """Test high risk at boundary values (51°C temperature, 71% smoke)."""
        data = {
            'sensor_data': [{
                'location': 'High Boundary Test',
                'temperature': 51,
                'smoke_level': 71,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'High'
        assert result['analysis'][0]['risk_level'] == 'High'
        assert 'Critical temperature: 51°C' in result['analysis'][0]['reasons']
        assert 'Dangerous smoke level: 71%' in result['analysis'][0]['reasons']
    
    # Multiple Readings Tests
    def test_multiple_readings_mixed_risk_levels(self):
        """Test multiple readings with different risk levels."""
        data = {
            'sensor_data': [
                {
                    'location': 'Location A',
                    'temperature': 25,
                    'smoke_level': 15,
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
                    'temperature': 65,
                    'smoke_level': 25,
                    'timestamp': '2025-01-11T10:32:00Z'
                }
            ]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'High'  # Highest risk wins
        assert result['total_readings'] == 3
        assert len(result['analysis']) == 3
        
        # Check individual risk levels
        assert result['analysis'][0]['risk_level'] == 'Low'
        assert result['analysis'][1]['risk_level'] == 'Medium'
        assert result['analysis'][2]['risk_level'] == 'High'
    
    def test_multiple_readings_all_medium_risk(self):
        """Test multiple readings all at medium risk level."""
        data = {
            'sensor_data': [
                {
                    'location': 'Location A',
                    'temperature': 40,
                    'smoke_level': 30,
                    'timestamp': '2025-01-11T10:30:00Z'
                },
                {
                    'location': 'Location B',
                    'temperature': 30,
                    'smoke_level': 50,
                    'timestamp': '2025-01-11T10:31:00Z'
                }
            ]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'Medium'
        assert result['total_readings'] == 2
        assert result['analysis'][0]['risk_level'] == 'Medium'
        assert result['analysis'][1]['risk_level'] == 'Medium'
    
    # Edge Cases and Error Handling
    def test_single_reading_not_in_array(self):
        """Test handling of single reading not wrapped in array."""
        data = {
            'sensor_data': {
                'location': 'Single Reading',
                'temperature': 45,
                'smoke_level': 25,
                'timestamp': '2025-01-11T10:30:00Z'
            }
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'Medium'
        assert result['total_readings'] == 1
        assert result['analysis'][0]['risk_level'] == 'Medium'
    
    def test_missing_optional_fields(self):
        """Test handling of missing optional fields (location, timestamp)."""
        data = {
            'sensor_data': [{
                'temperature': 35,
                'smoke_level': 25
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'Low'
        assert result['analysis'][0]['location'] == 'Unknown'
        assert result['analysis'][0]['timestamp'] is not None
    
    def test_missing_sensor_data(self):
        """Test error handling for missing sensor_data."""
        data = {}
        
        with pytest.raises(ValueError, match="No sensor data provided"):
            self.agent.analyze(data)
    
    def test_empty_sensor_data(self):
        """Test error handling for empty sensor_data array."""
        data = {'sensor_data': []}
        
        with pytest.raises(ValueError, match="No sensor data provided"):
            self.agent.analyze(data)
    
    def test_missing_temperature(self):
        """Test error handling for missing temperature field."""
        data = {
            'sensor_data': [{
                'location': 'Test Location',
                'smoke_level': 25,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        with pytest.raises(ValueError, match="Each reading must include numeric temperature and smoke_level fields"):
            self.agent.analyze(data)
    
    def test_missing_smoke_level(self):
        """Test error handling for missing smoke_level field."""
        data = {
            'sensor_data': [{
                'location': 'Test Location',
                'temperature': 35,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        with pytest.raises(ValueError, match="Each reading must include numeric temperature and smoke_level fields"):
            self.agent.analyze(data)
    
    def test_non_numeric_temperature(self):
        """Test error handling for non-numeric temperature."""
        data = {
            'sensor_data': [{
                'location': 'Test Location',
                'temperature': 'hot',
                'smoke_level': 25,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        with pytest.raises(ValueError, match="Temperature and smoke_level must be numeric values"):
            self.agent.analyze(data)
    
    def test_non_numeric_smoke_level(self):
        """Test error handling for non-numeric smoke_level."""
        data = {
            'sensor_data': [{
                'location': 'Test Location',
                'temperature': 35,
                'smoke_level': 'smoky',
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        with pytest.raises(ValueError, match="Temperature and smoke_level must be numeric values"):
            self.agent.analyze(data)
    
    def test_float_values(self):
        """Test handling of float values for temperature and smoke_level."""
        data = {
            'sensor_data': [{
                'location': 'Float Test',
                'temperature': 45.5,
                'smoke_level': 35.7,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        assert result['overall_risk_level'] == 'Medium'
        assert result['analysis'][0]['temperature'] == 45.5
        assert result['analysis'][0]['smoke_level'] == 35.7
        assert 'Elevated temperature: 45.5°C' in result['analysis'][0]['reasons']
    
    def test_result_structure(self):
        """Test that result structure matches expected format."""
        data = {
            'sensor_data': [{
                'location': 'Structure Test',
                'temperature': 45,
                'smoke_level': 55,
                'timestamp': '2025-01-11T10:30:00Z'
            }]
        }
        
        result = self.agent.analyze(data)
        
        # Check top-level structure
        assert 'overall_risk_level' in result
        assert 'total_readings' in result
        assert 'analysis' in result
        assert 'timestamp' in result
        
        # Check analysis item structure
        analysis_item = result['analysis'][0]
        assert 'location' in analysis_item
        assert 'timestamp' in analysis_item
        assert 'temperature' in analysis_item
        assert 'smoke_level' in analysis_item
        assert 'risk_level' in analysis_item
        assert 'reasons' in analysis_item
        
        # Check data types
        assert isinstance(result['overall_risk_level'], str)
        assert isinstance(result['total_readings'], int)
        assert isinstance(result['analysis'], list)
        assert isinstance(result['timestamp'], str)
        assert isinstance(analysis_item['reasons'], list) 