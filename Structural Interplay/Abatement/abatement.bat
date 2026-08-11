@echo off
setlocal EnableDelayedExpansion

set "AMPL_EXE=C:\Users\Other User\AMPL\ampl.exe"
set "WORKDIR=C:\Users\Other User\Desktop\Claude\steel-mip\Plots\Abatement"

cd /d "%WORKDIR%"

if not exist results mkdir results

echo run,year,solve_result,total_steel,steel_bof,coaldri,ngdri,h2dri,scrap_eaf,scope1,scope2,ccs,total_emissions,e_h2,bof_scrap,cdri_scrap,ngdri_scrap,h2dri_scrap,scrapeaf_scrap,scrap_limit,total_cost,whr_power,gross_bf,gross_cdri,gross_ngdri,gross_scrapeaf> "results\abatement_yearly.csv"

echo Running Baseline...
"%AMPL_EXE%" abatement_baseline.mod > "results\Baseline.txt" 2>&1

set "TEMPFILE=temp_abatement.mod"

for %%S in ("EF1.6 1.6 0.06 15000000 6000000"
            "EF1.8 1.8 0.06 15000000 6000000"
            "S4    1.8 0.04 15000000 6000000"
            "S8    1.8 0.08 15000000 6000000"
            "RL    1.8 0.06 10000000 4000000"
            "RH    1.8 0.06 20000000 8000000") do (
    for /f "tokens=1-5" %%A in (%%S) do (

        echo Running %%A...
        copy /Y abatement_scenario.mod "!TEMPFILE!" >nul
        powershell -NoProfile -Command "(Get-Content '!TEMPFILE!') | ForEach-Object { $_ -replace 'SCENLABEL','%%A' -replace 'H2REFVAL','%%E' -replace 'EFVAL','%%B' -replace 'SCRAPVAL','%%C' -replace 'RAMPVAL','%%D' } | Set-Content '!TEMPFILE!'"
        "%AMPL_EXE%" "!TEMPFILE!" > "results\%%A.txt" 2>&1

    )
)

del "%TEMPFILE%" >nul 2>&1

echo.
echo Building Excel workbook and figure...
python abatement_pivot.py
python abatement_plot.py

echo.
echo ============================
echo DONE
echo Yearly CSV:  results\abatement_yearly.csv
echo Workbook:    results\abatement_summary.xlsx
echo Figure:      fig_abatement_bars.png
echo ============================
pause


