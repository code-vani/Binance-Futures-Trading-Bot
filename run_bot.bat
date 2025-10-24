@echo off
REM Trading Bot Startup Script for Windows
REM This fixes Unicode character display issues

REM Set console to UTF-8 encoding
chcp 65001 > nul

REM Clear screen
cls

REM Run the trading bot
python cli.py

REM Keep window open if error occurs
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Error occurred! Press any key to exit...
    pause > nul
)