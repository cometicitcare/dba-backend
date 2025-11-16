#!/bin/bash

# Industry-Level Email & OTP Service Installation Script
# This script helps you set up the new services quickly

set -e

echo "=========================================="
echo "Email & OTP Service Upgrade Installation"
echo "=========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Step 1: Install Python dependencies
echo "Step 1: Installing Python dependencies..."
if pip install redis==5.0.1 hiredis==2.3.2; then
    print_success "Python dependencies installed"
else
    print_error "Failed to install dependencies"
    exit 1
fi
echo ""

# Step 2: Check if Redis is running
echo "Step 2: Checking Redis connection..."
if command -v redis-cli &> /dev/null; then
    if redis-cli ping &> /dev/null; then
        print_success "Redis is running and accessible"
        REDIS_RUNNING=true
    else
        print_warning "Redis is installed but not running"
        REDIS_RUNNING=false
    fi
else
    print_warning "Redis CLI not found. Redis may not be installed."
    REDIS_RUNNING=false
fi
echo ""

# Step 3: Offer to start Redis with Docker if not running
if [ "$REDIS_RUNNING" = false ]; then
    echo "Step 3: Redis Setup Options"
    echo "─────────────────────────────"
    echo "Redis is required for production OTP storage."
    echo ""
    echo "Options:"
    echo "  1) Start Redis with Docker (recommended for development)"
    echo "  2) I'll set up Redis manually later"
    echo "  3) Use in-memory storage (NOT recommended for production)"
    echo ""
    read -p "Choose an option (1-3): " redis_option
    
    case $redis_option in
        1)
            if command -v docker &> /dev/null; then
                echo ""
                echo "Starting Redis with Docker..."
                read -sp "Enter Redis password (or press Enter for no password): " redis_pass
                echo ""
                
                if [ -z "$redis_pass" ]; then
                    docker run -d --name redis-otp -p 6379:6379 redis:7-alpine
                else
                    docker run -d --name redis-otp -p 6379:6379 redis:7-alpine redis-server --requirepass "$redis_pass"
                fi
                
                sleep 2
                
                if docker ps | grep -q redis-otp; then
                    print_success "Redis container started successfully"
                    REDIS_RUNNING=true
                else
                    print_error "Failed to start Redis container"
                fi
            else
                print_error "Docker is not installed. Please install Docker first."
            fi
            ;;
        2)
            print_warning "Remember to set up Redis before deploying to production"
            ;;
        3)
            print_warning "Using in-memory storage. OTPs will be lost on restart."
            ;;
    esac
fi
echo ""

# Step 4: Update .env file
echo "Step 4: Updating environment variables..."
if [ -f .env ]; then
    # Backup existing .env
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    print_success ".env file backed up"
    
    # Add new environment variables if they don't exist
    if ! grep -q "OTP_MAX_ATTEMPTS" .env; then
        cat >> .env << EOF

# ============================================================================
# Industry-Level Email & OTP Configuration (Added $(date +%Y-%m-%d))
# ============================================================================

# OTP Configuration
OTP_EXPIRE_MINUTES=10
OTP_LENGTH=6
OTP_MAX_ATTEMPTS=3
OTP_MAX_REQUESTS_PER_HOUR=5
OTP_MAX_REQUESTS_PER_DAY=10

# Redis Configuration
REDIS_ENABLED=${REDIS_RUNNING}
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
EOF
        print_success "Environment variables added to .env"
    else
        print_warning "OTP configuration already exists in .env"
    fi
else
    print_warning ".env file not found. Please create it manually."
    echo "See .env.email-otp-example for reference."
fi
echo ""

# Step 5: Test the installation
echo "Step 5: Testing installation..."
python3 << 'PYTHON_TEST'
import sys
try:
    # Test imports
    from app.services.email_service_v2 import email_service_v2
    from app.services.otp_service_v2 import otp_service_v2
    from app.services.background_tasks import background_task_service
    
    print("✓ All modules imported successfully")
    
    # Check OTP service storage type
    metrics = otp_service_v2.get_metrics()
    storage_type = metrics.get('storage_type', 'unknown')
    
    if storage_type == 'redis':
        print("✓ OTP service connected to Redis")
    else:
        print("⚠ OTP service using in-memory storage (Redis not available)")
    
    sys.exit(0)
except Exception as e:
    print(f"✗ Error during testing: {e}")
    sys.exit(1)
PYTHON_TEST

if [ $? -eq 0 ]; then
    print_success "Installation test passed"
else
    print_error "Installation test failed"
fi
echo ""

# Step 6: Summary and next steps
echo "=========================================="
echo "Installation Complete!"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ Dependencies installed"
if [ "$REDIS_RUNNING" = true ]; then
    echo "  ✓ Redis running"
else
    echo "  ⚠ Redis not configured"
fi
echo "  ✓ Environment variables updated"
echo ""
echo "Next Steps:"
echo "  1. Review EMAIL_OTP_UPGRADE_GUIDE.md for detailed documentation"
echo "  2. Test email sending: python -m app.services.test_email_service"
echo "  3. Test OTP generation: python -m app.services.test_otp_service"
echo "  4. Update your code to use the new services (backward compatible)"
echo "  5. Monitor metrics after deployment"
echo ""
echo "For production deployment:"
if [ "$REDIS_RUNNING" = false ]; then
    echo "  • Set up Redis (Railway, Redis Cloud, or self-hosted)"
    echo "  • Update REDIS_* environment variables"
fi
echo "  • Set REDIS_ENABLED=true in production .env"
echo "  • Configure monitoring and alerts"
echo "  • Review rate limits and adjust as needed"
echo ""
print_success "Setup script completed!"
