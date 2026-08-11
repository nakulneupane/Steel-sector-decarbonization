@echo off
setlocal EnableDelayedExpansion

set "AMPL_EXE=C:\Users\Other User\AMPL\ampl.exe"
set "WORKDIR=C:\Users\Other User\Desktop\Claude\steel-mip"
set "GRIDDIR=Plots\Grid"

cd /d "%WORKDIR%"

if not exist "%GRIDDIR%\results" mkdir "%GRIDDIR%\results"

rem fresh summary with header each launch
echo h2_start,scrap_rate,grid_ef_end,theta_grid,tariff_2050,solve_result,avg_emis,pv_avg_cost,h2_share_2050,ccs_frac_2050,scrapeaf_share_2050> "%GRIDDIR%\results\grid_summary.csv"

set "TEMPFILE=temp_grid_template.mod"

for %%H in (2030 2033 2036 2039 2042 2045) do (
    for %%S in (0.01 0.02 0.03 0.04 0.05 0.06 0.07 0.08) do (
        for %%G in (0.0000 0.00005 0.0001 0.00015 0.0002 0.00025 0.0003 0.00035 0.0004 0.00045 0.0005 0.00055 0.0006 0.00065 0.0007 0.00075 0.0008 0.00085) do (

            set "LABEL=h2%%H_scrap%%S_grid%%G"
            set "OUTFILE=%GRIDDIR%\results\!LABEL!.txt"

            echo.
            echo =====================================
            echo Running !LABEL!
            echo =====================================

            copy /Y "%GRIDDIR%\grid_template.mod" "!TEMPFILE!" >nul

            powershell -NoProfile -Command "(Get-Content '!TEMPFILE!') | ForEach-Object { $_ -replace 'H2ENDVAL','%%H' -replace 'SCRAPVAL','%%S' -replace 'GRIDVAL','%%G' } | Set-Content '!TEMPFILE!'"

            "%AMPL_EXE%" "!TEMPFILE!" > "!OUTFILE!" 2>&1

        )
    )
)

del "%TEMPFILE%" >nul 2>&1

echo.
echo Building Excel workbook (runs + offset_required sheets)...
python "%GRIDDIR%\grid_pivot.py"

echo.
echo ============================
echo ALL RUNS FINISHED
echo Summary CSV:  %GRIDDIR%\results\grid_summary.csv
echo Workbook:     %GRIDDIR%\results\grid_summary.xlsx  (sheet 2 = grid offset required)
echo ============================
pause
