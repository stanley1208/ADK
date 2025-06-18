import React, { useState } from 'react';
import { Upload, AlertTriangle, CheckCircle, AlertCircle, Activity, MapPin, Clock } from 'lucide-react';

interface SensorReading {
  location: string;
  temperature: number;
  smoke_level: number;
  timestamp: string;
}

interface AnalysisResult {
  overall_risk_level: 'Low' | 'Medium' | 'High';
  total_readings: number;
  analysis: Array<{
    location: string;
    timestamp: string;
    temperature: number;
    smoke_level: number;
    risk_level: 'Low' | 'Medium' | 'High';
    reasons: string[];
  }>;
  timestamp: string;
}

function App() {
  const [inputData, setInputData] = useState('');
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const sampleData = JSON.stringify({
    sensor_data: [
      {
        location: "Building A - Floor 3",
        temperature: 45,
        smoke_level: 25,
        timestamp: "2025-01-11T10:30:00Z"
      },
      {
        location: "Building B - Basement",
        temperature: 65,
        smoke_level: 80,
        timestamp: "2025-01-11T10:31:00Z"
      }
    ]
  }, null, 2);

  const handleAnalyze = async () => {
    setLoading(true);
    setError('');
    setAnalysisResult(null);

    try {
      const parsedData = JSON.parse(inputData);
      
      const response = await fetch('http://localhost:3001/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(parsedData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Analysis failed');
      }

      const result = await response.json();
      setAnalysisResult(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze data');
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'High': return 'text-red-600 bg-red-50 border-red-200';
      case 'Medium': return 'text-orange-600 bg-orange-50 border-orange-200';
      case 'Low': return 'text-green-600 bg-green-50 border-green-200';
      default: return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getRiskIcon = (risk: string) => {
    switch (risk) {
      case 'High': return <AlertTriangle className="w-5 h-5" />;
      case 'Medium': return <AlertCircle className="w-5 h-5" />;
      case 'Low': return <CheckCircle className="w-5 h-5" />;
      default: return <Activity className="w-5 h-5" />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="p-3 bg-red-100 rounded-full">
              <AlertTriangle className="w-8 h-8 text-red-600" />
            </div>
            <h1 className="text-4xl font-bold text-gray-900">
              Global Disaster Response Orchestrator
            </h1>
          </div>
          <p className="text-gray-600 text-lg">
            Real-time sensor data analysis for emergency response coordination
          </p>
        </div>

        {/* High Risk Alert Banner */}
        {analysisResult?.overall_risk_level === 'High' && (
          <div className="mb-6 p-4 bg-red-600 text-white rounded-lg shadow-lg animate-pulse">
            <div className="flex items-center gap-3">
              <AlertTriangle className="w-6 h-6" />
              <div>
                <h3 className="font-bold text-lg">🚨 HIGH DISASTER RISK DETECTED</h3>
                <p className="opacity-90">Immediate response coordination required. Deploy emergency protocols.</p>
              </div>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-center gap-2 mb-4">
              <Upload className="w-5 h-5 text-blue-600" />
              <h2 className="text-xl font-semibold text-gray-900">Sensor Data Input</h2>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  JSON Sensor Readings
                </label>
                <textarea
                  value={inputData}
                  onChange={(e) => setInputData(e.target.value)}
                  placeholder="Paste or type JSON sensor data here..."
                  className="w-full h-64 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
                />
              </div>

              <div className="flex gap-2">
                <button
                  onClick={handleAnalyze}
                  disabled={!inputData.trim() || loading}
                  className="flex-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 font-medium"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Activity className="w-4 h-4" />
                      Analyze Risk
                    </>
                  )}
                </button>
                <button
                  onClick={() => setInputData(sampleData)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
                >
                  Load Sample
                </button>
              </div>
            </div>

            {error && (
              <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                <p className="text-red-600 text-sm">{error}</p>
              </div>
            )}
          </div>

          {/* Results Section */}
          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-green-600" />
              Risk Analysis Results
            </h2>

            {!analysisResult ? (
              <div className="text-center py-12 text-gray-500">
                <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>No analysis data available</p>
                <p className="text-sm">Submit sensor data to see risk assessment</p>
              </div>
            ) : (
              <div className="space-y-4">
                {/* Overall Risk */}
                <div className={`p-4 rounded-lg border-2 ${getRiskColor(analysisResult.overall_risk_level)}`}>
                  <div className="flex items-center gap-3">
                    {getRiskIcon(analysisResult.overall_risk_level)}
                    <div>
                      <h3 className="font-bold text-lg">
                        Overall Risk: {analysisResult.overall_risk_level}
                      </h3>
                      <p className="text-sm opacity-75">
                        {analysisResult.total_readings} sensor reading{analysisResult.total_readings !== 1 ? 's' : ''} analyzed
                      </p>
                    </div>
                  </div>
                </div>

                {/* Individual Readings */}
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900">Detailed Analysis</h4>
                  {analysisResult.analysis.map((reading, idx) => (
                    <div key={idx} className="border border-gray-200 rounded-lg p-4">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex items-center gap-2">
                          <MapPin className="w-4 h-4 text-gray-500" />
                          <span className="font-medium text-gray-900">{reading.location}</span>
                        </div>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getRiskColor(reading.risk_level).replace('border-', 'border ')}`}>
                          {reading.risk_level}
                        </span>
                      </div>
                      
                      <div className="grid grid-cols-2 gap-4 mb-2 text-sm">
                        <div>
                          <span className="text-gray-500">Temperature:</span>
                          <span className="ml-1 font-medium">{reading.temperature}°C</span>
                        </div>
                        <div>
                          <span className="text-gray-500">Smoke Level:</span>
                          <span className="ml-1 font-medium">{reading.smoke_level}%</span>
                        </div>
                      </div>

                      <div className="flex items-center gap-1 text-xs text-gray-500 mb-2">
                        <Clock className="w-3 h-3" />
                        {new Date(reading.timestamp).toLocaleString()}
                      </div>

                      <div className="text-sm">
                        <span className="text-gray-500">Assessment:</span>
                        <ul className="mt-1 space-y-1">
                          {reading.reasons.map((reason, reasonIdx) => (
                            <li key={reasonIdx} className="text-gray-700 text-xs">• {reason}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-gray-500 text-sm">
          <p>Emergency Response System v1.0 • Real-time Disaster Detection</p>
        </div>
      </div>
    </div>
  );
}

export default App;