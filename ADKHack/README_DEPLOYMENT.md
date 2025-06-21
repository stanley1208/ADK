# Disaster Response System - Containerization & Deployment

## Overview

Step 7 provides complete containerization and deployment capabilities for the disaster response system, enabling deployment to Google Cloud Run and Agent Engine with enterprise-grade scalability and reliability.

## ✅ Step 7 Complete: Containerization & Deployment

### 🎯 What Was Implemented

#### 1. **Docker Containerization** (`Dockerfile`)
- ✅ **Optimized multi-stage container** with Python 3.10-slim base
- ✅ **Security hardening** with non-root user and minimal attack surface
- ✅ **Layer optimization** for faster builds and deployments
- ✅ **Health checks** for container monitoring
- ✅ **Environment configuration** for cloud deployment

#### 2. **FastAPI Web Server** (`main.py`)
- ✅ **Google ADK integration** with fallback support
- ✅ **RESTful API endpoints** for all agent operations
- ✅ **Comprehensive error handling** and status reporting
- ✅ **CORS support** for web interface integration
- ✅ **Production-ready configuration** with uvicorn

#### 3. **Cloud Run Deployment** (`cloud-run.yaml`)
- ✅ **Optimized Cloud Run configuration** for performance and cost
- ✅ **Auto-scaling** from 0 to 100 instances
- ✅ **Health monitoring** with startup, liveness, and readiness probes
- ✅ **Resource allocation** tuned for agent workloads
- ✅ **Service account integration** for BigQuery access

#### 4. **Automated Deployment** (`deploy.sh`)
- ✅ **One-command deployment** to Google Cloud Run
- ✅ **Prerequisite checking** and API enablement
- ✅ **Service account creation** for BigQuery integration
- ✅ **Error handling** and progress tracking
- ✅ **Post-deployment verification** and URL display

## 🚀 Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r python_agents/requirements.txt

# Run locally
python main.py

# Test endpoints
curl http://localhost:8080/health
curl http://localhost:8080/status
```

### Docker Local Testing
```bash
# Build container
docker build -t disaster-response-system .

# Run container
docker run -p 8080:8080 disaster-response-system

# Test health check
curl http://localhost:8080/health
```

### Cloud Run Deployment
```bash
# Set your project
export GOOGLE_CLOUD_PROJECT="your-project-id"

# Deploy with BigQuery service account
CREATE_SERVICE_ACCOUNT=true ./deploy.sh

# Or basic deployment
./deploy.sh
```

## 📊 API Endpoints

### Core Endpoints

#### `GET /` - System Information
```json
{
  "message": "Disaster Response System API",
  "version": "1.0.0",
  "status": "operational",
  "agents": ["DetectionAgent", "AnalysisAgent", "AlertAgent"],
  "adk_available": false,
  "timestamp": "2025-01-11T15:30:00Z"
}
```

#### `GET /health` - Health Check
```json
{
  "status": "healthy",
  "timestamp": "2025-01-11T15:30:00Z",
  "agents": {
    "detection": "sensor_detection_agent",
    "analysis": "disaster_analysis_agent",
    "alerts": "disaster_alert_agent"
  },
  "adk_available": false
}
```

#### `GET /status` - System Status
```json
{
  "system": "operational",
  "agents": {
    "detection": "ready",
    "analysis": "ready", 
    "alerts": "ready"
  },
  "bigquery": {
    "bigquery_available": false,
    "bigquery_enabled": false,
    "project_id": null
  },
  "adk_available": false,
  "timestamp": "2025-01-11T15:30:00Z"
}
```

### Analysis Endpoints

#### `POST /analyze` - Direct Analysis
```bash
curl -X POST "https://your-service-url/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "sensor_data": [
      {
        "location": "Building A",
        "temperature": 75,
        "smoke_level": 85,
        "timestamp": "2025-01-11T15:30:00Z"
      }
    ]
  }'
```

#### `POST /pipeline` - Full Pipeline
```bash
curl -X POST "https://your-service-url/pipeline" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "sample_data.json",
    "bigquery_config": {
      "project_id": "your-project-id"
    }
  }'
```

## 🏗️ Architecture

### Container Architecture
```
┌─────────────────────────────────────────┐
│              Docker Container           │
├─────────────────────────────────────────┤
│  FastAPI Server (main.py)              │
│  ├─ Google ADK Integration              │
│  ├─ RESTful API Endpoints               │
│  └─ Health Checks & Monitoring         │
├─────────────────────────────────────────┤
│  3-Agent Pipeline                       │
│  ├─ DetectionAgent (+ BigQuery)         │
│  ├─ AnalysisAgent                       │
│  └─ AlertAgent                          │
├─────────────────────────────────────────┤
│  Python 3.10-slim Base                 │
│  ├─ Security: Non-root user             │
│  ├─ Optimization: Layer caching         │
│  └─ Monitoring: Health checks           │
└─────────────────────────────────────────┘
```

### Cloud Run Deployment
```
┌─────────────────────────────────────────┐
│           Google Cloud Run              │
├─────────────────────────────────────────┤
│  Auto-scaling: 0-100 instances         │
│  Resource: 1 CPU, 1GB RAM              │
│  Timeout: 3600 seconds                 │
│  Concurrency: 80 requests/instance     │
├─────────────────────────────────────────┤
│  Load Balancer & HTTPS                 │
│  Health Monitoring                     │
│  Request Logging                       │
├─────────────────────────────────────────┤
│  Service Account Integration            │
│  BigQuery Access                       │
│  Cloud Logging & Monitoring            │
└─────────────────────────────────────────┘
```

## 🔧 Configuration

### Environment Variables

#### Production Environment
```bash
# Cloud Run automatically sets these
PORT=8080                    # Container port
ENVIRONMENT=production       # Environment type
GOOGLE_CLOUD_PROJECT=my-project  # GCP project ID

# Optional: BigQuery configuration
BIGQUERY_DATASET=disaster_response
BIGQUERY_TABLE=sensor_readings
```

#### Local Development
```bash
# Local development settings
HOST=0.0.0.0
PORT=8080
ENVIRONMENT=development

# Optional: Google Cloud authentication
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Cloud Run Configuration

#### Resource Allocation
- **CPU**: 1 vCPU per instance
- **Memory**: 1GB RAM per instance
- **Concurrency**: 80 concurrent requests per instance
- **Timeout**: 1 hour per request (for long-running analysis)

#### Auto-scaling
- **Min Instances**: 0 (scales to zero when idle)
- **Max Instances**: 100 (handles high traffic spikes)
- **Startup Time**: ~10 seconds with cold start optimization

#### Security
- **Non-root Container**: App runs as `app` user
- **Minimal Attack Surface**: Only required dependencies installed
- **HTTPS Only**: Cloud Run provides automatic TLS termination

## 🚀 Deployment Guide

### Prerequisites
```bash
# Install required tools
curl https://sdk.cloud.google.com | bash
docker --version
gcloud --version

# Authenticate with Google Cloud
gcloud auth login
gcloud auth configure-docker
```

### Basic Deployment
```bash
# 1. Set project
export GOOGLE_CLOUD_PROJECT="your-project-id"

# 2. Deploy
./deploy.sh

# 3. Test deployment
curl $(gcloud run services describe disaster-response-system \
  --region=us-central1 --format='value(status.url)')/health
```

### Advanced Deployment
```bash
# Custom region and image tag
GOOGLE_CLOUD_PROJECT=my-project \
REGION=europe-west1 \
IMAGE_TAG=v1.0.0 \
CREATE_SERVICE_ACCOUNT=true \
./deploy.sh
```

### CI/CD Integration
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud Run
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - uses: google-github-actions/setup-gcloud@v1
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.GCP_PROJECT_ID }}
    - name: Deploy
      run: ./deploy.sh
      env:
        GOOGLE_CLOUD_PROJECT: ${{ secrets.GCP_PROJECT_ID }}
```

## 📊 Monitoring & Observability

### Health Checks
```bash
# Container health
curl https://your-service-url/health

# System status
curl https://your-service-url/status

# Agent information
curl https://your-service-url/agents
```

### Cloud Logging
```bash
# View logs
gcloud logs tail --service=disaster-response-system --region=us-central1

# Filter by severity
gcloud logs read --filter='severity>=ERROR' --service=disaster-response-system
```

### Metrics & Monitoring
- **Request Latency**: Average response time per endpoint
- **Error Rate**: 4xx/5xx response percentage
- **Throughput**: Requests per second
- **Instance Count**: Active container instances
- **Memory Usage**: RAM utilization per instance
- **CPU Usage**: CPU utilization per instance

## 🔍 Troubleshooting

### Common Issues

#### Container Won't Start
```bash
# Check logs
gcloud logs read --service=disaster-response-system --limit=50

# Common causes:
# - Missing dependencies in requirements.txt
# - Port configuration mismatch
# - Python path issues
```

#### Health Check Failures
```bash
# Test locally
docker run -p 8080:8080 disaster-response-system
curl http://localhost:8080/health

# Common causes:
# - Agent initialization failures
# - Missing environment variables
# - Import errors
```

#### BigQuery Connection Issues
```bash
# Check service account permissions
gcloud projects get-iam-policy your-project-id

# Verify service account has roles:
# - roles/bigquery.dataEditor
# - roles/bigquery.jobUser
```

#### Performance Issues
```bash
# Monitor resource usage
gcloud monitoring metrics list --filter="resource.type=cloud_run_revision"

# Scaling configuration
gcloud run services update disaster-response-system \
  --memory=2Gi \
  --cpu=2 \
  --concurrency=40
```

## 🔮 Production Considerations

### Security
- **Service Account**: Use dedicated service account with minimal permissions
- **VPC Connector**: Deploy in private VPC for enhanced security
- **Identity-Aware Proxy**: Add authentication for sensitive endpoints
- **Secrets Management**: Use Google Secret Manager for credentials

### Scalability
- **Database**: Consider Cloud SQL for persistent data storage
- **Caching**: Add Redis for response caching
- **Load Testing**: Validate performance under expected load
- **Regional Deployment**: Deploy to multiple regions for reliability

### Cost Optimization
- **Request Batching**: Batch multiple sensor readings per request
- **Connection Pooling**: Reuse database connections
- **Image Optimization**: Use smaller base images
- **Auto-scaling Tuning**: Optimize min/max instances based on usage

### Maintenance
- **Automated Updates**: Set up automated container image updates
- **Backup Strategy**: Regular backup of BigQuery data
- **Disaster Recovery**: Multi-region deployment strategy
- **Version Management**: Implement blue-green deployments

---

**Status**: ✅ Step 7 Complete - Containerization & Cloud Run Deployment Implemented  
**Next**: Production hardening and advanced monitoring  
**Dependencies**: Google Cloud Project, Docker, gcloud CLI 