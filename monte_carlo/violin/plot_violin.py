#!/usr/bin/env python3
"""Split composition-violins: one asymmetric violin per (scrap group x H2
start year): LEFT half = LCOP (whole-path PV, USD/t) distribution, filled
with the stacked mean 2050 production mix per cost bin; RIGHT half = 2050
emission-intensity (tCO2/t) distribution, plain fill; circle at the
median = mean CCS capture fraction (cumulative captured / cumulative
gross emitted). P(infeasible) of each cell is printed under its violin.

Rows: 3 exact scrap_rate bands from our 5-level discrete axis --
Low = {0.02, 0.04}, Mid = {0.06}, High = {0.08, 0.10}. avg_emi = 1.8,
ramp = medium fixed throughout.

Fully self-contained: reads data/violin.xlsx in this same folder (sheets
"cells"/"lcop_bins"/"emis_bins") -- see run_violin.py.

    python plot_violin.py
"""
import pathlib

import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

plt.rcParams.update({
    "font.family": "Source Code Pro",
    "font.size": 14,
    "axes.labelsize": 14,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
})

HERE = pathlib.Path(__file__).resolve().parent
XLSX = HERE / "data" / "violin.xlsx"

H2_YEARS = [2030, 2035, 2040, 2045]
PAL = plt.colormaps["Pastel2"].colors
ROUTE_COLS = [
    ("Scrap-EAF", PAL[0]), ("H2-DRI", PAL[1]), ("NG-DRI", PAL[2]),
    ("Coal-DRI", "#5c5c5c"), ("BF-BOF", PAL[4]),
]
EDGE = dict(edgecolor="black", linewidth=0.8)
RMAX = 16.0


def draw_bins(ax, xpos, bins, lo_col, hi_col, side, shares=None, halfw=0.40):
    if len(bins) == 0:
        return
    scale = halfw / bins["count"].max()
    for _, row in bins.iterrows():
        width = row["count"] * scale
        y = row[lo_col]
        h = row[hi_col] - row[lo_col]
        x0 = xpos - width if side == "L" else xpos
        if shares:
            vals = [max(row[c], 0) for c, _ in shares]
            total = sum(vals) or 1
            for (c, color), value in zip(shares, vals):
                w = width * value / total
                ax.add_patch(Rectangle((x0, y), w, h, facecolor=color, **EDGE))
                x0 += w
        else:
            ax.add_patch(Rectangle((x0, y), width, h, facecolor="#a7c0fb", **EDGE))


def main():
    cells = pd.read_excel(XLSX, sheet_name="cells")
    lcop_bins = pd.read_excel(XLSX, sheet_name="lcop_bins")
    emis_bins = pd.read_excel(XLSX, sheet_name="emis_bins")

    groups = cells[["scrap_group", "grange"]].drop_duplicates().values
    cost_min, cost_max = lcop_bins.lcop_bin_lo.min(), lcop_bins.lcop_bin_hi.max()
    cap_max = cells.capture_frac.max()

    fig, axes = plt.subplots(3, 1, figsize=(14.5, 12))
    fig.subplots_adjust(left=0.08, right=0.92, top=0.965, bottom=0.05, hspace=0.12)

    for tag, axL, (group, grange) in zip("abc", axes, groups):
        axR = axL.twinx()
        xs, ys, ss = [], [], []

        for xpos, year in enumerate(H2_YEARS, start=1):
            axL.axvline(xpos, color="0.75", lw=0.6, zorder=0)
            cell = cells[(cells.scrap_group == group) & (cells.h2_year == year)]
            p = float(cell.P_infeasible.iloc[0])
            axL.text(xpos, cost_min - 25, f"{(1 - p):.0%}", ha="center", va="center",
                     fontsize=12, color="0.25", fontweight="bold")

            cb = lcop_bins[(lcop_bins.scrap_group == group) & (lcop_bins.h2_year == year)]
            if len(cb) == 0:
                axL.text(xpos, (cost_min + cost_max) / 2, "INFEASIBLE", rotation=90,
                         ha="center", va="center", color="#c0392b", fontweight="bold",
                         fontsize=14)
                continue

            draw_bins(axL, xpos, cb, "lcop_bin_lo", "lcop_bin_hi", "L", shares=ROUTE_COLS)
            eb = emis_bins[(emis_bins.scrap_group == group) & (emis_bins.h2_year == year)]
            draw_bins(axR, xpos, eb, "emis_bin_lo", "emis_bin_hi", "R")

            xs.append(xpos - 0.45)
            ys.append(float(cell.lcop_p50.iloc[0]))
            capfrac = float(cell.capture_frac.iloc[0])
            ss.append((capfrac / cap_max * RMAX) ** 2)

        axL.scatter(xs, ys, s=ss, facecolor="#1f78b4", edgecolor="black",
                    linewidth=0.8, alpha=0.9, zorder=5)
        axL.set_xlim(0.35, len(H2_YEARS) + 0.65)
        axL.set_ylim(cost_min - 40, cost_max + 20)
        axR.set_ylim(0.4, 1.8)

        axL.set_xticks(range(1, len(H2_YEARS) + 1))
        if tag == "c":
            axL.set_xticklabels([f"H$_2$ {y}" for y in H2_YEARS])
            axL.set_xlabel("H2 Start Year")
        else:
            axL.set_xticklabels([])

        axL.set_ylabel("LCOP (2025-2050) [USD/t]")
        axL.text(0.45, cost_min - 25, "Feasibility", ha="left", va="center",
                 fontsize=12, color="0.25", fontweight="bold")
        axR.set_ylabel(r"EF 2050 [tCO$_2$/t]")
        axL.grid(axis="y", alpha=0.1)
        for spine in list(axL.spines.values()) + list(axR.spines.values()):
            spine.set_linewidth(1.2)
        axL.set_title(f"({tag}) {group} scrap ({grange})", loc="left",
                      fontweight="bold")

    handles = [Patch(facecolor=c, label=l, **EDGE) for l, c in ROUTE_COLS]
    handles += [Line2D([0], [0], marker="o", ls="", markerfacecolor="#1f78b4",
                       markeredgecolor="black", markersize=f / cap_max * RMAX,
                       label=f"CCS: {100*f:.0f}%") for f in (0.05, 0.10, 0.20)]
    fig.legend(handles=handles, ncol=8, loc="lower center", frameon=True,
               framealpha=0.95, edgecolor="black", fancybox=False, fontsize=12,
               bbox_to_anchor=(0.5, -0.05))

    out = HERE / "fig_violin.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"written: {out}")

    out_pdf = HERE / "fig_violin.pdf"
    fig.savefig(out_pdf, format="pdf", dpi=600, bbox_inches="tight", facecolor="white")
    print(f"written: {out_pdf}")


if __name__ == "__main__":
    main()
