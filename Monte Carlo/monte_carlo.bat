@echo off
setlocal

set "WORKDIR=C:\Users\Other User\Desktop\Claude\steel-mip\Plots\MC"

cd /d "%WORKDIR%"

if not exist results mkdir results

if not "%~1"=="" set "MCP_CLOUD=%~1"

echo Running probabilistic Monte-Carlo (staged; resumable)...
python mc_run.py
if errorlevel 1 (
    echo mc_run.py reported errors -- inspect results\mcp_results.csv
)

echo.
echo Building Excel workbook...
python mc_pivot.py

echo.
echo ============================
echo DONE (rerun this bat until all four clouds report complete)
echo Raw runs:  results\mcp_results.csv
echo Workbook:  results\mcp_summary.xlsx
echo ============================
pause
