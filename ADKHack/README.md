# Global Disaster Response Orchestrator

A real-time disaster detection and response coordination system that analyzes sensor data to assess risk levels and trigger emergency alerts.

## Features

- **Real-time Risk Analysis**: Analyzes temperature and smoke level data to determine disaster risk
- **Emergency Alerts**: Displays prominent alerts for high-risk situations
- **Multi-location Support**: Processes sensor data from multiple locations simultaneously
- **Responsive Design**: Works on desktop and mobile devices for field use
- **REST API**: Express.js backend with risk assessment logic

## Risk Assessment Logic

The system evaluates risk based on:
- **High Risk**: Temperature > 50°C OR Smoke Level > 70%
- **Medium Risk**: Temperature > 35°C OR Smoke Level > 40%
- **Low Risk**: All readings within normal parameters

## Project Structure

```
├── src/                 # React frontend
│   ├── App.tsx         # Main application component
│   ├── main.tsx        # Application entry point
│   └── index.css       # Tailwind CSS styles
├── backend/            # Express.js backend
│   ├── server.js       # API server with risk analysis
│   └── package.json    # Backend dependencies
└── README.md          # This file
```

## Installation & Setup

### Prerequisites
- Node.js 18+ installed
- npm or yarn package manager

### Installation

1. **Clone and install dependencies:**
   ```bash
   npm run install:all
   ```

2. **Start the development servers:**
   ```bash
   npm run dev
   ```

   This runs both frontend (port 5173) and backend (port 3001) concurrently.

### Individual Services

**Frontend only:**
```bash
npm run dev:frontend
```

**Backend only:**
```bash
npm run dev:backend
```

## API Endpoints

### POST /analyze
Analyzes sensor data and returns risk assessment.

**Request Body:**
```json
{
  "sensor_data": [
    {
      "location": "Building A - Floor 3",
      "temperature": 45,
      "smoke_level": 25,
      "timestamp": "2025-01-11T10:30:00Z"
    }
  ]
}
```

**Response:**
```json
{
  "overall_risk_level": "Medium",
  "total_readings": 1,
  "analysis": [
    {
      "location": "Building A - Floor 3",
      "timestamp": "2025-01-11T10:30:00Z",
      "temperature": 45,
      "smoke_level": 25,
      "risk_level": "Medium",
      "reasons": ["Elevated temperature: 45°C"]
    }
  ],
  "timestamp": "2025-01-11T10:35:00Z"
}
```

### GET /health
Health check endpoint for monitoring system status.

## Usage

1. **Input Sensor Data**: Paste JSON sensor readings or use the sample data
2. **Analyze**: Click "Analyze Risk" to process the data
3. **Review Results**: View color-coded risk levels and detailed analysis
4. **Emergency Response**: High-risk situations trigger prominent alert banners

## Sample Data Format

```json
{
  "sensor_data": [
    {
      "location": "Building A - Floor 3",
      "temperature": 45,
      "smoke_level": 25,
      "timestamp": "2025-01-11T10:30:00Z"
    },
    {
      "location": "Building B - Basement",
      "temperature": 65,
      "smoke_level": 80,
      "timestamp": "2025-01-11T10:31:00Z"
    }
  ]
}
```

## Technology Stack

- **Frontend**: React 18, TypeScript, Tailwind CSS, Vite
- **Backend**: Node.js, Express.js, CORS
- **Icons**: Lucide React
- **Development**: Concurrently, ESLint

## Production Deployment

1. **Build frontend:**
   ```bash
   npm run build
   ```

2. **Start backend:**
   ```bash
   cd backend && npm start
   ```

3. Deploy the built frontend to a static hosting service and the backend to a Node.js hosting platform.

## Contributing

This is a prototype system. For production use, consider adding:
- Database integration for historical data
- Authentication and authorization
- Real-time WebSocket connections
- Advanced sensor data validation
- Geographic mapping integration
- Multi-language support

## License

MIT License - Built for emergency response and disaster management.