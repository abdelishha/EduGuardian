@echo off
:: EduGuardian — Easy Start Script for Windows
:: Just double-click this file to start EduGuardian!

echo.
echo ============================================================
echo  EduGuardian - AI Study Companion and Wellness Advisor
echo ============================================================
echo.

:: Set UTF-8 mode so emoji characters work in the terminal
set PYTHONUTF8=1

:: Activate the virtual environment
call venv\Scripts\activate

:: Run the server
echo Starting EduGuardian...
echo Open your browser at: http://localhost:5000
echo Press CTRL+C to stop.
echo.
python main.py

pause
