@echo off
setlocal

set "WORKDIR=C:\Users\Other User\Desktop\Claude\steel-mip\Plots\NewRegret"
set "MC_WORKERS=10"
set "REG_WORLDS=100"

cd /d "%WORKDIR%"
if not exist results mkdir results

echo [1/2] Solving PF, no-recourse and recourse epochs over 400 worlds...
python commit_mc_run.py
if errorlevel 1 echo commit_mc_run.py reported errors -- inspect results\commit_mc_results.csv

echo.
echo [2/2] Rendering the 2x2 figure and workbooks...
python commit_mc_plot.py
if errorlevel 1 echo commit_mc_plot.py failed -- is results\commit_mc_plots.xlsx open in Excel?

echo.
echo ============================
echo DONE
echo Results:  results\commit_mc_results.csv / commit_mc_results.xlsx
echo Workbook: results\commit_mc_plots.xlsx (figure data + filters + ER)
echo Figure:   fig_commit_mc_2x2.png / .pdf
echo ============================
pause
