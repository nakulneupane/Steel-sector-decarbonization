#!/usr/bin/env python3
"""H2-delay heatmaps: EF x H2-supply rows, H2 start year columns.
Panel (a) H2-DRI 2050 route share (%), panel (b) LCOP ($/t).

Reads data/h2_delay.xlsx (sheet "plot_data") -- the output of
run_h2delay.py, not raw solver output. "X" cells = infeasible.
"""
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

plt.rcParams.update({
    "font.family": "Source Code Pro",
    "font.size": 16,
    "axes.labelsize": 16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
})

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "data", "h2_delay.xlsx")

EFS = [1.6, 1.8, 2.0]
SUPPLY = ["Low", "Mid", "High"]
YEARS = [2030, 2035, 2040, 2045]

CMAP_A = LinearSegmentedColormap.from_list(
    "blue_seq", ["#eaf1fb", "#8fb8dd", "#3c6ea5", "#152f52"])
CMAP_B = LinearSegmentedColormap.from_list(
    "orange_purple", ["#fdf1d9", "#f2a153", "#c65f6f", "#3c1a4a"])


def load_grids():
    df = pd.read_excel(XLSX, sheet_name="plot_data")
    df = df.replace("X", np.nan)
    for c in ["H2-DRI share 2050 (%)", "LCOP ($/t)"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    SHARE = np.full((9, 4), np.nan)
    LCOP = np.full((9, 4), np.nan)
    for i, (ef, sup) in enumerate((e, s) for e in EFS for s in SUPPLY):
        for j, yr in enumerate(YEARS):
            s = df[(df["EF"] == ef) & (df["H2 supply"] == sup)
                   & (df["H2 start year"] == yr)]
            if len(s):
                SHARE[i, j] = s["H2-DRI share 2050 (%)"].iloc[0]
                LCOP[i, j] = s["LCOP ($/t)"].iloc[0]
    return SHARE, LCOP


def main():
    SHARE, LCOP = load_grids()
    mask = np.isnan(SHARE)
    s_lo, s_hi = np.nanmin(SHARE), np.nanmax(SHARE)
    l_lo, l_hi = np.nanmin(LCOP), np.nanmax(LCOP)

    fig = plt.figure(figsize=(14, 7))
    gs = fig.add_gridspec(2, 3, width_ratios=[0.3, 1, 1], height_ratios=[1.6, 9],
                          wspace=0.03, hspace=0)

    ax_head = fig.add_subplot(gs[0, 0])
    ax_tbl = fig.add_subplot(gs[1, 0])
    fig.add_subplot(gs[0, 1]).axis("off")
    fig.add_subplot(gs[0, 2]).axis("off")
    ax1 = fig.add_subplot(gs[1, 1])
    ax2 = fig.add_subplot(gs[1, 2])

    ax_head.set_xlim(0, 2)
    ax_head.set_ylim(1, 0)
    ax_head.axis("off")
    ax_tbl.set_xlim(0, 2)
    ax_tbl.set_ylim(9, 0)
    ax_tbl.axis("off")

    for x in [0, 1, 2]:
        ax_head.plot([x, x], [0, 1], color="black", lw=1.4)
        ax_tbl.plot([x, x], [0, 9], color="black", lw=1.4)
    ax_head.plot([0, 2], [0, 0], color="black", lw=1.4)
    ax_head.plot([0, 2], [1, 1], color="black", lw=1.4)
    ax_tbl.plot([0, 2], [0, 0], color="black", lw=1.4)
    for y in [3, 6, 9]:
        ax_tbl.plot([0, 2], [y, y], color="black", lw=1.4)
    for y in [1, 2, 4, 5, 7, 8]:
        ax_tbl.plot([1, 2], [y, y], color="black", lw=1.0)

    ax_head.text(0.5, 0.5, "EF", ha="center", va="center", fontsize=16, fontweight="bold")
    ax_head.text(1.5, 0.5, "H$_2$\nsupply", ha="center", va="center",
                 fontsize=16, fontweight="bold")
    for y, v in zip([1.5, 4.5, 7.5], ["1.6", "1.8", "2.0"]):
        ax_tbl.text(0.5, y, v, ha="center", va="center", fontsize=16, fontweight="bold")
    for i, r in enumerate(SUPPLY * 3):
        ax_tbl.text(1.5, i + 0.5, r, ha="center", va="center", fontsize=16)

    ax_head.add_patch(Rectangle((0, 0), 2, 1, facecolor="#d9e6f2", edgecolor="none", zorder=0))
    for k in range(3):
        ax_tbl.add_patch(Rectangle((0, 3 * k), 1, 3, facecolor="#fdf2e6", edgecolor="none", zorder=0))
    for i in range(9):
        ax_tbl.add_patch(Rectangle((1, i), 1, 1, facecolor="#ececec", edgecolor="none", zorder=0))

    sns.heatmap(SHARE, ax=ax1, cmap=CMAP_A, vmin=s_lo, vmax=s_hi,
                linewidths=0, mask=mask, annot=True, fmt=".0f",
                annot_kws=dict(fontsize=16, fontweight="bold"), cbar=False)
    sns.heatmap(LCOP, ax=ax2, cmap=CMAP_B, vmin=l_lo, vmax=l_hi,
                linewidths=0, mask=mask, annot=True, fmt=".0f",
                annot_kws=dict(fontsize=16, fontweight="bold"), cbar=False)

    cax1 = inset_axes(ax1, width="80%", height="6.5%", loc="upper left",
                      bbox_to_anchor=(0.18, 0.165, 1, 1),
                      bbox_transform=ax1.transAxes, borderpad=0)
    cb1 = plt.colorbar(ax1.collections[0], cax=cax1, orientation="horizontal")
    cb1.ax.tick_params(labelsize=16, pad=2)
    cb1.ax.text(0.5, 0.5, "H$_2$-DRI Share 2050 (%)", ha="center", va="center",
                color="white", fontsize=16, fontweight="bold", transform=cb1.ax.transAxes)

    cax2 = inset_axes(ax2, width="80%", height="6.5%", loc="upper left",
                      bbox_to_anchor=(0.18, 0.165, 1, 1),
                      bbox_transform=ax2.transAxes, borderpad=0)
    cb2 = plt.colorbar(ax2.collections[0], cax=cax2, orientation="horizontal")
    cb2.ax.tick_params(labelsize=16, pad=2)
    cb2.ax.text(0.5, 0.5, "LCOP ($/t)", ha="center", va="center",
                color="white", fontsize=16, fontweight="bold", transform=cb2.ax.transAxes)

    for cb in (cb1, cb2):
        if cb.solids is not None:
            cb.solids.set_rasterized(False)
            cb.solids.set_edgecolor("face")

    for ax in [ax1, ax2]:
        ax.set_xticklabels(YEARS, rotation=0)
        ax.set_xlabel("Hydrogen start year")
        ax.set_yticks([])
        ax.set_ylabel("")
        for y in [3, 6]:
            ax.hlines(y, *ax.get_xlim(), colors="white", linewidth=0.5)

    s_thr = (s_lo + s_hi) / 2
    for t in ax1.texts:
        try:
            t.set_color("white" if float(t.get_text()) > s_thr else "black")
        except ValueError:
            pass
    l_thr = np.nanmean(LCOP)
    for t in ax2.texts:
        try:
            t.set_color("white" if float(t.get_text()) > l_thr else "black")
        except ValueError:
            pass

    for i in range(mask.shape[0]):
        for j in range(mask.shape[1]):
            if mask[i, j]:
                for ax in [ax1, ax2]:
                    ax.text(j + 0.5, i + 0.5, "X", ha="center", va="center",
                            fontsize=16, color="dimgray", fontweight="bold")

    ax1.set_title("(a)", fontsize=16, fontweight="bold", x=0.03, y=1.09)
    ax2.set_title("(b)", fontsize=16, fontweight="bold", x=0.03, y=1.09)

    plt.subplots_adjust(left=0.05, right=0.98, top=0.92, bottom=0.12, wspace=0.03, hspace=0)

    out = os.path.join(HERE, "fig_h2delay.png")
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    print("written:", out)

    out_pdf = os.path.join(HERE, "fig_h2delay.pdf")
    fig.savefig(out_pdf, format="pdf", dpi=600, bbox_inches="tight", facecolor="white")
    print("written:", out_pdf)
    print(f"anchors: H2-DRI share [{s_lo:.0f}, {s_hi:.0f}]%  LCOP [{l_lo:.0f}, {l_hi:.0f}]")


if __name__ == "__main__":
    main()
