#!/bin/bash

echo "Pulling the github repository"
git pull

# Kill any process running on port 8000
PID=$(lsof -t -i:8000)
if [ -n "$PID" ]; then
    echo "Killing process $PID running on port 8000"
    sudo kill -9 $PID
fi

# Activate the virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip3 install -r requirements.txt

# Run the Gunicorn server in the background
echo "Starting Gunicorn server..."
nohup gunicorn world_model.wsgi &> gunicorn.log &

echo "Server is running in the background."
