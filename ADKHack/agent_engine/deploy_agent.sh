#!/bin/bash

# Disaster Response System - Vertex AI Agent Engine Deployment Script
# This script deploys the disaster response agent to Google Vertex AI Agent Engine

set -e  # Exit on any error

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
REGION=${REGION:-"us-central1"}
AGENT_NAME="disaster-response-agent"
AGENT_VERSION=${AGENT_VERSION:-"v1.0.0"}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites for Agent Engine deployment..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if logged into gcloud
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "Please log in to gcloud: gcloud auth login"
        exit 1
    fi
    
    # Set project if provided
    if [ "$PROJECT_ID" != "your-project-id" ]; then
        gcloud config set project $PROJECT_ID
        log_success "Project set to $PROJECT_ID"
    else
        log_warning "Using default project. Set GOOGLE_CLOUD_PROJECT environment variable to override."
        PROJECT_ID=$(gcloud config get-value project)
    fi
    
    # Check if ADK is available
    python -c "import google.adk" 2>/dev/null || {
        log_warning "Google ADK not available. Agent will use fallback implementation."
    }
    
    log_success "Prerequisites check completed"
}

# Enable required APIs
enable_apis() {
    log_info "Enabling required Google Cloud APIs for Agent Engine..."
    
    gcloud services enable aiplatform.googleapis.com \
                          bigquery.googleapis.com \
                          logging.googleapis.com \
                          monitoring.googleapis.com \
                          storage.googleapis.com
    
    log_success "APIs enabled"
}

# Create service account for the agent
create_service_account() {
    log_info "Creating service account for Agent Engine..."
    
    SA_NAME="disaster-response-agent-sa"
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    
    # Create service account if it doesn't exist
    if ! gcloud iam service-accounts describe $SA_EMAIL &> /dev/null; then
        gcloud iam service-accounts create $SA_NAME \
            --display-name="Disaster Response Agent Service Account" \
            --description="Service account for disaster response agent in Vertex AI"
        
        # Grant required permissions
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$SA_EMAIL" \
            --role="roles/bigquery.dataEditor"
        
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$SA_EMAIL" \
            --role="roles/bigquery.jobUser"
        
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$SA_EMAIL" \
            --role="roles/logging.logWriter"
        
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$SA_EMAIL" \
            --role="roles/monitoring.metricWriter"
        
        log_success "Service account created and configured"
    else
        log_info "Service account already exists"
    fi
}

# Prepare agent package
prepare_agent_package() {
    log_info "Preparing agent package for deployment..."
    
    # Create temporary directory for packaging
    TEMP_DIR=$(mktemp -d)
    PACKAGE_DIR="$TEMP_DIR/disaster_response_agent"
    
    mkdir -p "$PACKAGE_DIR"
    
    # Copy agent engine files
    cp -r agent_engine/* "$PACKAGE_DIR/"
    
    # Copy python_agents directory
    cp -r python_agents "$PACKAGE_DIR/"
    
    # Update agent config with actual project ID
    sed "s/PROJECT_ID/${PROJECT_ID}/g" agent_engine/agent_config.yaml > "$PACKAGE_DIR/agent_config.yaml"
    
    # Create package archive
    cd "$TEMP_DIR"
    tar -czf "disaster_response_agent_${AGENT_VERSION}.tar.gz" disaster_response_agent/
    
    AGENT_PACKAGE="$TEMP_DIR/disaster_response_agent_${AGENT_VERSION}.tar.gz"
    
    log_success "Agent package prepared: $AGENT_PACKAGE"
}

# Upload agent to Vertex AI
upload_agent() {
    log_info "Uploading agent to Vertex AI Agent Engine..."
    
    # Note: This is a placeholder command structure
    # The actual gcloud command for Agent Engine may differ
    # Replace with actual Vertex AI Agent Engine deployment command when available
    
    log_warning "Agent Engine deployment command placeholder - update with actual gcloud command"
    
    # Placeholder command structure:
    # gcloud ai agents deploy \
    #     --agent-package="$AGENT_PACKAGE" \
    #     --region="$REGION" \
    #     --service-account="disaster-response-agent-sa@${PROJECT_ID}.iam.gserviceaccount.com" \
    #     --config="$PACKAGE_DIR/agent_config.yaml"
    
    log_info "Would deploy with:"
    log_info "  Package: $AGENT_PACKAGE"
    log_info "  Region: $REGION"
    log_info "  Service Account: disaster-response-agent-sa@${PROJECT_ID}.iam.gserviceaccount.com"
    
    # For now, just verify the package structure
    log_info "Verifying agent package structure..."
    tar -tzf "$AGENT_PACKAGE" | head -20
    
    log_success "Agent package verified and ready for deployment"
}

# Test agent deployment
test_agent() {
    log_info "Testing agent deployment..."
    
    # Test agent import
    cd "$PACKAGE_DIR"
    python -c "
import sys
sys.path.insert(0, '.')
try:
    from agent import root_agent, AGENT_CONFIG
    print('✅ Agent import successful')
    print(f'Agent name: {root_agent.name}')
    print(f'Agent description: {root_agent.description}')
    print(f'Sub-agents: {len(root_agent.sub_agents)}')
    print('✅ Agent configuration valid')
except Exception as e:
    print(f'❌ Agent import failed: {e}')
    exit(1)
"
    
    log_success "Agent testing completed"
}

# Main deployment function
main() {
    echo "🚀 Disaster Response System - Vertex AI Agent Engine Deployment"
    echo "=============================================================="
    
    check_prerequisites
    enable_apis
    create_service_account
    prepare_agent_package
    upload_agent
    test_agent
    
    log_success "Agent Engine deployment process completed! 🎉"
    
    echo ""
    echo "📋 Next Steps:"
    echo "1. Update the upload_agent() function with actual Vertex AI commands"
    echo "2. Configure agent endpoints and access policies"
    echo "3. Set up monitoring and alerting for the deployed agent"
    echo "4. Test agent execution with sample data"
    echo ""
    echo "📚 For more information:"
    echo "https://cloud.google.com/vertex-ai/docs/agent-engine"
}

# Help function
show_help() {
    echo "Disaster Response System - Agent Engine Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Environment Variables:"
    echo "  GOOGLE_CLOUD_PROJECT    Google Cloud project ID"
    echo "  REGION                  Vertex AI region (default: us-central1)"
    echo "  AGENT_VERSION          Agent version tag (default: v1.0.0)"
    echo ""
    echo "Examples:"
    echo "  # Basic deployment"
    echo "  GOOGLE_CLOUD_PROJECT=my-project ./deploy_agent.sh"
    echo ""
    echo "  # With custom region and version"
    echo "  GOOGLE_CLOUD_PROJECT=my-project REGION=europe-west4 AGENT_VERSION=v1.1.0 ./deploy_agent.sh"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac 