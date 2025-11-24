#!/usr/bin/env bash
# Setup script for Bhikku Management System
# This script sets up all necessary permissions, roles, and users

set -e

echo "========================================================================"
echo "  Bhikku Management System Setup"
echo "========================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

echo "Running complete setup..."
echo ""

# Check if running in Docker
if [ -f "/.dockerenv" ] || grep -q docker /proc/1/cgroup 2>/dev/null; then
    echo "Running in Docker container..."
    python -m app.utils.setup_bhikku_complete
else
    # Check if Docker Compose is running
    if docker compose ps | grep -q "api.*Up"; then
        echo "Running via Docker Compose..."
        docker compose exec api python -m app.utils.setup_bhikku_complete
    else
        echo "Docker Compose not running. Starting it now..."
        docker compose up -d
        echo "Waiting for services to be ready..."
        sleep 5
        docker compose exec api python -m app.utils.setup_bhikku_complete
    fi
fi

echo ""
echo "========================================================================"
echo "  Setup Complete!"
echo "========================================================================"
echo ""
echo "You can now test the API with:"
echo ""
echo "1. Login as bhikku_admin:"
echo "   curl -X POST https://api.dbagovlk.com/api/v1/auth/login \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -c cookies.txt \\"
echo "     -d '{\"ua_username\":\"bhikku_admin\",\"ua_password\":\"Bhikku@123\"}'"
echo ""
echo "2. Use the saved cookies to make requests:"
echo "   curl -X POST https://api.dbagovlk.com/api/v1/bhikkus-high/manage \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -b cookies.txt \\"
echo "     -d @test_payload.json"
echo ""
echo "========================================================================"
