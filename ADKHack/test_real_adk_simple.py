import os
import asyncio
from datetime import datetime

# Set the Google API key in code (for testing)
os.environ['GOOGLE_API_KEY'] = 'your-actual-api-key-here'

try:
    from google.adk.agents import BaseAgent
    from google.adk.sessions import Session
    print("✅ Google ADK is available!")
    ADK_AVAILABLE = True
except ImportError as e:
    print(f"❌ Google ADK not available: {e}")
    ADK_AVAILABLE = False

class RealDetectionAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="sensor_detection_agent", description="Detects sensor data")
    
    async def run(self, session, input_data):
        print(f"🔍 DetectionAgent processing with session: {session.id}")
        
        # Simulate sensor data detection
        sensor_data = [
            {
                "location": "Real ADK Demo - Server Room",
                "temperature": 78,
                "smoke_level": 90,
                "timestamp": datetime.now().isoformat() + 'Z'
            },
            {
                "location": "Real ADK Demo - Office Area", 
                "temperature": 22,
                "smoke_level": 5,
                "timestamp": datetime.now().isoformat() + 'Z'
            }
        ]
        
        return {
            "status": "data_detected",
            "sensor_data": sensor_data,
            "total_readings": len(sensor_data),
            "timestamp": datetime.now().isoformat() + 'Z'
        }

class RealAnalysisAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="disaster_analysis_agent", description="Analyzes disaster risk")
    
    async def run(self, session, input_data):
        print(f"🔍 AnalysisAgent processing with session: {session.id}")
        
        sensor_data = input_data.get('sensor_data', [])
        analysis_results = []
        overall_risk = "Low"
        
        for reading in sensor_data:
            temp = reading.get('temperature', 0)
            smoke = reading.get('smoke_level', 0)
            
            # Risk assessment logic
            if temp > 50 or smoke > 70:
                risk_level = "High"
                overall_risk = "High"
                reasons = [f"Critical temp: {temp}°C" if temp > 50 else "", 
                          f"Dangerous smoke: {smoke}%" if smoke > 70 else ""]
                reasons = [r for r in reasons if r]
            elif temp > 35 or smoke > 40:
                risk_level = "Medium"
                if overall_risk != "High":
                    overall_risk = "Medium"
                reasons = [f"Elevated temp: {temp}°C" if temp > 35 else "",
                          f"Elevated smoke: {smoke}%" if smoke > 40 else ""]
                reasons = [r for r in reasons if r]
            else:
                risk_level = "Low"
                reasons = ["Normal parameters"]
            
            analysis_results.append({
                "location": reading['location'],
                "risk_level": risk_level,
                "temperature": temp,
                "smoke_level": smoke,
                "reasons": reasons
            })
        
        return {
            "overall_risk_level": overall_risk,
            "total_readings": len(sensor_data),
            "analysis": analysis_results,
            "timestamp": datetime.now().isoformat() + 'Z'
        }

class RealAlertAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="disaster_alert_agent", description="Generates emergency alerts")
    
    async def run(self, session, input_data):
        print(f"🚨 AlertAgent processing with session: {session.id}")
        
        risk_level = input_data.get('overall_risk_level', 'Low')
        analysis = input_data.get('analysis', [])
        
        alerts = []
        if risk_level == "High":
            alerts.append({
                "severity": "CRITICAL",
                "message": "EMERGENCY: High risk detected - immediate evacuation required!",
                "timestamp": datetime.now().isoformat() + 'Z'
            })
            
            for location_data in analysis:
                if location_data.get('risk_level') == 'High':
                    alerts.append({
                        "severity": "CRITICAL",
                        "message": f"EVACUATE: {location_data['location']} - {', '.join(location_data.get('reasons', []))}",
                        "location": location_data['location'],
                        "timestamp": datetime.now().isoformat() + 'Z'
                    })
        elif risk_level == "Medium":
            alerts.append({
                "severity": "WARNING",
                "message": "WARNING: Medium risk detected - monitor closely",
                "timestamp": datetime.now().isoformat() + 'Z'
            })
        
        return {
            "alert_status": "alerts_generated" if alerts else "no_alerts_needed",
            "total_alerts": len(alerts),
            "alerts_triggered": alerts,
            "risk_level": risk_level,
            "timestamp": datetime.now().isoformat() + 'Z'
        }

async def test_disaster_pipeline():
    """Test the complete disaster response pipeline manually."""
    if not ADK_AVAILABLE:
        print("❌ Cannot test - ADK not available")
        return
    
    # Create session
    session = Session(
        id="disaster_manual_" + datetime.now().strftime("%Y%m%d_%H%M%S"),
        app_name="DisasterResponseSystem",
        user_id="hackathon_demo"
    )
    
    # Create agents
    detection_agent = RealDetectionAgent()
    analysis_agent = RealAnalysisAgent()
    alert_agent = RealAlertAgent()
    
    print("🚀 Starting REAL Google ADK Multi-Agent Pipeline (Manual Execution)...")
    print(f"Session: {session.id}")
    print("=" * 60)
    
    # Step 1: Detection
    print("\n🤖 Step 1: Detection Agent")
    detection_result = await detection_agent.run(session, {})
    print(f"  📊 Detected {detection_result.get('total_readings', 0)} sensor readings")
    
    # Step 2: Analysis (using detection results)
    print("\n🤖 Step 2: Analysis Agent") 
    analysis_result = await analysis_agent.run(session, detection_result)
    print(f"  ⚠️  Overall Risk: {analysis_result['overall_risk_level']}")
    for analysis in analysis_result.get('analysis', []):
        print(f"     • {analysis['location']}: {analysis['risk_level']} Risk")
        if analysis['risk_level'] != 'Low':
            print(f"       Reasons: {', '.join(analysis['reasons'])}")
    
    # Step 3: Alert (using analysis results)
    print("\n🤖 Step 3: Alert Agent")
    alert_result = await alert_agent.run(session, analysis_result)
    alerts = alert_result.get('alerts_triggered', [])
    print(f"  🚨 Generated {len(alerts)} alerts")
    for alert in alerts:
        print(f"     • {alert['severity']}: {alert['message']}")
    
    print("\n" + "=" * 60)
    print("✅ REAL Google ADK Multi-Agent Pipeline Complete!")
    print(f"Final Status: {analysis_result['overall_risk_level']} Risk - {alert_result['alert_status']}")
    
    return {
        "session_id": session.id,
        "detection": detection_result,
        "analysis": analysis_result,
        "alerts": alert_result
    }

if __name__ == "__main__":
    print("🧪 Testing REAL Google ADK Disaster Response Pipeline...")
    result = asyncio.run(test_disaster_pipeline())
    
    if result:
        print(f"\n🎉 Pipeline completed successfully!")
        print(f"Session ID: {result['session_id']}")
        print(f"Total sensor readings: {result['detection']['total_readings']}")
        print(f"Risk level: {result['analysis']['overall_risk_level']}")
        print(f"Alerts generated: {result['alerts']['total_alerts']}") 