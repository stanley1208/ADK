import express from 'express';
import cors from 'cors';

const app = express();
const PORT = process.env.PORT || 3001;

// Middleware
app.use(cors());
app.use(express.json({ limit: '10mb' }));

// Risk analysis logic
function analyzeRisk(sensorData) {
  if (!Array.isArray(sensorData)) {
    sensorData = [sensorData];
  }

  let highestRisk = 'Low';
  const analysis = [];

  for (const reading of sensorData) {
    const { temperature, smoke_level, location, timestamp } = reading;
    
    let riskLevel = 'Low';
    let reasons = [];

    // Risk assessment logic
    if (temperature > 50 || smoke_level > 70) {
      riskLevel = 'High';
      if (temperature > 50) reasons.push(`Critical temperature: ${temperature}°C`);
      if (smoke_level > 70) reasons.push(`Dangerous smoke level: ${smoke_level}%`);
    } else if (temperature > 35 || smoke_level > 40) {
      riskLevel = 'Medium';
      if (temperature > 35) reasons.push(`Elevated temperature: ${temperature}°C`);
      if (smoke_level > 40) reasons.push(`Elevated smoke level: ${smoke_level}%`);
    } else {
      reasons.push('All readings within normal parameters');
    }

    analysis.push({
      location: location || 'Unknown',
      timestamp: timestamp || new Date().toISOString(),
      temperature,
      smoke_level,
      risk_level: riskLevel,
      reasons
    });

    // Track highest risk level
    if (riskLevel === 'High' || (riskLevel === 'Medium' && highestRisk === 'Low')) {
      highestRisk = riskLevel;
    }
  }

  return {
    overall_risk_level: highestRisk,
    total_readings: sensorData.length,
    analysis,
    timestamp: new Date().toISOString()
  };
}

// Routes
app.get('/health', (req, res) => {
  res.json({ status: 'OK', service: 'Disaster Response Backend' });
});

app.post('/analyze', (req, res) => {
  try {
    const { sensor_data } = req.body;

    if (!sensor_data) {
      return res.status(400).json({
        error: 'No sensor data provided',
        message: 'Please provide sensor_data in the request body'
      });
    }

    // Validate sensor data structure
    const dataArray = Array.isArray(sensor_data) ? sensor_data : [sensor_data];
    
    for (const reading of dataArray) {
      if (typeof reading.temperature !== 'number' || typeof reading.smoke_level !== 'number') {
        return res.status(400).json({
          error: 'Invalid sensor data format',
          message: 'Each reading must include numeric temperature and smoke_level fields'
        });
      }
    }

    const result = analyzeRisk(sensor_data);
    res.json(result);

  } catch (error) {
    console.error('Analysis error:', error);
    res.status(500).json({
      error: 'Analysis failed',
      message: 'Internal server error during risk analysis'
    });
  }
});

app.listen(PORT, () => {
  console.log(`🚨 Disaster Response Backend running on port ${PORT}`);
  console.log(`📡 Health check: http://localhost:${PORT}/health`);
  console.log(`🔍 Analysis endpoint: http://localhost:${PORT}/analyze`);
});