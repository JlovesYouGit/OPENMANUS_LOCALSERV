@echo off
echo Starting local server for OpenManus Cover Page...
echo.
echo Open your browser and navigate to http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

cd /d "n:\Openmanus\OpenManus\coverpage\Animatedlandingpagedesign\dist"
python -m http.server 8000