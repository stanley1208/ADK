"""
Detection Agent for disaster response sensor data detection.

This agent is responsible for detecting and reading sensor data from JSON files
stored in the simulated_data/ directory. It processes one file at a time and
outputs the JSON dictionary for further analysis by other agents.
Enhanced with BigQuery logging to store detected sensor data for historical analysis.
"""

import os
import json
import glob
from datetime import datetime
from typing import Dict, List, Any, Optional

# Try to import Google Cloud BigQuery, fall back gracefully if not available
try:
    from google.cloud import bigquery
    from google.cloud.exceptions import NotFound, Forbidden
    BIGQUERY_AVAILABLE = True
except ImportError:
    print("⚠️  Google Cloud BigQuery not available, detection will work without logging")
    bigquery = None
    NotFound = Forbidden = Exception
    BIGQUERY_AVAILABLE = False

# Try to import Google ADK components, fall back to mocks if not available
try:
    from google.adk.agents import BaseAgent
    from google.adk.events import Event
    from google.adk.sessions import Session
    ADK_AVAILABLE = True
except ImportError:
    print("⚠️  Google ADK not available, using mock classes for testing")
    from utils.mocks import MockBaseAgent as BaseAgent, MockSession as Session
    Event = dict  # Simple fallback for Event
    ADK_AVAILABLE = False


class DetectionAgent(BaseAgent):
    """
    Agent responsible for detecting and reading sensor data from JSON files.
    Enhanced with BigQuery logging for historical data storage and analysis.
    
    This agent monitors the simulated_data/ directory for JSON files containing
    sensor readings, processes them one at a time, and optionally logs the data
    to BigQuery for long-term storage and trend analysis.
    """
    
    def __init__(self, name: str = "sensor_detection_agent", description: str = None, 
                 bigquery_config: Optional[Dict[str, str]] = None):
        """
        Initialize the Detection Agent with optional BigQuery logging.
        
        Args:
            name: The name of the agent
            description: Description of the agent's capabilities
            bigquery_config: Optional BigQuery configuration with keys:
                - project_id: Google Cloud project ID
                - dataset_id: BigQuery dataset ID (default: "disaster_response")
                - table_id: BigQuery table ID (default: "sensor_readings")
                - location: BigQuery dataset location (default: "US")
        """
        if description is None:
            description = (
                "AI agent specialized in detecting and reading sensor data from JSON files. "
                "Monitors the simulated_data directory for new sensor readings, processes "
                "one file at a time, and optionally logs data to BigQuery for historical analysis."
            )
        
        # Initialize the BaseAgent with ADK-specific parameters
        super().__init__(
            name=name,
            description=description
        )
        
        # Set the data directory path relative to the agent location
        self.data_directory = os.path.join(os.path.dirname(__file__), '..', 'simulated_data')
        self.data_directory = os.path.abspath(self.data_directory)
        
        # BigQuery configuration
        self.bigquery_config = bigquery_config or {}
        self.project_id = self.bigquery_config.get('project_id')
        self.dataset_id = self.bigquery_config.get('dataset_id', 'disaster_response')
        self.table_id = self.bigquery_config.get('table_id', 'sensor_readings')
        self.location = self.bigquery_config.get('location', 'US')
        
        # BigQuery client and logging state
        self.bigquery_client = None
        self.bigquery_enabled = False
        self.table_created = False
        
        # Initialize BigQuery if configuration is provided
        if BIGQUERY_AVAILABLE and self.project_id:
            self._initialize_bigquery()
    
    def _initialize_bigquery(self):
        """Initialize BigQuery client and create dataset/table if needed."""
        try:
            self.bigquery_client = bigquery.Client(project=self.project_id)
            
            # Test connection by trying to get project info
            project = self.bigquery_client.get_project(self.project_id)
            print(f"✅ BigQuery connected to project: {project.project_id}")
            
            # Create dataset and table if they don't exist
            self._ensure_dataset_exists()
            self._ensure_table_exists()
            
            self.bigquery_enabled = True
            print(f"✅ BigQuery logging enabled: {self.project_id}.{self.dataset_id}.{self.table_id}")
            
        except Exception as e:
            print(f"⚠️  BigQuery initialization failed: {e}")
            print("   Detection will continue without BigQuery logging")
            self.bigquery_enabled = False
    
    def _ensure_dataset_exists(self):
        """Create BigQuery dataset if it doesn't exist."""
        dataset_id = f"{self.project_id}.{self.dataset_id}"
        
        try:
            self.bigquery_client.get_dataset(dataset_id)
            print(f"📊 BigQuery dataset exists: {dataset_id}")
        except NotFound:
            # Create the dataset
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = self.location
            dataset.description = "Disaster response sensor data storage"
            
            dataset = self.bigquery_client.create_dataset(dataset, timeout=30)
            print(f"📊 Created BigQuery dataset: {dataset.dataset_id}")
    
    def _ensure_table_exists(self):
        """Create BigQuery table if it doesn't exist."""
        table_id = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
        
        try:
            self.bigquery_client.get_table(table_id)
            print(f"📋 BigQuery table exists: {table_id}")
            self.table_created = True
        except NotFound:
            # Define table schema for sensor readings
            schema = [
                bigquery.SchemaField("detection_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("file_name", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("file_path", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("location", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("temperature", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("smoke_level", "FLOAT", mode="REQUIRED"),
                bigquery.SchemaField("sensor_timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("detection_timestamp", "TIMESTAMP", mode="REQUIRED"),
                bigquery.SchemaField("file_size", "INTEGER", mode="NULLABLE"),
                bigquery.SchemaField("total_readings", "INTEGER", mode="NULLABLE"),
            ]
            
            table = bigquery.Table(table_id, schema=schema)
            table.description = "Sensor readings detected by the disaster response system"
            
            table = self.bigquery_client.create_table(table)
            print(f"📋 Created BigQuery table: {table.table_id}")
            self.table_created = True
    
    async def run(self, session: Session, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        ADK-compatible run method for detecting and reading sensor data files.
        
        Args:
            session: ADK session object for maintaining state
            input_data: Dictionary that may contain a specific file path or search parameters
            
        Returns:
            Dictionary containing the sensor data from the detected JSON file
        """
        return self.detect_and_read(input_data)
    
    def detect_and_read(self, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Detect and read sensor data from JSON files in the simulated_data directory.
        Enhanced with BigQuery logging for detected data.
        
        Args:
            input_data: Optional dictionary that may contain:
                - file_path: Specific file to read
                - pattern: File pattern to match (default: "*.json")
                
        Returns:
            Dictionary with detected sensor data and BigQuery logging status
        """
        if input_data is None:
            input_data = {}
        
        # Check if a specific file path is provided
        specific_file = input_data.get('file_path')
        if specific_file:
            return self._read_specific_file(specific_file)
        
        # Look for JSON files in the simulated_data directory
        pattern = input_data.get('pattern', '*.json')
        json_files = self._find_json_files(pattern)
        
        if not json_files:
            return {
                "status": "no_data_found",
                "message": f"No JSON files found in {self.data_directory}",
                "timestamp": datetime.now().isoformat() + 'Z',
                "detection_info": {
                    "directory_checked": self.data_directory,
                    "pattern_searched": pattern,
                    "files_found": 0
                },
                "bigquery_logging": {
                    "enabled": self.bigquery_enabled,
                    "status": "no_data_to_log"
                }
            }
        
        # Read the first available file (one at a time as requested)
        first_file = json_files[0]
        return self._read_json_file(first_file)
    
    def _find_json_files(self, pattern: str = "*.json") -> List[str]:
        """
        Find JSON files in the simulated_data directory.
        
        Args:
            pattern: File pattern to match (default: "*.json")
            
        Returns:
            List of file paths matching the pattern
        """
        if not os.path.exists(self.data_directory):
            print(f"⚠️  Data directory does not exist: {self.data_directory}")
            return []
        
        search_pattern = os.path.join(self.data_directory, pattern)
        files = glob.glob(search_pattern)
        
        # Sort files to ensure consistent processing order
        files.sort()
        return files
    
    def _read_specific_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read a specific JSON file.
        
        Args:
            file_path: Path to the specific file to read
            
        Returns:
            Dictionary containing the file data
        """
        # If relative path, make it relative to data directory
        if not os.path.isabs(file_path):
            file_path = os.path.join(self.data_directory, file_path)
        
        return self._read_json_file(file_path)
    
    def _read_json_file(self, file_path: str) -> Dict[str, Any]:
        """
        Read and parse a JSON file with BigQuery logging.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Dictionary containing the parsed JSON data with metadata and BigQuery status
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            # Add detection metadata
            detection_timestamp = datetime.now()
            result = {
                "status": "data_detected",
                "sensor_data": data.get("sensor_data", data),  # Handle both wrapped and direct formats
                "detection_info": {
                    "file_path": file_path,
                    "file_name": os.path.basename(file_path),
                    "file_size": os.path.getsize(file_path),
                    "read_timestamp": detection_timestamp.isoformat() + 'Z'
                },
                "bigquery_logging": {
                    "enabled": self.bigquery_enabled,
                    "status": "not_attempted"
                }
            }
            
            # If the data is already in the expected format, preserve it
            if "sensor_data" in data:
                result.update(data)
            else:
                # Assume the entire JSON is sensor data
                result["sensor_data"] = data
            
            # Log to BigQuery if enabled
            if self.bigquery_enabled and self.table_created:
                bigquery_status = self._log_to_bigquery(
                    result["sensor_data"], 
                    file_path, 
                    detection_timestamp
                )
                result["bigquery_logging"] = bigquery_status
            
            return result
            
        except FileNotFoundError:
            return {
                "status": "file_not_found",
                "error": f"File not found: {file_path}",
                "timestamp": datetime.now().isoformat() + 'Z',
                "bigquery_logging": {
                    "enabled": self.bigquery_enabled,
                    "status": "no_data_to_log"
                }
            }
        except json.JSONDecodeError as e:
            return {
                "status": "invalid_json",
                "error": f"Invalid JSON in file {file_path}: {str(e)}",
                "timestamp": datetime.now().isoformat() + 'Z',
                "bigquery_logging": {
                    "enabled": self.bigquery_enabled,
                    "status": "no_data_to_log"
                }
            }
        except Exception as e:
            return {
                "status": "read_error",
                "error": f"Error reading file {file_path}: {str(e)}",
                "timestamp": datetime.now().isoformat() + 'Z',
                "bigquery_logging": {
                    "enabled": self.bigquery_enabled,
                    "status": "no_data_to_log"
                }
            }
    
    def _log_to_bigquery(self, sensor_data: List[Dict[str, Any]], file_path: str, 
                        detection_timestamp: datetime) -> Dict[str, Any]:
        """
        Log detected sensor data to BigQuery.
        
        Args:
            sensor_data: List of sensor readings
            file_path: Path to the source file
            detection_timestamp: When the detection occurred
            
        Returns:
            Dictionary with BigQuery logging status
        """
        if not self.bigquery_enabled or not self.bigquery_client:
            return {
                "enabled": False,
                "status": "bigquery_not_enabled"
            }
        
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            
            # Prepare rows for insertion
            rows_to_insert = []
            detection_id = f"detection_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            file_name = os.path.basename(file_path)
            
            for i, reading in enumerate(sensor_data):
                # Parse sensor timestamp
                sensor_timestamp_str = reading.get('timestamp', detection_timestamp.isoformat())
                try:
                    # Handle different timestamp formats
                    if sensor_timestamp_str.endswith('Z'):
                        sensor_timestamp = datetime.fromisoformat(sensor_timestamp_str[:-1])
                    else:
                        sensor_timestamp = datetime.fromisoformat(sensor_timestamp_str)
                except:
                    sensor_timestamp = detection_timestamp
                
                row = {
                    "detection_id": f"{detection_id}_{i}",
                    "file_name": file_name,
                    "file_path": file_path,
                    "location": reading.get('location', 'Unknown'),
                    "temperature": float(reading.get('temperature', 0)),
                    "smoke_level": float(reading.get('smoke_level', 0)),
                    "sensor_timestamp": sensor_timestamp,
                    "detection_timestamp": detection_timestamp,
                    "file_size": os.path.getsize(file_path),
                    "total_readings": len(sensor_data)
                }
                rows_to_insert.append(row)
            
            # Insert rows into BigQuery
            errors = self.bigquery_client.insert_rows_json(
                self.bigquery_client.get_table(table_id), 
                rows_to_insert
            )
            
            if errors:
                return {
                    "enabled": True,
                    "status": "insert_errors",
                    "errors": errors,
                    "rows_attempted": len(rows_to_insert)
                }
            else:
                return {
                    "enabled": True,
                    "status": "success",
                    "rows_inserted": len(rows_to_insert),
                    "table_id": table_id,
                    "detection_id": detection_id
                }
                
        except Exception as e:
            return {
                "enabled": True,
                "status": "error",
                "error": str(e),
                "rows_attempted": len(sensor_data) if sensor_data else 0
            }
    
    def list_available_files(self) -> List[str]:
        """
        List all available JSON files in the simulated_data directory.
        
        Returns:
            List of available JSON file paths
        """
        return self._find_json_files()
    
    def get_data_directory(self) -> str:
        """
        Get the absolute path to the data directory.
        
        Returns:
            Absolute path to the simulated_data directory
        """
        return self.data_directory
    
    def get_bigquery_status(self) -> Dict[str, Any]:
        """
        Get the current BigQuery configuration and status.
        
        Returns:
            Dictionary with BigQuery status information
        """
        return {
            "bigquery_available": BIGQUERY_AVAILABLE,
            "bigquery_enabled": self.bigquery_enabled,
            "project_id": self.project_id,
            "dataset_id": self.dataset_id,
            "table_id": self.table_id,
            "table_created": self.table_created,
            "full_table_id": f"{self.project_id}.{self.dataset_id}.{self.table_id}" if self.project_id else None
        }
    
    def query_historical_data(self, location: Optional[str] = None, 
                             hours_back: int = 24) -> Optional[List[Dict[str, Any]]]:
        """
        Query historical sensor data from BigQuery.
        
        Args:
            location: Optional location filter
            hours_back: Number of hours back to query (default: 24)
            
        Returns:
            List of historical readings or None if BigQuery not available
        """
        if not self.bigquery_enabled or not self.bigquery_client:
            return None
        
        try:
            table_id = f"{self.project_id}.{self.dataset_id}.{self.table_id}"
            
            query = f"""
                SELECT 
                    location,
                    temperature,
                    smoke_level,
                    sensor_timestamp,
                    detection_timestamp
                FROM `{table_id}`
                WHERE detection_timestamp >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL {hours_back} HOUR)
            """
            
            if location:
                query += f" AND location = '{location}'"
            
            query += " ORDER BY sensor_timestamp DESC LIMIT 1000"
            
            query_job = self.bigquery_client.query(query)
            results = query_job.result()
            
            historical_data = []
            for row in results:
                historical_data.append({
                    "location": row.location,
                    "temperature": row.temperature,
                    "smoke_level": row.smoke_level,
                    "sensor_timestamp": row.sensor_timestamp.isoformat() if row.sensor_timestamp else None,
                    "detection_timestamp": row.detection_timestamp.isoformat() if row.detection_timestamp else None
                })
            
            return historical_data
            
        except Exception as e:
            print(f"⚠️  Error querying BigQuery: {e}")
            return None 