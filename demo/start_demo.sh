#!/bin/bash

cd "$(dirname "$0")"

echo "Starting Flask backend..."
uv run demo_agent.py &
FLASK_PID=$!

sleep 3

echo "Starting Streamlit frontend..."
streamlit run app.py &
STREAMLIT_PID=$!

echo "Demo services started!"
echo "Flask backend PID: $FLASK_PID"
echo "Streamlit frontend PID: $STREAMLIT_PID"
echo ""
echo "Press Ctrl+C to stop both services"

trap "kill $FLASK_PID $STREAMLIT_PID 2>/dev/null" EXIT

wait
