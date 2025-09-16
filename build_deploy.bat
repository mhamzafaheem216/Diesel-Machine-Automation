@echo off
echo Building Diesel Automation Service...

REM Create build directory
if not exist build mkdir build

REM Build using our spec file
pyinstaller diesel-service.spec

echo.
echo Building complete!
echo.

REM Create deployment directory structure
if not exist deploy mkdir deploy

echo Copying files to deployment directory...
copy /Y dist\diesel-service.exe deploy\
copy /Y config.py deploy\

echo.
echo Deployment package created successfully!
echo Files are ready in the 'deploy' folder.
echo.
echo To deploy:
echo 1. Copy the 'deploy' folder to your server
echo 2. Configure config.py as needed
echo 3. Set up the service using NSSM or Windows Service Manager
echo.