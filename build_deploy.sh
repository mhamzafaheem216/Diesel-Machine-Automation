#!/bin/bash
echo "Building Diesel Automation Service..."

# Create build directory
mkdir -p build

# Build using our spec file
pyinstaller diesel-service.spec

echo
echo "Building complete!"
echo

# Create deployment directory structure
mkdir -p deploy

echo "Copying files to deployment directory..."
cp dist/diesel-service deploy/
cp config.py deploy/

echo
echo "Deployment package created successfully!"
echo "Files are ready in the 'deploy' folder."
echo
echo "To deploy:"
echo "1. Copy the 'deploy' folder to your server"
echo "2. Configure config.py as needed"
echo "3. Set up the service using systemd"
echo