# BigQuery Integration for Disaster Response System

## Overview

Step 6 enhances the DetectionAgent with **Google Cloud BigQuery logging** capabilities for historical data storage and analysis. The system maintains full functionality without BigQuery while providing powerful data warehousing when configured.

## ✅ Step 6 Complete: BigQuery Logging Integration

### 🎯 What Was Implemented

#### 1. **Enhanced DetectionAgent** (`detection_agent.py`)
- ✅ **Google Cloud BigQuery client integration**
- ✅ **Automatic dataset and table creation**
- ✅ **Sensor data logging to BigQuery**
- ✅ **Historical data querying capabilities**
- ✅ **Graceful fallback when BigQuery unavailable**
- ✅ **Comprehensive error handling and status reporting**

#### 2. **BigQuery Schema Design**
```sql
CREATE TABLE `project.disaster_response.sensor_readings` (
  detection_id STRING NOT NULL,
  file_name STRING NOT NULL,
  file_path STRING NOT NULL,
  location STRING NOT NULL,
  temperature FLOAT64 NOT NULL,
  smoke_level FLOAT64 NOT NULL,
  sensor_timestamp TIMESTAMP NOT NULL,
  detection_timestamp TIMESTAMP NOT NULL,
  file_size INT64,
  total_readings INT64
);
```

#### 3. **Enhanced Orchestrator** (`orchestrator.py`)
- ✅ **BigQuery configuration management**
- ✅ **Status reporting and monitoring**
- ✅ **Historical data query interface**
- ✅ **Demonstration of BigQuery capabilities**

### 🚀 Configuration

#### Basic Setup
```python
# Configure BigQuery logging
bigquery_config = {
    "project_id": "your-gcp-project-id",      # Required
    "dataset_id": "disaster_response",        # Optional (default)
    "table_id": "sensor_readings",           # Optional (default)
    "location": "US"                         # Optional (default)
}

# Initialize orchestrator with BigQuery
orchestrator = DisasterResponseOrchestrator(
    bigquery_config=bigquery_config
)
```

#### Environment Setup
```bash
# Install BigQuery client
pip install google-cloud-bigquery>=3.0.0

# Set up authentication (choose one)
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
# OR
gcloud auth application-default login
```

### 📊 Features

#### Automatic Infrastructure Creation
- **Dataset Creation**: Creates `disaster_response` dataset if not exists
- **Table Creation**: Creates `sensor_readings` table with proper schema
- **Error Handling**: Graceful handling of permissions and network issues

#### Data Logging
- **Real-time Logging**: Each detected sensor reading logged immediately
- **Metadata Tracking**: File information, timestamps, and detection context
- **Batch Operations**: Efficient bulk inserts for multiple readings
- **Status Reporting**: Detailed logging status in pipeline results

#### Historical Queries
```python
# Query recent data for all locations
historical_data = await orchestrator.query_historical_data(hours_back=24)

# Query specific location
location_data = await orchestrator.query_historical_data(
    location="Building A - Server Room", 
    hours_back=48
)
```

### 🔍 Pipeline Integration

#### Detection Results with BigQuery Status
```json
{
  "detection": {
    "status": "data_detected",
    "file_info": {...},
    "bigquery_logging": {
      "enabled": true,
      "status": "success",
      "rows_inserted": 3,
      "table_id": "project.disaster_response.sensor_readings",
      "detection_id": "detection_20250620_201731_123456"
    }
  }
}
```

#### Status Options
- `"not_attempted"`: BigQuery not configured
- `"bigquery_not_enabled"`: BigQuery disabled
- `"success"`: Data successfully logged
- `"error"`: Logging failed (with error details)
- `"insert_errors"`: Partial failure (with error details)

### 🧪 Testing

#### Comprehensive Test Coverage
```bash
# Run full test suite including BigQuery tests
python test_orchestrator.py
```

#### Test Scenarios
- ✅ **DetectionAgent without BigQuery config**
- ✅ **DetectionAgent with BigQuery config (no credentials)**
- ✅ **Orchestrator BigQuery configuration**
- ✅ **Data detection with BigQuery logging attempts**
- ✅ **Error handling for all BigQuery scenarios**
- ✅ **Status reporting in all pipeline stages**

### 📈 Benefits

#### Historical Analysis
- **Trend Detection**: Identify patterns in sensor readings over time
- **Location Analytics**: Compare risk levels across different areas
- **Temporal Analysis**: Understand how conditions change throughout day/week
- **Capacity Planning**: Plan sensor deployment based on historical data

#### Operational Intelligence
- **Audit Trail**: Complete record of all detected sensor readings
- **Performance Monitoring**: Track detection system performance
- **Data Quality**: Validate sensor data accuracy and consistency
- **Compliance**: Maintain records for regulatory requirements

### 🛠️ Production Deployment

#### Google Cloud Project Setup
```bash
# Create BigQuery dataset
bq mk --dataset --location=US your-project:disaster_response

# Grant permissions (if using service account)
bq add-iam-policy-binding \
    --member="serviceAccount:service-account@project.iam.gserviceaccount.com" \
    --role="roles/bigquery.dataEditor" \
    your-project:disaster_response
```

#### Service Account Permissions
Required IAM roles:
- `BigQuery Data Editor`: Insert and query data
- `BigQuery Job User`: Run queries
- `BigQuery Dataset Viewer`: List datasets (optional)

#### Environment Variables
```bash
export GOOGLE_CLOUD_PROJECT="your-project-id"
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
```

### 🔧 Troubleshooting

#### Common Issues

**BigQuery Not Available**
```
⚠️  Google Cloud BigQuery not available, detection will work without logging
```
- Solution: Install `google-cloud-bigquery` package

**Authentication Failed**
```
BigQuery initialization failed: DefaultCredentialsError
```
- Solution: Set up Google Cloud authentication

**Permission Denied**
```
BigQuery initialization failed: 403 Access denied
```
- Solution: Grant proper IAM roles to service account

**Table Creation Failed**
```
Error creating dataset: Dataset already exists
```
- This is normal - the system handles existing resources gracefully

### 📊 Monitoring

#### BigQuery Status Check
```python
# Get detailed BigQuery status
status = orchestrator.get_bigquery_status()
print(f"BigQuery Enabled: {status['bigquery_enabled']}")
print(f"Table: {status['full_table_id']}")
```

#### Query Performance
```sql
-- Monitor table size
SELECT 
  COUNT(*) as total_rows,
  COUNT(DISTINCT location) as unique_locations,
  MIN(detection_timestamp) as first_detection,
  MAX(detection_timestamp) as last_detection
FROM `project.disaster_response.sensor_readings`;
```

### 🔮 Future Enhancements

#### Phase 7: Advanced Analytics
- **ML Integration**: Train models on historical data for predictive analysis
- **Real-time Dashboards**: BigQuery + Data Studio visualization
- **Anomaly Detection**: Identify unusual patterns in sensor readings
- **Automated Alerting**: BigQuery-based threshold monitoring

#### Phase 8: Data Pipeline
- **Streaming Inserts**: Real-time data pipeline with Pub/Sub
- **Data Lake Integration**: Export to Cloud Storage for long-term archival
- **Data Validation**: Automated data quality checks and cleansing
- **Multi-region Replication**: Disaster recovery and compliance

---

**Status**: ✅ Step 6 Complete - BigQuery Integration Implemented  
**Next**: Advanced Analytics and ML Integration
**Dependencies**: Google Cloud Project, BigQuery API enabled, Authentication configured 