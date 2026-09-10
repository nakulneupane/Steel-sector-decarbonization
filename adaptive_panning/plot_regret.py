#!/usr/bin/env python3
"""Regret figure: (a) regret-decay lines by arrival cohort, x-axis =
recourse YEAR (0=None, 1=2030, 2=2035, 3=2040, 4=2045) instead of
recourse count; (b) staggered stranded-capex bars by asset class,
per-cohort recourse cutoff fixed to where that cohort's regret has
already plateaued (a cohort whose worlds are all resolved by a given
checkpoint has nothing new to show at later checkpoints -- see
run_regret.py's docstring on the 2030-34 cohort as the clearest case).

Reads data/regret_ladder.csv (this folder) -- see run_regret.py.

    python plot_regret.py
"""
import pathlib

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

plt.rcParams.update({
    "font.family": "Source Code Pro", "font.size": 16,
    "axes.labelsize": 16, "xtick.labelsize": 16, "ytick.labelsize": 16,
})
LABEL_SIZE = 16

HERE = pathlib.Path(__file__).resolve().parent
CSV = HERE / "data" / "regret_ladder.csv"

STAGES = {"norec": 0, "settle_n1": 1, "settle_n2": 2, "settle_n3": 3, "settle_n4": 4}
BINS = [(2030, 2034, "2030-34"), (2035, 2039, "2035-39"),
       (2040, 2044, "2040-44"), (2045, 2049, "2045-49")]
BIN_N_LEVELS = {"2030-34": [0, 1], "2035-39": [0, 1, 2],
                "2040-44": [0, 1, 2, 3], "2045-49": [0, 1, 2, 3, 4]}
BIN_COLOR = {"2030-34": "#4daf4a", "2035-39": "#377eb8",
             "2040-44": "#e67e22", "2045-49": "#313e61"}
BIN_MARKER = {"2030-34": "o", "2035-39": "s", "2040-44": "^", "2045-49": "D"}
RECOURSE_YEAR = {0: "None", 1: "2030", 2: "2035", 3: "2040", 4: "2045"}
STR_CLASSES = [("str_conv_B", "Conventional routes", "#313e61"),
               ("str_h2dri_B", "H2-DRI plants", "#4daf4a"),
               ("str_h2supply_B", "H2 supply (elz+RE)", "#a6d96a"),
               ("str_ccs_B", "CCS", "#c0392b"),
               ("str_scrapchain_B", "Scrap chain", "#6e8b3d"),
               ("str_othchain_B", "Other", "#e67e22")]


def bin_of(R):
    for lo, hi, label in BINS:
        if lo <= R <= hi:
            return label
    return None


def load():
    d = pd.read_csv(CSV)
    d = d[d.status == "solved"].copy()
    pf = d[d.kind == "pf"].set_index("wid")
    ev = d[d.kind.isin(STAGES)].copy()
    ev["n_reviews"] = ev.kind.map(STAGES)
    ev["realized"] = ev.realized.astype(int)
    ev["bin"] = ev.realized.apply(bin_of)
    ev["regret"] = ev.lcop_pv - pf.lcop_pv.reindex(ev.wid).values
    return ev


def panel_a(ax, ev):
    for lo, hi, label in BINS:
        levels = BIN_N_LEVELS[label]
        means = [ev[(ev.bin == label) & (ev.n_reviews == n)].regret.mean()
                for n in levels]
        ax.plot(levels, means, "-", marker=BIN_MARKER[label],
               color=BIN_COLOR[label], lw=3.2, ms=10, mew=0,
               label=label)
    ax.set_xticks(range(5))
    ax.set_xticklabels([RECOURSE_YEAR[n] for n in range(5)])
    ax.set_xlabel("Recourse year")
    ax.set_ylabel("Mean regret (USD/t)")
    ax.grid(alpha=0.15)
    ax.legend(frameon=True, edgecolor="black", framealpha=0.95, fontsize=16,
              title="Arrival", title_fontsize=16)
    ax.set_title("(a) Drivers of regret", loc="left", fontweight="bold", fontsize=16)


def panel_b(ax, ev):
    bin_labels = [b[2] for b in BINS]
    bar_h = 0.8
    GAP = 1.5
    y_of, group_centers = {}, []
    y0 = 0.0
    for label in bin_labels:
        levels = BIN_N_LEVELS[label]
        for k, n in enumerate(levels):
            y_of[(label, n)] = y0 + k
        group_centers.append(y0 + (len(levels) - 1) / 2)
        y0 += len(levels) + GAP

    max_right = 0.0
    for gi, label in enumerate(bin_labels):
        for n in BIN_N_LEVELS[label]:
            sub = ev[(ev.n_reviews == n) & (ev.bin == label)]
            y = y_of[(label, n)]
            left = 0.0
            for col, clabel, color in STR_CLASSES:
                v = pd.to_numeric(sub[col], errors="coerce").mean()
                v = 0.0 if np.isnan(v) else v
                ax.barh(y, v, height=bar_h, left=left, color=color,
                       edgecolor="white", linewidth=0.3,
                       label=clabel if (gi == 0 and n == 0) else None, zorder=2)
                left += v
            ax.text(left + 1.5, y, str(n), ha="left", va="center",
                   fontsize=LABEL_SIZE, zorder=3)
            max_right = max(max_right, left)

    ax.set_xlim(0, max_right * 1.1)
    ax.set_yticks(group_centers)
    ax.set_yticklabels(bin_labels, rotation=90, va="center", ha="center")
    ax.invert_yaxis()
    ax.set_ylabel(r"H$_2$ arrival year", labelpad=12)
    ax.set_xlabel("Expected stranded capex (billion USD)")
    ax.grid(alpha=0.18, axis="x")
    ax.set_axisbelow(True)
    ax.tick_params(axis="y", length=0, pad=14)
    ax.legend(frameon=True, edgecolor="black", framealpha=1, loc="upper right",
             bbox_to_anchor=(0.98, 1.0), fontsize=16)
    ax.set_title("(b) Stranded assets", loc="left", fontweight="bold", fontsize=16)


def main():
    ev = load()
    fig, (ax_a, ax_b) = plt.subplots(1, 2, figsize=(16, 8.2),
                                     gridspec_kw={"width_ratios": [0.85, 1]})
    panel_a(ax_a, ev)
    panel_b(ax_b, ev)
    for ax in (ax_a, ax_b):
        for spine in ax.spines.values():
            spine.set_visible(True); spine.set_color("black"); spine.set_linewidth(1.0)

    fig.tight_layout()
    out = HERE / "fig_regret.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"written: {out}")
    out_pdf = HERE / "fig_regret.pdf"
    fig.savefig(out_pdf, format="pdf", dpi=600, bbox_inches="tight", facecolor="white")
    print(f"written: {out_pdf}")


if __name__ == "__main__":
    main()
