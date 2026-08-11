@echo off
setlocal EnableDelayedExpansion

rem ============================================================================
rem WHR-STEAM VALUE sweep: joint CCS+grid theta (0/0.25/0.5/0.75/1) x steam
rem sourcing (WHR-integrated vs boiler-only) = 10 runs against the model copy
rem in THIS folder. Fixed backdrop inside whr_template.mod: theta_tech 0.5,
rem H2 start 2030, scrap 6%%, Medium ramp, NG 10, cap 1.8.
rem Outputs: per-run logs + whr_summary.csv in results\, then whr_pivot.py
rem builds results\whr_summary.xlsx and whr_plot.py the figure.
rem ============================================================================

set "AMPL_EXE=C:\Users\Other User\AMPL\ampl.exe"
set "WORKDIR=C:\Users\Other User\Desktop\Claude\steel-mip\Plots\WHR"

cd /d "%WORKDIR%"

if not exist results mkdir results

echo theta,mode,whr_integration,solve_result,eff_capture_cost,cum_captured,ccs_2050,boiler_steam_share,lcop> "results\whr_summary.csv"

set "TEMPFILE=temp_whr_template.mod"

for %%T in (0 0.25 0.5 0.75 1) do (
    for %%M in ("integrated 1" "boiler-only 0") do (
        for /f "tokens=1-2" %%A in (%%M) do (

            set "LABEL=theta%%T_%%A"
            set "OUTFILE=results\!LABEL!.txt"

            echo.
            echo =====================================
            echo Running !LABEL!
            echo =====================================

            copy /Y whr_template.mod "!TEMPFILE!" >nul

            powershell -NoProfile -Command "(Get-Content '!TEMPFILE!') | ForEach-Object { $_ -replace 'THETAVAL','%%T' -replace 'WHRVAL','%%B' -replace 'MODELABEL','%%A' } | Set-Content '!TEMPFILE!'"

            "%AMPL_EXE%" "!TEMPFILE!" > "!OUTFILE!" 2>&1

        )
    )
)

del "%TEMPFILE%" >nul 2>&1

echo.
echo Building Excel workbook and figure...
python whr_pivot.py
python whr_plot.py

echo.
echo ============================
echo ALL RUNS FINISHED
echo Summary CSV:  results\whr_summary.csv
echo Workbook:     results\whr_summary.xlsx
echo Figure:       fig_whr_value.png
echo ============================
pause
