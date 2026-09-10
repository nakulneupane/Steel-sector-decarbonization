#!/usr/bin/env python3
"""Fuel-availability figure: 2x2 regime panels (coking coal x NG,
abundant/scarce), stacked 2050 route shares by H2 start year + cumulative
import bill on a twin axis.

Reads data/fuel_availability.xlsx (sheet "plot_data") -- the output of
run_fuelavailability.py, not raw solver output. "X" rows = infeasible
(hatched grey bar, no import-bill point).
"""
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

plt.rcParams.update({
    "font.family": "Source Code Pro",
    "font.size": 14,
})

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "data", "fuel_availability.xlsx")

ROUTES = [
    ("BF-BOF share 2050", "BF-BOF", "#774a62"),
    ("Coal-DRI share 2050", "Coal DRI-EAF/IF", "#313e61"),
    ("NG-DRI share 2050", "NG DRI-EAF", "orange"),
    ("H2-DRI share 2050", "H$_2$ DRI-EAF", "#4daf4a"),
    ("Scrap-EAF share 2050", "Scrap-EAF", "#377eb8"),
]

PANELS = [
    ("AbCoal-AbNG", ("(a)", "Abundant coking coal, abundant NG")),
    ("AbCoal-ScNG", ("(b)", "Abundant coking coal, scarce NG")),
    ("ScCoal-AbNG", ("(c)", "Scarce coking coal, abundant NG")),
    ("ScCoal-ScNG", ("(d)", "Scarce coking coal, scarce NG")),
]

BAR_WIDTH = 0.62
BILL_COL = "Cumulative import bill 2025-50 ($B)"


def main():
    df = pd.read_excel(XLSX, sheet_name="plot_data")
    df.columns = df.columns.str.strip()
    df["feasible"] = df["BF-BOF share 2050"].astype(str).str.strip().str.upper().ne("X")
    for col, _, _ in ROUTES:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    df[BILL_COL] = pd.to_numeric(df[BILL_COL], errors="coerce")

    fig, axes = plt.subplots(2, 2, figsize=(10.2, 7), sharey=True)
    fig.subplots_adjust(left=0, right=1, top=0.97, bottom=0.14,
                        wspace=0.06, hspace=0.25)

    for idx, (ax, (regime, (panel, subtitle))) in enumerate(zip(axes.ravel(), PANELS)):
        data = df[df["Regime"] == regime].sort_values("H2 start year").reset_index(drop=True)
        x = range(len(data))
        bottom = [0] * len(data)

        for col, label, color in ROUTES:
            values = data[col].where(data["feasible"], 0)
            ax.bar(x, values, width=BAR_WIDTH, bottom=bottom, color=color)
            bottom = [b + v for b, v in zip(bottom, values)]

        for i, ok in enumerate(data["feasible"]):
            if not ok:
                ax.bar(i, 1, width=BAR_WIDTH, color="0.93", edgecolor="0.7",
                       hatch="//", linewidth=0.6)
                ax.text(i, 0.5, "Infeasible", ha="center", va="center", rotation=90,
                        fontsize=14, fontweight="bold", color="0.4")

        ax.set_xlim(-BAR_WIDTH / 2, len(data) - 1 + BAR_WIDTH / 2)
        ax.set_xticks(list(x))
        ax.set_xticklabels(data["H2 start year"], fontsize=14)

        if idx < 2:
            ax.set_xticklabels([])
            ax.set_xlabel("")
            ax.tick_params(axis="x", labelbottom=False, bottom=False)
        else:
            ax.tick_params(axis="x", bottom=False)

        ax.set_ylim(0, 1)
        ax.grid(axis="y", alpha=0)

        ax.text(0.00, 1.05, panel, transform=ax.transAxes,
                va="bottom", ha="left", fontsize=14, fontweight="bold")
        ax.text(0.10, 1.05, subtitle, transform=ax.transAxes,
                va="bottom", ha="left", fontsize=14, fontweight="bold")

        ax2 = ax.twinx()
        bill = data[BILL_COL].where(data["feasible"], np.nan)
        ax2.plot(x, bill, color="black", marker="s", linestyle="--",
                 linewidth=1.5, markersize=6)
        ax2.set_ylim(0, 800)
        ax2.tick_params(axis="y", labelsize=14, colors="black")
        ax2.spines["right"].set_visible(True)
        ax2.spines["right"].set_color("black")
        ax2.yaxis.label.set_color("black")

        if idx in [1, 3]:
            ax2.set_ylabel("Import Bill ($B)", fontsize=14, color="black")
        else:
            ax2.set_ylabel("")
            ax2.tick_params(axis="y", labelleft=False, labelright=False)

    for ax in axes[:, 0]:
        ax.set_ylabel("2050 Route Share", fontsize=14)
    for ax in axes[1]:
        ax.set_xlabel("H$_2$ Start Year", fontsize=14)

    handles = [Patch(color=color, label=label) for _, label, color in ROUTES]
    fig.legend(handles=handles, ncol=5, loc="lower center",
               bbox_to_anchor=(0.5, 0.001), frameon=False, fontsize=14)

    out = os.path.join(HERE, "fig_fuelavailability.png")
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    print("written:", out)

    out_pdf = os.path.join(HERE, "fig_fuelavailability.pdf")
    fig.savefig(out_pdf, format="pdf", dpi=600, bbox_inches="tight", facecolor="white")
    print("written:", out_pdf)


if __name__ == "__main__":
    main()
