@echo off
:: ══════════════════════════════════════════════════════════════════════════════
:: Export_Video.bat
:: Exports NutriAI_Presentation.pptx → NutriAI_Video.mp4
:: Double-click this file from the nutrition-ai folder
:: ══════════════════════════════════════════════════════════════════════════════
title NutriAI — Export Presentation to Video (150s MP4)

echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║  🎬  NutriAI — Export to MP4 Video (150 seconds)        ║
echo  ║  20 slides x 7.5s = 150s  ^|  Full HD 1080p             ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
echo  Requirements:
echo    - Microsoft PowerPoint 2016 / 2019 / 2021 / 365
echo    - Python 3.9+ in PATH
echo.
echo  Starting export...
echo.

PowerShell -ExecutionPolicy Bypass -File "%~dp0Export_NutriAI_Video.ps1"

echo.
echo  Finished! Check nutrition-ai folder for NutriAI_Video.mp4
pause
