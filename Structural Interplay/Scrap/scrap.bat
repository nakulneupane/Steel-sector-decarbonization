@echo off
setlocal EnableDelayedExpansion

set "AMPL_EXE=C:\Users\Other User\AMPL\ampl.exe"
set "WORKDIR=C:\Users\Other User\Desktop\Claude\steel-mip\Plots\Scrap"

cd /d "%WORKDIR%"

if not exist results mkdir results

echo avg_emi,scrap_rate,solve_result,h2dri_cap_2050,ccs_2050,red_h2_2050,lcop,scrap_use_2050,scrap_limit_2050,scrapeaf_share_2050> "results\scrap_summary.csv"

set "TEMPFILE=temp_scrap_template.mod"

for %%E in (1.6 1.8 2.0) do (
    for %%S in (0.00 0.01 0.02 0.03 0.04 0.05 0.06 0.07 0.08 0.09 0.10) do (

        set "LABEL=ef%%E_scrap%%S"
        set "OUTFILE=results\!LABEL!.txt"

        echo.
        echo =====================================
        echo Running !LABEL!
        echo =====================================

        copy /Y scrap_template.mod "!TEMPFILE!" >nul

        powershell -NoProfile -Command "(Get-Content '!TEMPFILE!') | ForEach-Object { $_ -replace 'SCRAPVAL','%%S' -replace 'EFVAL','%%E' } | Set-Content '!TEMPFILE!'"

        "%AMPL_EXE%" "!TEMPFILE!" > "!OUTFILE!" 2>&1

    )
)

del "%TEMPFILE%" >nul 2>&1

echo.
echo Building Excel workbook...
python scrap_pivot.py

echo.
echo ============================
echo ALL RUNS FINISHED
echo Summary CSV:  results\scrap_summary.csv
echo Workbook:     results\scrap_summary.xlsx
echo ============================
pause
