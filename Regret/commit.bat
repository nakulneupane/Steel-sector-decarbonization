@echo off
setlocal

set "WORKDIR=C:\Users\Other User\Desktop\Claude\steel-mip\Plots\NewRegret"
set "MC_WORKERS=8"

cd /d "%WORKDIR%"
if not exist results mkdir results

echo [1/2] Solving plans, PF, no-recourse and recourse epochs...
python commit_run.py
if errorlevel 1 echo commit_run.py reported errors -- inspect results\commit_results.csv

echo.
echo [2/2] Rendering the 2x2 figure...
python commit_plot.py
if errorlevel 1 echo commit_plot.py failed -- is results\commit_plots.xlsx open in Excel?

echo.
echo ============================
echo DONE
echo Results:  results\commit_results.csv / commit_results.xlsx
echo Workbook: results\commit_plots.xlsx (figure data)
echo Figure:   fig_commit_2x2.png / .pdf
echo ============================
pause
