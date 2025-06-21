#!/bin/bash

# Disaster Response System - Cloud Run Deployment Script
# This script builds and deploys the disaster response system to Google Cloud Run

set -e  # Exit on any error

# Configuration
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-"your-project-id"}
SERVICE_NAME="disaster-response-system"
REGION=${REGION:-"us-central1"}
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
IMAGE_TAG=${IMAGE_TAG:-"latest"}
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

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
    log_info "Checking prerequisites..."
    
    # Check if gcloud is installed
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install it first."
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
        FULL_IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}:${IMAGE_TAG}"
    fi
    
    log_success "Prerequisites check completed"
}

# Enable required APIs
enable_apis() {
    log_info "Enabling required Google Cloud APIs..."
    
    gcloud services enable cloudbuild.googleapis.com \
                          run.googleapis.com \
                          containerregistry.googleapis.com \
                          bigquery.googleapis.com \
                          logging.googleapis.com \
                          monitoring.googleapis.com
    
    log_success "APIs enabled"
}

# Build Docker image
build_image() {
    log_info "Building Docker image: $FULL_IMAGE_NAME"
    
    # Configure Docker for GCR
    gcloud auth configure-docker --quiet
    
    # Build the image
    docker build -t $FULL_IMAGE_NAME .
    
    log_success "Docker image built successfully"
}

# Push image to Container Registry
push_image() {
    log_info "Pushing image to Google Container Registry..."
    
    docker push $FULL_IMAGE_NAME
    
    log_success "Image pushed to GCR"
}

# Deploy to Cloud Run
deploy_service() {
    log_info "Deploying to Cloud Run..."
    
    # Update the cloud-run.yaml with actual project ID
    sed "s/PROJECT_ID/${PROJECT_ID}/g" cloud-run.yaml > cloud-run-deploy.yaml
    
    # Deploy using gcloud
    gcloud run services replace cloud-run-deploy.yaml \
        --region=$REGION \
        --platform=managed
    
    # Clean up temporary file
    rm cloud-run-deploy.yaml
    
    log_success "Service deployed to Cloud Run"
}

# Get service URL
get_service_url() {
    log_info "Getting service URL..."
    
    SERVICE_URL=$(gcloud run services describe $SERVICE_NAME \
        --region=$REGION \
        --platform=managed \
        --format="value(status.url)")
    
    log_success "Service deployed successfully!"
    echo ""
    echo "🚀 Service URL: $SERVICE_URL"
    echo "📊 Health Check: $SERVICE_URL/health"
    echo "📋 API Documentation: $SERVICE_URL/docs"
    echo "📈 System Status: $SERVICE_URL/status"
    echo ""
    echo "🔧 To test the service:"
    echo "curl $SERVICE_URL/health"
    echo ""
    echo "📝 To view logs:"
    echo "gcloud logs tail --service=$SERVICE_NAME --region=$REGION"
}

# Create service account for BigQuery (optional)
create_service_account() {
    log_info "Creating service account for BigQuery access..."
    
    SA_NAME="disaster-response-sa"
    SA_EMAIL="${SA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"
    
    # Create service account if it doesn't exist
    if ! gcloud iam service-accounts describe $SA_EMAIL &> /dev/null; then
        gcloud iam service-accounts create $SA_NAME \
            --display-name="Disaster Response System Service Account" \
            --description="Service account for disaster response system BigQuery access"
        
        # Grant BigQuery permissions
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$SA_EMAIL" \
            --role="roles/bigquery.dataEditor"
        
        gcloud projects add-iam-policy-binding $PROJECT_ID \
            --member="serviceAccount:$SA_EMAIL" \
            --role="roles/bigquery.jobUser"
        
        log_success "Service account created and configured"
    else
        log_info "Service account already exists"
    fi
}

# Main deployment function
main() {
    echo "🚀 Disaster Response System - Cloud Run Deployment"
    echo "=================================================="
    
    check_prerequisites
    enable_apis
    
    # Optional: Create service account for BigQuery
    if [ "$CREATE_SERVICE_ACCOUNT" = "true" ]; then
        create_service_account
    fi
    
    build_image
    push_image
    deploy_service
    get_service_url
    
    log_success "Deployment completed successfully! 🎉"
}

# Help function
show_help() {
    echo "Disaster Response System - Cloud Run Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Environment Variables:"
    echo "  GOOGLE_CLOUD_PROJECT    Google Cloud project ID"
    echo "  REGION                  Cloud Run region (default: us-central1)"
    echo "  IMAGE_TAG              Docker image tag (default: latest)"
    echo "  CREATE_SERVICE_ACCOUNT Set to 'true' to create BigQuery service account"
    echo ""
    echo "Examples:"
    echo "  # Basic deployment"
    echo "  GOOGLE_CLOUD_PROJECT=my-project ./deploy.sh"
    echo ""
    echo "  # With custom region and tag"
    echo "  GOOGLE_CLOUD_PROJECT=my-project REGION=europe-west1 IMAGE_TAG=v1.0.0 ./deploy.sh"
    echo ""
    echo "  # With service account creation"
    echo "  GOOGLE_CLOUD_PROJECT=my-project CREATE_SERVICE_ACCOUNT=true ./deploy.sh"
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